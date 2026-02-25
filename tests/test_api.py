from backend.src.api import get_sample_payload

def test_payload_shape():
    payload = get_sample_payload()
    assert payload["status"] == "ok"
    assert "component" in payload
    assert "source" in payload
    assert "generatedAt" in payload
