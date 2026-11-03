from ajf.evidence.claim_extractor_v21 import (
    extract_claim_value_v21,
    ClaimExtractionError,
)

cases = [
    ("Population (2024): approximately 37.5 million", 37500000),
    ("Population (2024): 37.5 million", 37500000),
    ("Population in 2024 was about 37.5 million", 37500000),
    ("38,081,173 people", 38081173),
    ("38.08M", 38080000),
    ("38 thousand", 38000),
    ("0.038 billion", 38000000),
    ("3.8081173e7", 38081173),
    ("-37.5 million", -37500000),
]

invalid = [
    "Population in 2024",
    "No numerical information",
    "Population: approximately",
    "Population: 2024; estimate: 37.5 million",
    "Population: 37.5 million or 38 million",
]

passed = 0

print("===== VALID CLAIMS =====")
for text, expected in cases:
    try:
        result = extract_claim_value_v21(text)
        ok = result["value"] == expected
        passed += int(ok)
        print("PASS" if ok else "FAIL", text, result)
    except Exception as exc:
        print("FAIL", text, repr(exc))

print(f"VALID: {passed}/{len(cases)}")

print("\n===== INVALID / AMBIGUOUS =====")
rejected = 0
for text in invalid:
    try:
        result = extract_claim_value_v21(text)
        print("REVIEW", text, result)
    except ClaimExtractionError as exc:
        rejected += 1
        print("REJECT", text, str(exc))

print(f"REJECTED: {rejected}/{len(invalid)}")
