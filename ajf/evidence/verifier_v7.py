"""AJF Evidence Verifier V007 - Raw Response Integrity."""

import json
import re
from urllib.parse import urlparse, parse_qs


class EvidenceVerifierV7:
    VERSION = "AJF-EVIDENCE-VERIFIER-007"

    def verify_source(self, agent_output, spec):
        trace = agent_output.get("source_trace")

        if not isinstance(trace, dict):
            return self._result(
                "NOT_VERIFIABLE",
                "Source trace is missing."
            )

        required = (
            "request_url",
            "http_status",
            "response_metadata",
            "response_record",
            "raw_response",
            "response_record_count",
            "execution_status"
        )

        missing = [key for key in required if key not in trace]

        if missing:
            return self._result(
                "NOT_VERIFIABLE",
                "Required trace fields are missing.",
                missing_fields=missing
            )

        try:
            raw_data = json.loads(trace["raw_response"])
        except (TypeError, ValueError):
            return self._result(
                "FAILED",
                "Raw response is not valid JSON."
            )

        if not isinstance(raw_data, list) or len(raw_data) < 2:
            return self._result(
                "FAILED",
                "Unexpected raw response structure."
            )

        metadata = raw_data[0]
        records = raw_data[1]

        if not isinstance(metadata, dict) or not isinstance(records, list):
            return self._result(
                "FAILED",
                "Invalid metadata or records structure."
            )

        if not records:
            return self._result(
                "FAILED",
                "Raw response contains no records."
            )

        url = urlparse(trace["request_url"])
        params = parse_qs(url.query)

        checks = {
            "provider": (
                url.scheme == "https"
                and url.hostname == "api.worldbank.org"
                and url.port is None
            ),
            "country_endpoint": (
                url.path ==
                "/v2/country/MA/indicator/SP.POP.TOTL"
            ),
            "format": params.get("format") == ["json"],
            "requested_year": (
                params.get("date") == [str(spec["year"])]
            ),
            "http_status": trace["http_status"] == 200,
            "execution_status": (
                trace["execution_status"] == "success"
            ),
            "raw_metadata_matches": (
                metadata == trace["response_metadata"]
            ),
            "raw_record_matches": (
                records[0] == trace["response_record"]
            ),
            "raw_record_count_matches": (
                len(records) == trace["response_record_count"]
                and metadata.get("total") == len(records)
            ),
            "country": (
                records[0].get("country", {}).get("id")
                == spec["country_code"]
            ),
            "indicator": (
                records[0].get("indicator", {}).get("id")
                == spec["indicator"]
            ),
            "year": (
                str(records[0].get("date"))
                == str(spec["year"])
            ),
            "value_exists": (
                isinstance(records[0].get("value"), (int, float))
                and not isinstance(records[0].get("value"), bool)
            )
        }

        failed = [
            name for name, passed in checks.items()
            if not passed
        ]

        if failed:
            return self._result(
                "FAILED",
                "One or more source integrity checks failed.",
                checks=checks,
                failed_checks=failed
            )

        evidence = agent_output.get("retrieved_evidence") or []

        if not evidence:
            return self._result(
                "NOT_VERIFIABLE",
                "Agent claim is missing.",
                checks=checks
            )

        numbers = re.findall(
            r"(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?",
            str(evidence[0])
        )

        if not numbers:
            return self._result(
                "NOT_VERIFIABLE",
                "Claimed numerical value is missing.",
                checks=checks
            )

        claimed_value = float(numbers[-1].replace(",", ""))
        source_value = float(records[0]["value"])

        checks["claim_matches_source"] = (
            claimed_value == source_value
        )

        status = (
            "VERIFIED"
            if checks["claim_matches_source"]
            else "FAILED"
        )

        return self._result(
            status,
            "Verification completed.",
            checks=checks,
            source_value=source_value,
            claimed_value=claimed_value,
            request_url=trace["request_url"],
            source_last_updated=metadata.get("lastupdated"),
            verification_scope=(
                "raw_response_internal_consistency_and_claim_matching"
            )
        )

    def _result(self, status, reason, **extra):
        return {
            "version": self.VERSION,
            "source_verification": status,
            "reason": reason,
            **extra
        }
