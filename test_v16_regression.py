import json
from unittest.mock import patch

from ajf.evidence.verifier_v16 import EvidenceVerifierV16


COUNTRY = "MA"
INDICATOR = "SP.POP.TOTL"
YEAR = "2024"

VALUE = 38081173
OLD_VALUE = 50000000

CURRENT_DATE = "2026-10-08"
OLD_DATE = "2026-09-01"

SPEC = {
    "country_code": COUNTRY,
    "indicator": INDICATOR,
    "year": YEAR
}


def record(
    value=VALUE,
    country=COUNTRY,
    indicator=INDICATOR,
    year=YEAR
):
    return {
        "indicator": {
            "id": indicator,
            "value": "Population, total"
        },
        "country": {
            "id": country,
            "value": "Morocco"
        },
        "countryiso3code": "MAR",
        "date": year,
        "value": value,
        "unit": "",
        "obs_status": "",
        "decimal": 0
    }


def payload(
    value=VALUE,
    country=COUNTRY,
    indicator=INDICATOR,
    year=YEAR,
    lastupdated=CURRENT_DATE
):
    return [
        {
            "page": 1,
            "pages": 1,
            "per_page": 50,
            "total": 1,
            "sourceid": "2",
            "lastupdated": lastupdated
        },
        [
            record(
                value=value,
                country=country,
                indicator=indicator,
                year=year
            )
        ]
    ]


class FakeResponse:

    def __init__(self, data=None, status=200, error=None):
        self.data = data
        self.status_code = status
        self.error = error
        self.url = (
            "https://api.worldbank.org/v2/country/MA/"
            "indicator/SP.POP.TOTL?format=json&date=2024"
        )

    def raise_for_status(self):
        if self.error:
            raise RuntimeError(self.error)

        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        if isinstance(self.data, Exception):
            raise self.data
        return self.data


def agent(
    evidence=None,
    agent_value=VALUE,
    agent_date=CURRENT_DATE,
    include_trace=True,
    raw_data=None
):
    output = {
        "retrieved_evidence": (
            evidence if evidence is not None
            else f"Morocco population (2024): {VALUE}"
        )
    }

    if include_trace:
        raw = raw_data if raw_data is not None else payload(
            value=agent_value,
            lastupdated=agent_date
        )

        output["source_trace"] = {
            "request_url": (
                "https://api.worldbank.org/v2/country/MA/"
                "indicator/SP.POP.TOTL?format=json&date=2024"
            ),
            "http_status": 200,
            "execution_status": "success",
            "raw_response": json.dumps(raw),
            "response_metadata": raw[0] if isinstance(raw, list) and raw else {},
            "response_record": (
                raw[1][0]
                if isinstance(raw, list)
                and len(raw) > 1
                and isinstance(raw[1], list)
                and raw[1]
                else None
            ),
            "response_record_count": 1
        }

    return output


def run_case(name, output, independent_data=None,
             expected=None, expected_exception=None):

    fake = FakeResponse(data=independent_data)

    with patch(
        "ajf.evidence.verifier_v16.requests.get",
        return_value=fake
    ):
        result = EvidenceVerifierV16().verify_source(
            output,
            SPEC
        )

    actual = (
        result.get("source_verification"),
        result.get("claim_verification"),
        result.get("provenance_verification"),
        result.get("divergence_classification")
    )

    if expected is None:
        ok = True
    else:
        ok = actual == expected

    print(
        ("PASS" if ok else "FAIL"),
        "|", name,
        "|", actual,
        "| expected:", expected
    )

    if not ok:
        print("FULL RESULT:", result)

    return ok


def run_failure_case(name, output, fake_response, expected_status):

    with patch(
        "ajf.evidence.verifier_v16.requests.get",
        return_value=fake_response
    ):
        result = EvidenceVerifierV16().verify_source(
            output,
            SPEC
        )

    actual = result.get("source_verification")
    ok = actual == expected_status

    print(
        ("PASS" if ok else "FAIL"),
        "|", name,
        "|", actual,
        "| expected:", expected_status
    )

    if not ok:
        print("FULL RESULT:", result)

    return ok


passed = 0
total = 0


def check(value):
    global passed, total
    total += 1
    passed += int(value)


print("\n========== V016 SYNTHETIC REGRESSION ==========\n")


# A1: Baseline
check(run_case(
    "A1 BASELINE",
    agent(),
    payload(),
    (
        "VERIFIED",
        "VERIFIED",
        "VERIFIED",
        "CONSISTENT"
    )
))


# A2: Correct claim, forged agent record
check(run_case(
    "A2 FORGED AGENT RECORD",
    agent(agent_value=OLD_VALUE),
    payload(),
    (
        "SOURCE_RESPONSE_MISMATCH",
        "VERIFIED",
        "MISMATCH",
        "UNRESOLVED_DIVERGENCE"
    )
))


# A3: Coherent forgery
check(run_case(
    "A3 COHERENT FORGERY",
    agent(
        evidence=f"Morocco population (2024): {OLD_VALUE}",
        agent_value=OLD_VALUE
    ),
    payload(),
    (
        "FAILED",
        "FAILED",
        "MISMATCH",
        "UNRESOLVED_DIVERGENCE"
    )
))


