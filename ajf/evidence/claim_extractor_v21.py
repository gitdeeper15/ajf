import re
from decimal import Decimal, InvalidOperation


class ClaimExtractionError(Exception):
    pass


NUMBER = (
    r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)"
    r"(?:\.\d+)?(?:[eE][-+]?\d+)?"
)

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
    "people": Decimal("1"),
    "persons": Decimal("1"),
    "population": Decimal("1"),
}

APPROX = re.compile(
    r"\b(approximately|about|around|roughly)\b|~",
    re.I
)

UNIT_PATTERN = re.compile(
    r"\s*(million|millions|billion|billions|"
    r"thousand|thousands|people|persons|population|"
    r"[kmb])\b",
    re.I,
)


def extract_claim_value_v21(text):
    if not isinstance(text, str) or not text.strip():
        raise ClaimExtractionError("Empty claim")

    # Only the primary claim is evaluated.
    primary = re.split(r"[;\n]+", text, maxsplit=1)[0].strip()

    candidates = []

    for match in re.finditer(NUMBER, primary):
        start, end = match.span()
        number_text = match.group()

        before = primary[max(0, start - 40):start]
        after = primary[end:end + 30]

        unit_match = UNIT_PATTERN.match(after)
        unit = unit_match.group(1).lower() if unit_match else ""

        # Exclude contextual years, not population values with units.
        is_year = (
            not unit
            and re.fullmatch(r"\d{4}", number_text) is not None
            and 1900 <= int(number_text) <= 2100
            and (
                re.search(r"\bin\s*$", before, re.I)
                or re.search(
                    r"\b(population|estimate|year|data)\s*[:(]?\s*$",
                    before,
                    re.I,
                )
                or (
                    primary.rfind("(", 0, start)
                    > primary.rfind(")", 0, start)
                    and primary.find(")", end) != -1
                )
            )
        )

        if is_year:
            continue

        try:
            number = Decimal(number_text.replace(",", ""))
        except InvalidOperation:
            continue

        value = number * UNITS.get(unit, Decimal("1"))

        approximate = bool(
            APPROX.search(before) or APPROX.search(after)
        )

        score = 0
        if unit:
            score += 4
        if approximate:
            score += 5

        candidates.append(
            (score, value, approximate, unit)
        )

    if not candidates:
        raise ClaimExtractionError(
            "No assessable numeric claim in primary segment"
        )

    highest = max(item[0] for item in candidates)
    best = [item for item in candidates if item[0] == highest]

    if len(best) != 1:
        raise ClaimExtractionError("Ambiguous numeric claim")

    _, value, approximate, unit = best[0]

    if value == value.to_integral_value():
        value = int(value)
    else:
        value = float(value)

    return {
        "value": value,
        "type": "approx" if approximate else "exact",
        "unit": unit or "base_unit",
    }
