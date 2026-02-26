from backend.src.api import get_sample_payload

def test_payload_shape():
    payload = get_sample_payload()
    assert payload["status"] == "ok"
    assert "component" in payload
    assert "source" in payload
    assert "generatedAt" in payload


from backend.src.api import get_value_endpoint_response


def test_value_endpoint_response_shape():
    payload = get_value_endpoint_response("acc-1", 87.3)
    assert payload["issue"] == "ISSUE-016"
    assert payload["accountId"] == "acc-1"
    assert payload["valueScore"] == 87.3
    assert payload["status"] == "ready"


from backend.src.api import clamp_value_score


def test_clamp_value_score():
    assert clamp_value_score(-5) == 0.0
    assert clamp_value_score(107.9) == 100.0
    assert clamp_value_score(87.345) == 87.34


from backend.src.api import build_value_endpoint_payload


def test_build_value_endpoint_payload():
    p = build_value_endpoint_payload("acc-9", 101, "mid-market")
    assert p["issue"] == "ISSUE-016"
    assert p["valueScore"] == 100.0
    assert p["segment"] == "mid-market"
