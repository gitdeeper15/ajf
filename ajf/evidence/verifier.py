"""
Verifier for extracting and validating claims from text.
NOTE: This is a prototype for the isolated test. It should replace the core logic eventually.
"""
import re
from typing import Dict, Any

class ClaimExtractionError(Exception):
    pass

def extract_claim_value(text: str) -> Dict[str, Any]:
    """
    Extracts a numerical value from a claim string.
    Handles 'approximately', 'about', '~' and exact numbers.
    """
    # Regex to match numbers with commas, decimals, and optional suffix (million, billion)
    # Matches: 37.5 million, 37,500,000, 38,081,173, ~37.5 million
    pattern = r"(?:approximately|about|~)?\s*([\d,]+(?:\.\d+)?)\s*(million|billion)?"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if not match:
        raise ClaimExtractionError(f"No numeric value found in: {text}")
    
    number_str = match.group(1).replace(",", "")
    unit = match.group(2)
    
    value = float(number_str)
    if unit:
        if unit.lower() == "million":
            value *= 1_000_000
        elif unit.lower() == "billion":
            value *= 1_000_000_000
            
    # Determine if the value is approximate or exact based on prefixes
    is_approximate = any(prefix in text.lower() for prefix in ["approximately", "about", "~"])
    claim_type = "approx" if is_approximate else "exact"
    
    # Convert to integer if it's a whole number, to avoid float issues
    if value.is_integer():
        value = int(value)
    
    return {"value": value, "type": claim_type}
