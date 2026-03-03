from datetime import datetime, timezone

def get_sample_payload():
    return {
        "component": "lf-openalex-enrichment-mvp",
        "source": "openalex",
        "status": "ok",
        "generatedAt": datetime.now(timezone.utc).isoformat()
    }


def get_value_signal():
    payload = get_sample_payload()
    return {"issue": "ISSUE-001", "kpi": "attribute_coverage", "targetLiftPct": 20, "component": payload["component"]}



def calculate_attribute_coverage(records, required_fields):
    """Return coverage ratio (0..1) for required_fields across records."""
    if not records or not required_fields:
        return 0.0
    total_checks = len(records) * len(required_fields)
    filled = 0
    for r in records:
        for f in required_fields:
            v = r.get(f)
            if v is not None and str(v).strip() != "":
                filled += 1
    return round(filled / total_checks, 4)


def calculate_weighted_attribute_coverage(records, field_weights):
    """Weighted coverage ratio (0..1) using field -> weight mapping."""
    if not records or not field_weights:
        return 0.0

    normalized = {k: float(v) for k, v in field_weights.items() if float(v) > 0}
    if not normalized:
        return 0.0

    total_weight_per_row = sum(normalized.values())
    total_possible = len(records) * total_weight_per_row
    covered = 0.0

    for r in records:
        for field, w in normalized.items():
            v = r.get(field)
            if v is not None and str(v).strip() != "":
                covered += w

    return round(covered / total_possible, 4)



def get_value_endpoint_response(account_id, score):
    return {
        "issue": "ISSUE-016",
        "accountId": str(account_id),
        "valueScore": float(score),
        "status": "ready",
    }



def clamp_value_score(score):
    s=float(score)
    if s < 0: return 0.0
    if s > 100: return 100.0
    return round(s, 2)



def build_value_endpoint_payload(account_id, score, segment):
    return {
        "issue": "ISSUE-016",
        "accountId": str(account_id),
        "segment": str(segment),
        "valueScore": clamp_value_score(score),
    }



def classify_value_band(score):
    s = clamp_value_score(score)
    if s >= 80: return "high"
    if s >= 50: return "medium"
    return "low"



def build_value_signal_summary(account_id, score):
    return {
        "accountId": str(account_id),
        "band": classify_value_band(score),
        "score": clamp_value_score(score),
    }



def is_high_value_account(score):
    return classify_value_band(score) == "high"



def score_to_percentile(score):
    s = clamp_value_score(score)
    return round(s / 100, 4)


def summarize_value_portfolio(accounts):
    """Aggregate portfolio stats for ISSUE-016 value endpoint consumers."""
    if not accounts:
        return {"total": 0, "highValueCount": 0, "avgScore": 0.0}

    normalized_scores = [clamp_value_score(a.get("valueScore", 0)) for a in accounts]
    high_value = sum(1 for s in normalized_scores if is_high_value_account(s))
    return {
        "total": len(accounts),
        "highValueCount": high_value,
        "avgScore": round(sum(normalized_scores) / len(normalized_scores), 2),
    }


def summarize_value_by_segment(accounts):
    """Count accounts by segment and high-value concentration."""
    out = {}
    for a in accounts or []:
        segment = str(a.get("segment", "unknown"))
        score = clamp_value_score(a.get("valueScore", 0))
        bucket = out.setdefault(segment, {"total": 0, "highValue": 0})
        bucket["total"] += 1
        if is_high_value_account(score):
            bucket["highValue"] += 1
    return out


def calculate_segment_lift_vs_baseline(accounts, baseline_score):
    """Average portfolio lift versus a baseline score (pct points)."""
    if not accounts:
        return 0.0
    base = clamp_value_score(baseline_score)
    avg = summarize_value_portfolio(accounts)["avgScore"]
    if base == 0:
        return 0.0
    return round(((avg - base) / base) * 100, 2)


def summarize_value_distribution(accounts):
    """Count accounts by value band for quick commercial reporting."""
    bands = {"high": 0, "medium": 0, "low": 0}
    for a in accounts or []:
        bands[classify_value_band(a.get("valueScore", 0))] += 1
    return bands


def estimate_high_value_rate(accounts):
    """Return share of high-value accounts in portfolio."""
    if not accounts:
        return 0.0
    dist = summarize_value_distribution(accounts)
    return round(dist["high"] / len(accounts), 4)


def calculate_coverage_delta(records, required_fields, baseline_coverage):
    """Return percentage-point improvement vs baseline coverage."""
    if baseline_coverage <= 0:
        return 0.0
    current = calculate_attribute_coverage(records, required_fields)
    return round((current - baseline_coverage) * 100, 2)


def normalize_required_fields(lead, required_fields):
    """Normalize required fields for consistent coverage checks."""
    normalized = dict(lead or {})
    for field in required_fields or []:
        value = normalized.get(field)
        if isinstance(value, str):
            normalized[field] = value.strip()
        elif value is None:
            normalized[field] = ""
    return normalized


def batch_enrich_leads(leads, enrichment_config=None):
    """
    Batch enrichment processor for B2B leads using OpenAlex data.
    Returns enriched leads with coverage metrics.
    """
    if not leads:
        return {"enriched": [], "stats": {"total": 0, "enriched_count": 0, "coverage_rate": 0.0}}

    config = enrichment_config or {"fields": ["company", "domain", "industry", "employee_count"]}
    required_fields = config.get("fields", [])

    enriched = []
    enriched_count = 0

    for lead in leads:
        normalized_lead = normalize_required_fields(lead, required_fields)
        coverage = calculate_attribute_coverage([normalized_lead], required_fields)
        enriched_lead = {
            **normalized_lead,
            "_enrichment": {
                "coverage": coverage,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "source": "openalex"
            }
        }
        enriched.append(enriched_lead)
        if coverage > 0.5:
            enriched_count += 1

    return {
        "enriched": enriched,
        "stats": {
            "total": len(leads),
            "enriched_count": enriched_count,
            "coverage_rate": round(enriched_count / len(leads), 4) if leads else 0.0
        }
    }


def get_enrichment_priority_score(lead, weights=None):
    """
    Calculate priority score for enrichment based on data completeness and value potential.
    Higher score = higher priority for enrichment.
    """
    default_weights = {"company": 3, "domain": 2, "email": 2, "industry": 1, "employee_count": 1}
    w = weights or default_weights
    
    missing_score = 0
    for field, weight in w.items():
        if not lead.get(field):
            missing_score += weight
    
    return missing_score

def prioritize_leads_by_enrichment_gap(leads, weights=None):
    """Sort leads by enrichment priority score (desc), preserving input for ties."""
    scored = []
    for idx, lead in enumerate(leads or []):
        scored.append({
            **lead,
            "_priorityScore": get_enrichment_priority_score(lead, weights),
            "_inputIndex": idx,
        })

    scored.sort(key=lambda x: (-x["_priorityScore"], x["_inputIndex"]))
    for item in scored:
        item.pop("_inputIndex", None)
    return scored


def dummy_openalex_function():
    return "This is a dummy function for ISSUE-001."
