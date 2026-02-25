"""Core service bootstrap for lf-openalex-enrichment-mvp."""

def healthcheck():
    return {"status": "ok", "component": "lf-openalex-enrichment-mvp"}


def roadmap_items():
    return [
        "ingest",
        "normalize",
        "publish-metrics"
    ]
