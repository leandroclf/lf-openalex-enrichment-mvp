from backend.src.api import get_value_signal


def test_value_signal_shape():
    x = get_value_signal()
    assert x["issue"] == "ISSUE-001"
    assert x["targetLiftPct"] == 20


from backend.src.api import calculate_attribute_coverage
from backend.src.api import calculate_weighted_attribute_coverage
from backend.src.api import calculate_lead_value_score
from backend.src.api import extract_openalex_match
from backend.src.api import merge_openalex_match
from backend.src.api import summarize_value_portfolio
from backend.src.api import summarize_value_by_segment
from backend.src.api import calculate_segment_lift_vs_baseline
from backend.src.api import summarize_value_distribution
from backend.src.api import estimate_high_value_rate
from backend.src.api import calculate_coverage_delta


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


def test_extract_openalex_match_projects_top_result():
    payload = {
        "results": [
            {
                "id": "https://openalex.org/I123",
                "display_name": "OpenAI Research",
                "homepage_url": "https://www.openai.com/",
                "works_count": 420,
                "cited_by_count": 8400,
                "geo": {"country_code": "US"},
                "x_concepts": [{"display_name": "Artificial Intelligence"}],
            }
        ]
    }

    match = extract_openalex_match(payload)

    assert match == {
        "id": "https://openalex.org/I123",
        "display_name": "OpenAI Research",
        "country_code": "US",
        "works_count": 420,
        "cited_by_count": 8400,
        "homepage_url": "https://www.openai.com/",
        "homepage_domain": "openai.com",
        "topic": "Artificial Intelligence",
    }


def test_merge_openalex_match_fills_missing_fields():
    lead = {"company": "", "domain": "", "industry": "", "country": ""}
    match = {
        "id": "https://openalex.org/I123",
        "display_name": "OpenAI Research",
        "country_code": "US",
        "works_count": 420,
        "cited_by_count": 8400,
        "homepage_url": "https://www.openai.com/",
        "homepage_domain": "openai.com",
        "topic": "Artificial Intelligence",
    }

    enriched = merge_openalex_match(lead, match)

    assert enriched["company"] == "OpenAI Research"
    assert enriched["domain"] == "openai.com"
    assert enriched["industry"] == "Artificial Intelligence"
    assert enriched["country"] == "US"
    assert enriched["openalex_id"] == "https://openalex.org/I123"


def test_calculate_lead_value_score_rewards_coverage_and_footprint():
    assert calculate_lead_value_score(0.5, None) == 30.0
    assert calculate_lead_value_score(1.0, {"works_count": 5000, "cited_by_count": 20000}) == 100.0


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


def test_calculate_segment_lift_vs_baseline():
    out = calculate_segment_lift_vs_baseline([
        {"segment": "enterprise", "valueScore": 90},
        {"segment": "enterprise", "valueScore": 40},
        {"segment": "smb", "valueScore": 82},
    ], baseline_score=50)
    assert out == 41.34


def test_calculate_segment_lift_vs_baseline_empty_or_zero_base():
    assert calculate_segment_lift_vs_baseline([], baseline_score=50) == 0.0
    assert calculate_segment_lift_vs_baseline([{"segment": "x", "valueScore": 90}], baseline_score=0) == 0.0


def test_summarize_value_distribution():
    out = summarize_value_distribution([
        {"valueScore": 90},
        {"valueScore": 62},
        {"valueScore": 10},
        {"valueScore": 82},
    ])
    assert out == {"high": 2, "medium": 1, "low": 1}


def test_summarize_value_distribution_empty():
    assert summarize_value_distribution([]) == {"high": 0, "medium": 0, "low": 0}


def test_estimate_high_value_rate():
    out = estimate_high_value_rate([
        {"valueScore": 90},
        {"valueScore": 62},
        {"valueScore": 10},
        {"valueScore": 82},
    ])
    assert out == 0.5


def test_estimate_high_value_rate_empty():
    assert estimate_high_value_rate([]) == 0.0


def test_calculate_coverage_delta():
    records = [
        {"title": "A", "doi": "10.1/x", "author": "Ana"},
        {"title": "B", "doi": "", "author": "Bruno"},
    ]
    delta = calculate_coverage_delta(records, ["title", "doi", "author"], baseline_coverage=0.70)
    assert delta == 13.33


def test_calculate_coverage_delta_zero_baseline():
    assert calculate_coverage_delta([{"title": "A"}], ["title"], baseline_coverage=0) == 0.0


