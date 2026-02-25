from backend.src.api import get_value_signal


def test_value_signal_shape():
    x=get_value_signal()
    assert x["issue"]=="ISSUE-001"
    assert x["targetLiftPct"]==20
