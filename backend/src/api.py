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
