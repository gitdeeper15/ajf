"""AJF V008 - Independent Source Verification."""

import requests


class EvidenceVerifierV8:
    VERSION = "AJF-EVIDENCE-VERIFIER-008"

    BASE_URL = "https://api.worldbank.org/v2/country"

    def verify_source(self, agent_output, spec):
        trace = agent_output.get("source_trace", {})

        country = spec["country_code"]
        indicator = spec["indicator"]
        year = str(spec["year"])

        url = (
            f"{self.BASE_URL}/{country}/indicator/{indicator}"
        )

        try:
            response = requests.get(
                url,
                params={"format": "json", "date": year},
                timeout=15
            )

            response.raise_for_status()
            data = response.json()

            if (
                not isinstance(data, list)
                or len(data) < 2
                or not isinstance(data[1], list)
                or not data[1]
            ):
                return self._result(
                    "NOT_VERIFIABLE",
                    "Independent source returned no usable record."
                )

            metadata = data[0]
            record = data[1][0]

        except Exception as exc:
            return self._result(
                "NOT_VERIFIABLE",
                f"Independent retrieval failed: {type(exc).__name__}: {exc}"
            )

        checks = {
            "independent_http_status": response.status_code == 200,
            "independent_country": (
                record.get("country", {}).get("id") == country
            ),
            "independent_indicator": (
                record.get("indicator", {}).get("id") == indicator
            ),
            "independent_year": (
                str(record.get("date")) == year
            ),
            "independent_value_exists": (
                isinstance(record.get("value"), (int, float))
                and not isinstance(record.get("value"), bool)
            )
        }

        source_value = record.get("value")

        original_record = trace.get("response_record", {})
        original_value = original_record.get("value")

        checks["agent_record_matches_independent_source"] = (
            original_value is not None
            and source_value is not None
            and float(original_value) == float(source_value)
        )

        evidence = agent_output.get("retrieved_evidence") or []

        if evidence and source_value is not None:
            import re

            numbers = re.findall(
                r"(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?",
                str(evidence[0])
            )

            checks["agent_claim_matches_independent_source"] = (
                bool(numbers)
                and float(numbers[-1].replace(",", ""))
                == float(source_value)
            )
        else:
            checks["agent_claim_matches_independent_source"] = False

        failed = [
            key for key, passed in checks.items()
            if not passed
        ]

        return self._result(
            "VERIFIED" if not failed else "FAILED",
            "Independent comparison completed.",
            checks=checks,
            failed_checks=failed,
            independent_source_value=source_value,
            independent_source_url=response.url,
            independent_source_last_updated=metadata.get("lastupdated"),
            verification_scope=(
                "independent_world_bank_retrieval_and_value_comparison"
            )
        )

    def _result(self, status, reason, **extra):
        return {
            "version": self.VERSION,
            "source_verification": status,
            "reason": reason,
            **extra
        }
