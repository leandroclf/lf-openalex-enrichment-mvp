from backend.src.api import get_sample_payload

REQUIRED_KEYS = {"component", "source", "status", "generatedAt"}

def test_contract_required_keys():
    payload = get_sample_payload()
    assert REQUIRED_KEYS.issubset(payload.keys())
    assert payload["status"] == "ok"
