"""
Independent test for claim extraction of approximate values.
This does NOT modify the core V016 logic. It isolates the extraction behavior.
"""
import pytest
from ajf.evidence.verifier import extract_claim_value, ClaimExtractionError

# The test cases for approximate and exact values
test_cases = [
    ("approximately 37.5 million", 37_500_000, "approx"),
    ("about 37.5 million", 37_500_000, "approx"),
    ("~37.5 million", 37_500_000, "approx"),
    ("37.5 million", 37_500_000, "exact"),
    ("38,081,173", 38_081_173, "exact"),
]

@pytest.mark.parametrize("text, expected_value, expected_type", test_cases)
def test_extract_approximate_claims(text, expected_value, expected_type):
    """Test that the extractor correctly identifies the numerical value and type."""
    try:
        claim = extract_claim_value(text)
        # Assert the extracted value matches the expected value
        assert claim["value"] == expected_value, f"Expected {expected_value}, got {claim['value']}"
        # Assert the type matches (approx or exact)
        assert claim["type"] == expected_type, f"Expected type {expected_type}, got {claim['type']}"
    except ClaimExtractionError as e:
        pytest.fail(f"Failed to extract claim from '{text}': {e}")

# A separate test to ensure it doesn't break on completely invalid input
def test_extract_invalid_claim():
    """Test that the extractor handles non-numerical text gracefully."""
    with pytest.raises(ClaimExtractionError):
        extract_claim_value("No number here")
