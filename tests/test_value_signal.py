from backend.src.api import get_value_signal


def test_value_signal_shape():
    x=get_value_signal()
    assert x["issue"]=="ISSUE-001"
    assert x["targetLiftPct"]==20


from backend.src.api import calculate_attribute_coverage


def test_attribute_coverage_calculation():
    records = [
        {"title": "A", "doi": "10.1/x", "author": "Ana"},
        {"title": "B", "doi": "", "author": "Bruno"},
    ]
    cov = calculate_attribute_coverage(records, ["title", "doi", "author"])
    assert cov == 0.8333
