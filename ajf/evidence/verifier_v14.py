"""AJF V014 - Independent Claim, Provenance and Divergence Verification."""

import re
from datetime import datetime, timezone

import requests


class EvidenceVerifierV14:
    VERSION = "AJF-EVIDENCE-VERIFIER-014"
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
                or not isinstance(data[0], dict)
                or not isinstance(data[1], list)
                or not data[1]
                or not isinstance(data[1][0], dict)
            ):
                return self._result(
                    "NOT_VERIFIABLE",
                    "Independent source returned no usable record.",
                    divergence_classification="NOT_ASSESSABLE",
                    verification_timestamp=verification_timestamp
                )

            metadata = data[0]
            record = data[1][0]

        except Exception as exc:
            return self._result(
                "NOT_VERIFIABLE",
                f"Independent retrieval failed: "
                f"{type(exc).__name__}: {exc}",
                divergence_classification="NOT_ASSESSABLE",
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
            "independent_value_exists": self._is_numeric(
                source_value
            )
        }

        if not all(checks.values()):
            failed_checks = [
                key for key, passed in checks.items() if not passed
            ]
            return self._result(
                "NOT_VERIFIABLE",
                "Independent source response failed validation.",
                divergence_classification="NOT_ASSESSABLE",
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
                agent_last_updated = response_metadata.get(
                    "lastupdated"
                )

            if agent_record is not None:
                if not self._is_numeric(agent_record):
                    provenance_status = "INVALID_AGENT_RECORD"

                elif self._matches(agent_record, source_value):
                    provenance_status = "VERIFIED"

                elif (
                    agent_last_updated
                    and last_updated
                    and agent_last_updated != last_updated
                ):
                    provenance_status = (
                        "SOURCE_REVISION_DIFFERENCE"
                    )

                else:
                    provenance_status = "MISMATCH"

        claim_matches_agent = (
            self._matches(claimed_value, agent_record)
            if agent_record is not None else None
        )

        # Divergence classification is descriptive.
        # It does not infer intentional tampering.

        if claimed_value is None:
            divergence = "NOT_ASSESSABLE"

        elif provenance_status == "MISSING":
            divergence = "INSUFFICIENT_PROVENANCE"

        elif provenance_status == "VERIFIED":
            divergence = (
                "CONSISTENT"
                if claim_matches_source
                else "CLAIM_RECORD_MISMATCH"
            )

        elif provenance_status == "SOURCE_REVISION_DIFFERENCE":
            divergence = "SOURCE_VERSION_DIFFERENCE"

        else:
            divergence = "UNRESOLVED_DIVERGENCE"

        # Claim validity is determined primarily against
        # the independently retrieved source.

        if claimed_value is None:
            claim_status = "NOT_ASSESSABLE"
            overall_status = "NOT_ASSESSABLE"

        elif claim_matches_source:
            claim_status = "VERIFIED"

            if provenance_status == "VERIFIED":
                overall_status = "VERIFIED"

            elif provenance_status == "MISSING":
                overall_status = "PARTIALLY_VERIFIED"

            elif (
                provenance_status == "SOURCE_REVISION_DIFFERENCE"
            ):
                overall_status = "SOURCE_RESPONSE_MISMATCH"

            else:
                overall_status = "SOURCE_RESPONSE_MISMATCH"

        else:
            claim_status = "FAILED"
            overall_status = "FAILED"

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

        return self._result(
            overall_status,
            "Independent claim, provenance and divergence assessment completed.",
            claim_verification=claim_status,
            provenance_verification=provenance_status,
            divergence_classification=divergence,
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
                "independent_claim_validation_provenance_"
                "and_divergence_classification"
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

        if isinstance(evidence, (list, tuple)):
            text = "; ".join(str(item) for item in evidence)
        else:
            text = str(evidence)

        # The first non-empty segment is treated as the primary claim.
        segments = [
            segment.strip()
            for segment in re.split(r"[;\n]+", text)
            if segment.strip()
        ]

        if not segments:
            return None

        primary = segments[0]

        # Prefer the value after the claim separator.
        if ":" in primary:
            candidate = primary.split(":", 1)[1]
        else:
            candidate = primary

        numbers = re.findall(
            r"(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?",
            candidate
        )

        # Ambiguous primary claims are not assessed.
        if len(numbers) != 1:
            return None

        try:
            return float(numbers[0].replace(",", ""))
        except ValueError:
            return None

    def _result(self, status, reason, **extra):
        return {
            "version": self.VERSION,
            "source_verification": status,
            "reason": reason,
            **extra
        }