def test_batch_enrich_leads_empty():
    from backend.src.api import batch_enrich_leads
    result = batch_enrich_leads([])
    assert result["stats"]["total"] == 0
    assert result["enriched"] == []
    assert result["stats"]["matched_count"] == 0


def test_batch_enrich_leads_with_data():
    from backend.src.api import batch_enrich_leads
    leads = [
        {"company": "Acme", "domain": "acme.com", "industry": "Tech", "employee_count": 100},
        {"company": "Beta", "domain": "", "industry": "", "employee_count": None}
    ]
    result = batch_enrich_leads(leads)
    assert result["stats"]["total"] == 2
    assert len(result["enriched"]) == 2
    assert result["enriched"][0]["_enrichment"]["coverage"] == 1.0


def test_batch_enrich_leads_with_openalex_lookup_improves_coverage():
    from backend.src.api import batch_enrich_leads

    leads = [{"company": "", "domain": "", "industry": "", "employee_count": None}]

    def fake_lookup(_lead):
        return {
            "results": [
                {
                    "id": "https://openalex.org/I123",
                    "display_name": "OpenAI Research",
                    "homepage_url": "https://openai.com",
                    "works_count": 420,
                    "cited_by_count": 8400,
                    "geo": {"country_code": "US"},
                    "x_concepts": [{"display_name": "Artificial Intelligence"}],
                }
            ]
        }

    result = batch_enrich_leads(
        leads,
        {
            "fields": ["company", "domain", "industry", "employee_count"],
            "lookup_fn": fake_lookup,
        },
    )

    enriched = result["enriched"][0]
    assert result["stats"]["matched_count"] == 1
    assert result["stats"]["improved_count"] == 1
    assert result["stats"]["avg_coverage_before"] == 0.0
    assert result["stats"]["avg_coverage_after"] == 0.75
    assert enriched["company"] == "OpenAI Research"
    assert enriched["domain"] == "openai.com"
    assert enriched["industry"] == "Artificial Intelligence"
    assert enriched["_enrichment"]["coverage_before"] == 0.0
    assert enriched["_enrichment"]["coverage"] == 0.75
    assert enriched["_enrichment"]["value_band"] == "medium"


def test_normalize_required_fields_trims_and_fills_missing():
    from backend.src.api import normalize_required_fields

    lead = {"company": "  Acme  ", "domain": None, "industry": " Tech "}
    out = normalize_required_fields(lead, ["company", "domain", "industry", "employee_count"])

    assert out["company"] == "Acme"
    assert out["domain"] == ""
    assert out["industry"] == "Tech"
    assert out["employee_count"] == ""


def test_batch_enrich_leads_applies_required_field_normalization():
    from backend.src.api import batch_enrich_leads

    leads = [{"company": " Acme ", "domain": "  ", "industry": "Tech", "employee_count": None}]
    result = batch_enrich_leads(leads)

    enriched = result["enriched"][0]
    assert enriched["company"] == "Acme"
    assert enriched["domain"] == ""
    assert enriched["employee_count"] == ""
    assert enriched["_enrichment"]["coverage"] == 0.5


def test_enrichment_priority_score():
    from backend.src.api import get_enrichment_priority_score
    complete_lead = {
        "company": "X",
        "domain": "x.com",
        "email": "a@x.com",
        "industry": "Tech",
        "employee_count": 50,
    }
    incomplete_lead = {"company": "Y"}

    assert get_enrichment_priority_score(complete_lead) == 0
    assert get_enrichment_priority_score(incomplete_lead) > 0

def test_prioritize_leads_by_enrichment_gap_orders_by_missing_weight():
    from backend.src.api import prioritize_leads_by_enrichment_gap

    leads = [
        {"company": "A", "domain": "a.com", "email": "a@a.com"},
        {"company": "B"},
        {"company": "C", "domain": "c.com", "email": "c@c.com", "industry": "Tech", "employee_count": 120},
    ]

    out = prioritize_leads_by_enrichment_gap(leads)
    assert out[0]["company"] == "B"
    assert out[0]["_priorityScore"] > out[1]["_priorityScore"]
    assert out[-1]["company"] == "C"


def test_prioritize_leads_by_enrichment_gap_empty():
    from backend.src.api import prioritize_leads_by_enrichment_gap
    assert prioritize_leads_by_enrichment_gap([]) == []
