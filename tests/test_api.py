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
