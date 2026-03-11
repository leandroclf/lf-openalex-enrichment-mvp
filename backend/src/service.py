"""Core service bootstrap for lf-openalex-enrichment-mvp."""

import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen


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
        "base_url": os.getenv(
            "OPENALEX_BASE_URL",
            "https://api.openalex.org/institutions",
        ),
        "mailto": os.getenv("OPENALEX_MAILTO", "").strip(),
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


def _select_openalex_search_term(lead):
    for field in ("company", "institution", "name", "domain"):
        value = str((lead or {}).get(field, "")).strip()
        if value:
            return value
    return ""


def build_openalex_institution_url(lead, base_url=None, mailto=None):
    """Build a deterministic OpenAlex institution search URL for a lead."""
    search_term = _select_openalex_search_term(lead)
    if not search_term:
        return None

    cfg = load_openalex_runtime_config()
    params = {"search": search_term, "per-page": 1}
    contact_email = mailto if mailto is not None else cfg["mailto"]
    if contact_email:
        params["mailto"] = contact_email

    api_base = base_url if base_url is not None else cfg["base_url"]
    return f"{api_base}?{urlencode(params)}"


def _default_openalex_request(url, headers, timeout):
    request = Request(url, headers=headers)
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def lookup_openalex_institution(
    lead,
    request_fn=None,
    timeout_seconds=None,
    max_retries=None,
    backoff_seconds=None,
    sleep_fn=None,
):
    """Fetch the top OpenAlex institution match for a lead."""
    cfg = load_openalex_runtime_config()
    url = build_openalex_institution_url(
        lead,
        base_url=cfg["base_url"],
        mailto=cfg["mailto"],
    )
    if not url:
        return None

    requester = request_fn or _default_openalex_request
    headers = {"User-Agent": "lf-openalex-enrichment-mvp/1.0"}

    def perform_request(timeout=None):
        effective_timeout = timeout
        if effective_timeout is None:
            effective_timeout = cfg["timeout_seconds"]
        return requester(url=url, headers=headers, timeout=effective_timeout)

    return run_openalex_with_retry(
        perform_request,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        backoff_seconds=backoff_seconds,
        sleep_fn=sleep_fn,
    )
