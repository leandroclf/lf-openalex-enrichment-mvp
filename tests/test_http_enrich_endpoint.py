"""
Test suite for HTTP /enrich endpoint integration.
"""

def test_enrich_endpoint_shape():
    """Verify /enrich endpoint returns expected structure."""
    from backend.src.api import batch_enrich_leads
    
    sample_leads = [
        {"company": "TestCorp", "domain": "test.com", "industry": "Tech", "employee_count": 50}
    ]
    
    result = batch_enrich_leads(sample_leads)
    
    assert "enriched" in result
    assert "stats" in result
    assert result["stats"]["total"] == 1
    assert len(result["enriched"]) == 1
    assert "_enrichment" in result["enriched"][0]


def test_enrich_endpoint_with_custom_config():
    """Verify custom config is applied correctly."""
    from backend.src.api import batch_enrich_leads

    leads = [
        {"name": "John", "email": "john@test.com", "phone": "123456"}
    ]

    config = {"fields": ["name", "email", "phone"]}
    result = batch_enrich_leads(leads, config)

    assert result["enriched"][0]["_enrichment"]["coverage"] == 1.0
    assert result["stats"]["coverage_rate"] == 1.0
    assert result["stats"]["enrichment_rate"] == 1.0


def test_enrich_endpoint_empty_leads():
    """Verify endpoint handles empty leads gracefully."""
    from backend.src.api import batch_enrich_leads
    
    result = batch_enrich_leads([])
    
    assert result["stats"]["total"] == 0
    assert result["enriched"] == []
    assert result["stats"]["coverage_rate"] == 0.0
