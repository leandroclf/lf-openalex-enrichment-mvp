from backend.src.api import get_value_signal


def test_value_signal_shape():
    x=get_value_signal()
    assert x["issue"]=="ISSUE-001"
    assert x["targetLiftPct"]==20


from backend.src.api import calculate_attribute_coverage
from backend.src.api import calculate_weighted_attribute_coverage
from backend.src.api import summarize_value_portfolio
from backend.src.api import summarize_value_by_segment


def test_attribute_coverage_calculation():
    records = [
        {"title": "A", "doi": "10.1/x", "author": "Ana"},
        {"title": "B", "doi": "", "author": "Bruno"},
    ]
    cov = calculate_attribute_coverage(records, ["title", "doi", "author"])
    assert cov == 0.8333


def test_weighted_attribute_coverage_calculation():
    records = [
        {"title": "A", "doi": "10.1/x", "author": "Ana"},
        {"title": "B", "doi": "", "author": "Bruno"},
    ]
    # DOI has higher business weight than other fields.
    cov = calculate_weighted_attribute_coverage(records, {"title": 1, "doi": 2, "author": 1})
    assert cov == 0.75


def test_weighted_attribute_coverage_ignores_zero_or_negative_weights():
    records = [{"title": "A"}]
    assert calculate_weighted_attribute_coverage(records, {"title": 0, "doi": -2}) == 0.0


def test_summarize_value_portfolio():
    out = summarize_value_portfolio([
        {"accountId": "a1", "valueScore": 90},
        {"accountId": "a2", "valueScore": 60},
        {"accountId": "a3", "valueScore": 10},
    ])
    assert out == {"total": 3, "highValueCount": 1, "avgScore": 53.33}


def test_summarize_value_portfolio_empty():
    assert summarize_value_portfolio([]) == {"total": 0, "highValueCount": 0, "avgScore": 0.0}


def test_summarize_value_by_segment():
    out = summarize_value_by_segment([
        {"segment": "enterprise", "valueScore": 90},
        {"segment": "enterprise", "valueScore": 40},
        {"segment": "smb", "valueScore": 82},
    ])
    assert out == {
        "enterprise": {"total": 2, "highValue": 1},
        "smb": {"total": 1, "highValue": 1},
    }


def test_summarize_value_by_segment_empty():
    assert summarize_value_by_segment([]) == {}
