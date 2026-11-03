"""AJF V010 - Independent Claim, Record and Provenance Verification."""

import re
from datetime import datetime, timezone

import requests


class EvidenceVerifierV10:
    VERSION = "AJF-EVIDENCE-VERIFIER-010"
    BASE_URL = "https://api.worldbank.org/v2/country"

    def verify_source(self, agent_output, spec):
        verification_timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        country = spec["country_code"]
        indicator = spec["indicator"]
        year = str(spec["year"])

        trace = agent_output.get("source_trace")
        trace = trace if isinstance(trace, dict) else None

        url = f"{self.BASE_URL}/{country}/indicator/{indicator}"

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
                or not isinstance(data[0], dict)
                or not isinstance(data[1], list)
                or not data[1]
                or not isinstance(data[1][0], dict)
            ):
                return self._result(
                    "NOT_VERIFIABLE",
                    "Independent source returned no usable record.",
                    verification_timestamp=verification_timestamp
                )

            metadata = data[0]
            record = data[1][0]

        except Exception as exc:
            return self._result(
                "NOT_VERIFIABLE",
                f"Independent retrieval failed: "
                f"{type(exc).__name__}: {exc}",
                verification_timestamp=verification_timestamp
            )

        source_value = record.get("value")
        last_updated = metadata.get("lastupdated")

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
                isinstance(source_value, (int, float))
                and not isinstance(source_value, bool)
            )
        }

        if not all(checks.values()):
            failed_checks = [
                key for key, passed in checks.items() if not passed
            ]
            return self._result(
                "NOT_VERIFIABLE",
                "Independent source response failed validation.",
                checks=checks,
                failed_checks=failed_checks,
                independent_source_value=source_value,
                independent_source_last_updated=last_updated,
                independent_source_url=response.url,
                verification_timestamp=verification_timestamp
            )

        claimed_value = self._extract_claim(
            agent_output.get("retrieved_evidence")
        )

        claim_matches_source = self._matches(
            claimed_value, source_value
        )

        agent_record = None
        agent_last_updated = None
        provenance_status = "MISSING"

        if trace is not None:
            original_record = trace.get("response_record")

            if isinstance(original_record, dict):
                agent_record = original_record.get("value")

            response_metadata = trace.get("response_metadata")
            if isinstance(response_metadata, dict):
                agent_last_updated = response_metadata.get("lastupdated")

            if agent_record is not None:
                if self._is_numeric(agent_record):
                    if self._matches(agent_record, source_value):
                        provenance_status = "VERIFIED"
                    elif (
                        agent_last_updated
                        and last_updated
                        and agent_last_updated != last_updated
                    ):
                        provenance_status = "SOURCE_REVISION_DIFFERENCE"
                    else:
                        provenance_status = "MISMATCH"
                else:
                    provenance_status = "INVALID_AGENT_RECORD"

        claim_matches_agent = (
            self._matches(claimed_value, agent_record)
            if agent_record is not None else None
        )

        checks.update({
            "agent_claim_matches_independent_source": (
                claim_matches_source
            ),
            "agent_claim_matches_agent_record": (
                claim_matches_agent
            ),
            "agent_record_matches_independent_source": (
                provenance_status == "VERIFIED"
            )
        })

        # Classification priority:
        # A claim contradicting the agent's own record is a claim failure.
        if (
            claimed_value is None
            or (
                agent_record is not None
                and claim_matches_agent is False
            )
        ):
            claim_status = (
                "NOT_ASSESSABLE"
                if claimed_value is None
                else "FAILED"
            )
            overall_status = (
                "NOT_ASSESSABLE"
                if claimed_value is None
                else "FAILED"
            )

        elif provenance_status == "SOURCE_REVISION_DIFFERENCE":
            claim_status = (
                "VERIFIED" if claim_matches_source
                else "SOURCE_RESPONSE_MISMATCH"
            )
            overall_status = "SOURCE_REVISION_DETECTED"

        elif provenance_status in (
            "MISMATCH", "INVALID_AGENT_RECORD"
        ):
            claim_status = (
                "VERIFIED" if claim_matches_source
                else "SOURCE_RESPONSE_MISMATCH"
            )
            overall_status = "SOURCE_RESPONSE_MISMATCH"

        elif provenance_status == "MISSING":
            claim_status = (
                "VERIFIED" if claim_matches_source else "FAILED"
            )
            overall_status = (
                "PARTIALLY_VERIFIED"
                if claim_matches_source
                else "FAILED"
            )

        else:
            claim_status = (
                "VERIFIED" if claim_matches_source else "FAILED"
            )
            overall_status = (
                "VERIFIED" if claim_matches_source else "FAILED"
            )

        return self._result(
            overall_status,
            "Independent claim, agent record and provenance assessment completed.",
            claim_verification=claim_status,
            provenance_verification=provenance_status,
            source_availability="AVAILABLE",
            checks=checks,
            claimed_value=claimed_value,
            claim_matches_independent_source=claim_matches_source,
            claim_matches_agent_record=claim_matches_agent,
            independent_source_value=source_value,
            agent_record_value=agent_record,
            agent_source_last_updated=agent_last_updated,
            independent_source_last_updated=last_updated,
            agent_retrieval_timestamp=(
                trace.get("retrieval_timestamp") if trace else None
            ),
            verifier_retrieval_timestamp=verification_timestamp,
            independent_source_url=response.url,
            verification_scope=(
                "independent_claim_validation_agent_record_comparison"
            )
        )

    @staticmethod
    def _is_numeric(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )

    @classmethod
    def _matches(cls, first, second):
        if first is None or second is None:
            return False
        if not cls._is_numeric(first) or not cls._is_numeric(second):
            return False
        return float(first) == float(second)

    @staticmethod
    def _extract_claim(evidence):
        if not evidence:
            return None

        if isinstance(evidence, str):
            text = evidence
        elif isinstance(evidence, (list, tuple)):
            text = " ".join(str(item) for item in evidence)
        else:
            text = str(evidence)

        numbers = re.findall(
            r"(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?",
            text
        )

        if not numbers:
            return None

        try:
            return float(numbers[-1].replace(",", ""))
        except ValueError:
            return None

    def _result(self, status, reason, **extra):
        return {
            "version": self.VERSION,
            "source_verification": status,
            "reason": reason,
            **extra
        }
