"""AJF Evidence Source Verifier V006."""

from urllib.parse import urlparse, parse_qs


class EvidenceVerifierV6:
    VERSION = "AJF-EVIDENCE-VERIFIER-006"

    def verify_source(self, agent_output, spec):
        trace = agent_output.get("source_trace")

        if not isinstance(trace, dict):
            return {
                "version": self.VERSION,
                "source_verification": "NOT_VERIFIABLE",
                "reason": "Source trace is missing."
            }

        required = (
            "request_url",
            "http_status",
            "response_metadata",
            "response_record",
            "execution_status"
        )

        missing = [key for key in required if key not in trace]

        if missing:
            return {
                "version": self.VERSION,
                "source_verification": "NOT_VERIFIABLE",
                "reason": "Missing trace fields.",
                "missing_fields": missing
            }

        checks = {}

        url = urlparse(trace["request_url"])
        params = parse_qs(url.query)

        checks["provider"] = (
            url.hostname == "api.worldbank.org"
        )

        checks["country_endpoint"] = (
            url.path == "/v2/country/MA/indicator/SP.POP.TOTL"
        )

        checks["format"] = (
            params.get("format") == ["json"]
        )

        checks["requested_year"] = (
            params.get("date") == [str(spec["year"])]
        )

        checks["http_status"] = (
            trace["http_status"] == 200
        )

        checks["execution_status"] = (
            trace["execution_status"] == "success"
        )

        metadata = trace["response_metadata"]
        record = trace["response_record"]

        checks["record_count"] = (
            metadata.get("total") == 1
        )

        checks["country"] = (
            record.get("country", {}).get("id")
            == spec["country_code"]
        )

        checks["indicator"] = (
            record.get("indicator", {}).get("id")
            == spec["indicator"]
        )

        checks["year"] = (
            str(record.get("date")) == str(spec["year"])
        )

        checks["value_exists"] = (
            isinstance(record.get("value"), (int, float))
        )

        failures = [
            name for name, passed in checks.items()
            if not passed
        ]

        if failures:
            return {
                "version": self.VERSION,
                "source_verification": "FAILED",
                "checks": checks,
                "failed_checks": failures
            }

        raw_value = record["value"]

        claimed_values = agent_output.get("retrieved_evidence") or []

        if not claimed_values:
            return {
                "version": self.VERSION,
                "source_verification": "NOT_VERIFIABLE",
                "reason": "Agent claim is missing.",
                "checks": checks,
                "source_value": raw_value
            }

        import re

        claimed_text = str(claimed_values[0])
        numbers = re.findall(
            r"(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?",
            claimed_text
        )

        if not numbers:
            return {
                "version": self.VERSION,
                "source_verification": "NOT_VERIFIABLE",
                "reason": "Claimed numerical value is missing.",
                "checks": checks,
                "source_value": raw_value
            }

        claimed_value = float(numbers[-1].replace(",", ""))

        checks["claim_matches_source"] = (
            claimed_value == float(raw_value)
        )

        return {
            "version": self.VERSION,
            "source_verification": (
                "VERIFIED"
                if checks["claim_matches_source"]
                else "FAILED"
            ),
            "checks": checks,
            "source_value": raw_value,
            "claimed_value": claimed_value,
            "request_url": trace["request_url"],
            "source_last_updated": metadata.get("lastupdated")
        }