# A4: Missing provenance trace
check(run_case(
    "A4 MISSING TRACE",
    agent(include_trace=False),
    payload(),
    (
        "PARTIALLY_VERIFIED",
        "VERIFIED",
        "MISSING",
        "INSUFFICIENT_PROVENANCE"
    )
))


# A5: False claim with older agent record
check(run_case(
    "A5 FALSE CLAIM WITH OLD RECORD",
    agent(
        evidence=f"Morocco population (2024): {OLD_VALUE}",
        agent_value=OLD_VALUE,
        agent_date=OLD_DATE
    ),
    payload(),
    (
        "FAILED",
        "FAILED",
        "SOURCE_REVISION_DIFFERENCE",
        "SOURCE_VERSION_DIFFERENCE"
    )
))


# A6: Claim tampering, valid agent record
check(run_case(
    "A6 CLAIM TAMPERING",
    agent(
        evidence=f"Morocco population (2024): {OLD_VALUE}",
        agent_value=VALUE,
        agent_date=CURRENT_DATE
    ),
    payload(),
    (
        "FAILED",
        "FAILED",
        "VERIFIED",
        "CLAIM_RECORD_MISMATCH"
    )
))


# A7: Invalid agent record
invalid_record_data = payload()
invalid_record_data[1][0]["value"] = None

check(run_case(
    "A7 INVALID AGENT RECORD",
    agent(
        agent_value=None,
        raw_data=invalid_record_data
    ),
    payload(),
    (
        "SOURCE_RESPONSE_MISMATCH",
        "VERIFIED",
        "INVALID_AGENT_RECORD",
        "UNRESOLVED_DIVERGENCE"
    )
))


# A8: Unassessable claim
check(run_case(
    "A8 UNASSESSABLE CLAIM",
    agent(evidence="Population data unavailable"),
    payload(),
    (
        "NOT_ASSESSABLE",
        "NOT_ASSESSABLE",
        "VERIFIED",
        "NOT_ASSESSABLE"
    )
))


print("\n========== V016 ROBUSTNESS TESTS ==========\n")


# B1: Wrong country
check(run_failure_case(
    "B1 WRONG COUNTRY",
    agent(),
    FakeResponse(data=payload(country="TN")),
    "NOT_VERIFIABLE"
))


# B2: Wrong indicator
check(run_failure_case(
    "B2 WRONG INDICATOR",
    agent(),
    FakeResponse(data=payload(indicator="SP.POP.GROW")),
    "NOT_VERIFIABLE"
))


# B3: Wrong year
check(run_failure_case(
    "B3 WRONG YEAR",
    agent(),
    FakeResponse(data=payload(year="2023")),
    "NOT_VERIFIABLE"
))


# B4: Null source value
null_data = payload()
null_data[1][0]["value"] = None

check(run_failure_case(
    "B4 NULL SOURCE VALUE",
    agent(),
    FakeResponse(data=null_data),
    "NOT_VERIFIABLE"
))


# B5: Invalid JSON
check(run_failure_case(
    "B5 INVALID JSON",
    agent(),
    FakeResponse(data=ValueError("Invalid JSON")),
    "NOT_VERIFIABLE"
))


# B6: HTTP failure
check(run_failure_case(
    "B6 HTTP FAILURE",
    agent(),
    FakeResponse(status=500, error="HTTP 500"),
    "NOT_VERIFIABLE"
))


# B7: Malformed response
check(run_failure_case(
    "B7 MALFORMED RESPONSE",
    agent(),
    FakeResponse(data={"unexpected": "structure"}),
    "NOT_VERIFIABLE"
))


# B8: Multiple statistics in evidence
check(run_case(
    "B8 MULTIPLE STATISTICS",
    agent(
        evidence=(
            "Morocco population (2024): 38081173; "
            "annual growth: 1.2%"
        )
    ),
    payload(),
    (
        "VERIFIED",
        "VERIFIED",
        "VERIFIED",
        "CONSISTENT"
    )
))


# B9: Correct claim, older agent record
check(run_case(
    "B9 OLD AGENT RECORD",
    agent(
        evidence=f"Morocco population (2024): {VALUE}",
        agent_value=OLD_VALUE,
        agent_date=OLD_DATE
    ),
    payload(),
    (
        "SOURCE_RESPONSE_MISMATCH",
        "VERIFIED",
        "SOURCE_REVISION_DIFFERENCE",
        "SOURCE_VERSION_DIFFERENCE"
    )
))


# B10: Boolean source value
boolean_data = payload()
boolean_data[1][0]["value"] = True

check(run_failure_case(
    "B10 BOOLEAN SOURCE VALUE",
    agent(),
    FakeResponse(data=boolean_data),
    "NOT_VERIFIABLE"
))


print("\n==============================================")
print(f"TOTAL: {total}/18")
print(f"RESULT: {'ALL PASS' if passed == total else 'FAILURES DETECTED'}")
print("==============================================")
