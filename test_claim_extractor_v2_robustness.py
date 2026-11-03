from ajf.evidence.claim_extractor_v2 import (
    extract_claim_value_v2,
    ClaimExtractionError,
)

cases = [
    ("38,081,173 people", 38081173),
    ("37.5 million", 37500000),
    ("38.08M", 38080000),
    ("38 thousand", 38000),
    ("0.038 billion", 38000000),
    ("3.8081173e7", 38081173),
    ("-37.5 million", -37500000),
    ("Population (2024): approximately 37.5 million", 37500000),
]

print("===== VALID CLAIMS =====")
passed = 0

for text, expected in cases:
    try:
        result = extract_claim_value_v2(text)
        ok = result["value"] == expected
        passed += int(ok)
        print(
            "PASS" if ok else "FAIL",
            repr(text),
            "=>", result,
            "expected:", expected,
        )
    except Exception as exc:
        print("FAIL", repr(text), type(exc).__name__, str(exc))

print(f"\nVALID: {passed}/{len(cases)}")

invalid_cases = [
    "Population in 2024",
    "No numerical information",
    "Population: approximately",
    "Population: 2024; estimate: 37.5 million",
    "Population: 37.5 million or 38 million",
]

print("\n===== AMBIGUOUS / INVALID CLAIMS =====")
for text in invalid_cases:
    try:
        print("REVIEW", repr(text), "=>", extract_claim_value_v2(text))
    except ClaimExtractionError as exc:
        print("REJECT", repr(text), "=>", exc)
