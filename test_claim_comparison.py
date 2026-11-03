from ajf.evidence.verifier import (
    extract_claim_value,
    ClaimExtractionError,
)
from ajf.evidence.verifier_v16 import EvidenceVerifierV16

evidence = [
    "morocco population: Morocco population (2024): approximately 37.5 million (World Bank WDI, SP.POP.TOTL).",
    "Morocco water resources: renewable water resources per capita.",
    "Morocco GDP: GDP per capita information.",
    "World Bank WDI: international development indicators.",
]

print("===== INDEPENDENT EXTRACTOR =====")
for index, item in enumerate(evidence, 1):
    try:
        print(index, extract_claim_value(item))
    except ClaimExtractionError as exc:
        print(index, "NO CLAIM:", exc)

print("\n===== V016 PARSER PER ITEM =====")
for index, item in enumerate(evidence, 1):
    print(index, EvidenceVerifierV16._parse_claim(item))

print("\n===== V016 PARSER FULL LIST =====")
print(EvidenceVerifierV16._parse_claim(evidence))
