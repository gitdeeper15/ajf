from ajf.evidence.claim_extractor_v2 import extract_claim_value_v2

cases = [
    "Morocco population (2024): approximately 37.5 million",
    "Morocco population (2024): 37.5 million",
    "Population in 2024 was about 37.5 million",
    "Morocco population: 38,081,173 people",
    "Approximately 37.5 million people in Morocco",
]

for text in cases:
    print("\nINPUT:", text)
    try:
        print("OUTPUT:", extract_claim_value_v2(text))
    except Exception as exc:
        print("ERROR:", exc)
