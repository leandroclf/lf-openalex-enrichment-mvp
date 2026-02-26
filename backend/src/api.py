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
