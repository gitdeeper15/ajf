import re
from decimal import Decimal, InvalidOperation


class ClaimExtractionError(Exception):
    pass


NUMBER = r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][-+]?\d+)?"

UNITS = {
    "thousand": Decimal("1000"),
    "thousands": Decimal("1000"),
    "k": Decimal("1000"),
    "million": Decimal("1000000"),
    "millions": Decimal("1000000"),
    "m": Decimal("1000000"),
    "billion": Decimal("1000000000"),
    "billions": Decimal("1000000000"),
    "b": Decimal("1000000000"),
}

APPROX = re.compile(r"\b(approximately|about|around|roughly)\b|~", re.I)


def extract_claim_value_v2(text):
    if not isinstance(text, str) or not text.strip():
        raise ClaimExtractionError("Empty claim")

    candidates = []

    for match in re.finditer(NUMBER, text):
        start, end = match.span()
        number_text = match.group()

        before = text[max(0, start - 35):start]
        after = text[end:end + 25]

        unit_match = re.match(
            r"\s*(million|millions|billion|billions|thousand|thousands|[kmb])\b",
            after,
            re.I,
        )

        unit = unit_match.group(1).lower() if unit_match else ""
        multiplier = UNITS.get(unit, Decimal("1"))

        try:
            value = Decimal(number_text.replace(",", "")) * multiplier
        except InvalidOperation:
            continue

        approximate = bool(APPROX.search(before)) or bool(
            re.search(r"\b(approximately|about|around|roughly)\b|~", after, re.I)
        )

        # A year in parentheses is contextual metadata, not the claim value.
        in_parentheses = (
            text.rfind("(", 0, start) > text.rfind(")", 0, start)
            and text.find(")", end) != -1
        )

        score = 0
        if unit:
            score += 4
        if approximate:
            score += 5
        if not in_parentheses:
            score += 2

        candidates.append((score, value, approximate, number_text, unit))

    if not candidates:
        raise ClaimExtractionError("No numeric claim found")

    highest = max(item[0] for item in candidates)
    best = [item for item in candidates if item[0] == highest]

    if len(best) != 1:
        raise ClaimExtractionError("Ambiguous numeric claim")

    _, value, approximate, _, unit = best[0]

    if value == value.to_integral_value():
        value = int(value)
    else:
        value = float(value)

    return {
        "value": value,
        "type": "approx" if approximate else "exact",
        "unit": unit or "base_unit",
    }
