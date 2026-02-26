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


from backend.src.api import classify_value_band


def test_classify_value_band():
    assert classify_value_band(88) == "high"
    assert classify_value_band(65) == "medium"
    assert classify_value_band(20) == "low"


from backend.src.api import build_value_signal_summary


def test_build_value_signal_summary():
    s = build_value_signal_summary("acc-22", 84.2)
    assert s["band"] == "high"
    assert s["score"] == 84.2


from backend.src.api import is_high_value_account


def test_is_high_value_account():
    assert is_high_value_account(85) is True
    assert is_high_value_account(49) is False


from backend.src.api import score_to_percentile


def test_score_to_percentile():
    assert score_to_percentile(80) == 0.8
    assert score_to_percentile(125) == 1.0
