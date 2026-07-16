import pytest
from backend.ai_service import AIService

def test_rule_based_fallback():
    event_desc = "AI for Sustainable Cities and renewable energy solutions."
    interests = ["climate change", "urban planning"]
    
    themes, starters = AIService._run_rule_based(event_desc, interests)
    
    # Verify theme extraction (should match AI and Sustainability / Climate Change)
    assert len(themes) > 0
    assert "AI" in themes or "Sustainability" in themes or "Climate Change" in themes
    
    # Verify starter generation (should generate exactly 3 starters)
    assert len(starters) == 3
    for starter in starters:
        assert isinstance(starter, str)
        assert len(starter) > 20
        # Should include relevant keywords
        assert "climate change" in starter or "urban planning" in starter

def test_ai_service_interface():
    # Calling the main interface method
    themes, starters = AIService.extract_themes_and_generate_starters(
        "Introduction to Fintech",
        ["finance", "cryptocurrency"]
    )
    
    assert isinstance(themes, list)
    assert isinstance(starters, list)
    assert len(starters) == 3
