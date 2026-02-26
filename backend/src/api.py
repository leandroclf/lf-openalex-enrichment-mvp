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
