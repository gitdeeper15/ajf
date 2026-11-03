"""AJF V009 - Independent Claim and Provenance Verification."""

import re
from datetime import datetime, timezone

import requests


class EvidenceVerifierV9:
    VERSION = "AJF-EVIDENCE-VERIFIER-009"
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

        # 1. Independent claim verification
        claimed_value = self._extract_claim(
            agent_output.get("retrieved_evidence")
        )

        claim_matches = (
            claimed_value is not None
            and float(claimed_value) == float(source_value)
        )

        claim_status = (
            "VERIFIED" if claim_matches
            else "FAILED" if claimed_value is not None
            else "NOT_ASSESSABLE"
        )

        # 2. Agent provenance verification
        provenance_status = "MISSING"
        agent_value = None
        agent_last_updated = None

        if trace is not None:
            original_record = trace.get("response_record")

            if isinstance(original_record, dict):
                agent_value = original_record.get("value")

            response_metadata = trace.get("response_metadata")
            if isinstance(response_metadata, dict):
                agent_last_updated = response_metadata.get("lastupdated")

            if agent_value is not None:
                try:
                    if float(agent_value) == float(source_value):
                        provenance_status = "VERIFIED"
                    elif (
                        agent_last_updated
                        and last_updated
                        and agent_last_updated != last_updated
                    ):
                        provenance_status = "SOURCE_REVISION_DIFFERENCE"
                    else:
                        provenance_status = "MISMATCH"
                except (TypeError, ValueError):
                    provenance_status = "INVALID_AGENT_RECORD"

        # 3. Overall classification
        if claim_status == "FAILED":
            overall_status = "FAILED"

        elif claim_status == "NOT_ASSESSABLE":
            overall_status = "NOT_ASSESSABLE"

        elif provenance_status == "VERIFIED":
            overall_status = "VERIFIED"

        elif provenance_status == "MISSING":
            overall_status = "PARTIALLY_VERIFIED"

        elif provenance_status == "SOURCE_REVISION_DIFFERENCE":
            overall_status = "SOURCE_REVISION_DETECTED"

        else:
            overall_status = "SOURCE_RESPONSE_MISMATCH"

        return self._result(
            overall_status,
            "Independent claim and provenance assessment completed.",
            claim_verification=claim_status,
            provenance_verification=provenance_status,
            source_availability="AVAILABLE",
            checks={
                **checks,
                "agent_claim_matches_independent_source": claim_matches,
                "agent_record_matches_independent_source": (
                    provenance_status == "VERIFIED"
                )
            },
            claimed_value=claimed_value,
            independent_source_value=source_value,
            agent_record_value=agent_value,
            agent_source_last_updated=agent_last_updated,
            independent_source_last_updated=last_updated,
            agent_retrieval_timestamp=(
                trace.get("retrieval_timestamp") if trace else None
            ),
            verifier_retrieval_timestamp=verification_timestamp,
            independent_source_url=response.url,
            verification_scope=(
                "independent_claim_validation_and_agent_provenance_comparison"
            )
        )

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
