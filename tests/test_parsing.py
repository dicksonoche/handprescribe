import pytest
from src.parsing import parse_rule_based

def test_parse_rule_based():
    text = "Aspirin 81mg po daily"
    result = parse_rule_based(text)
    assert result["drug_name"] == "aspirin"  # Fuzzy match
    assert result["confidence"] > 0

# AI'll add more tests here