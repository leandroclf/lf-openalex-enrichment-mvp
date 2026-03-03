"""Core service bootstrap for lf-openalex-enrichment-mvp."""

import os
import time


def healthcheck():
    return {"status": "ok", "component": "lf-openalex-enrichment-mvp"}


def roadmap_items():
    return [
        "ingest",
        "normalize",
        "publish-metrics"
    ]


def _to_positive_float(raw_value, default_value):
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return float(default_value)
    return value if value > 0 else float(default_value)


def _to_non_negative_int(raw_value, default_value):
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return int(default_value)
    return value if value >= 0 else int(default_value)


def load_openalex_runtime_config():
    """Load OpenAlex runtime knobs from env with safe defaults."""
    return {
        "timeout_seconds": _to_positive_float(os.getenv("OPENALEX_TIMEOUT"), 12.0),
        "max_retries": _to_non_negative_int(os.getenv("OPENALEX_MAX_RETRIES"), 2),
        "backoff_seconds": _to_positive_float(os.getenv("OPENALEX_RETRY_BACKOFF_SECONDS"), 0.5),
    }


def run_openalex_with_retry(
    request_fn,
    timeout_seconds=None,
    max_retries=None,
    backoff_seconds=None,
    sleep_fn=None,
):
    """
    Execute an OpenAlex request with retry/backoff policy.

    `max_retries` means extra attempts after the first call.
    """
    cfg = load_openalex_runtime_config()
    timeout = timeout_seconds if timeout_seconds is not None else cfg["timeout_seconds"]
    retries = max_retries if max_retries is not None else cfg["max_retries"]
    backoff = backoff_seconds if backoff_seconds is not None else cfg["backoff_seconds"]
    sleeper = sleep_fn or time.sleep
    transient_errors = (TimeoutError, ConnectionError)

    for attempt in range(retries + 1):
        try:
            return request_fn(timeout=timeout)
        except TypeError:
            # Compatibility for callables without `timeout` parameter.
            return request_fn()
        except transient_errors:
            if attempt >= retries:
                raise
            sleeper(backoff * (attempt + 1))
