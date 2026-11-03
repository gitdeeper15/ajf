"""AJF V016 - Unit-Aware Precision-Bounded Claim Verification."""

import re
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone

import requests


class EvidenceVerifierV16:
    VERSION = "AJF-EVIDENCE-VERIFIER-016"
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

        claim_details = self._parse_claim(
            agent_output.get("retrieved_evidence")
        )
        claimed_value = (
            claim_details["value"] if claim_details else None
        )

        claim_matches_source = self._matches_claim(
            claim_details, source_value
        )

        agent_record = None
        agent_last_updated = None
        provenance_status = "MISSING"

        if trace is not None:
            original_record = trace.get("response_record")

            response_metadata = trace.get("response_metadata")

            if isinstance(response_metadata, dict):
                agent_last_updated = response_metadata.get(
                    "lastupdated"
                )

            if isinstance(original_record, dict):
                agent_record = original_record.get("value")

                if not self._is_numeric(agent_record):
                    provenance_status = "INVALID_AGENT_RECORD"

                elif self._matches(agent_record, source_value):
                    provenance_status = "VERIFIED"

                elif (
                    agent_last_updated
                    and last_updated
                    and agent_last_updated != last_updated
                ):
                    provenance_status = "SOURCE_REVISION_DIFFERENCE"

                else:
                    provenance_status = "MISMATCH"

        claim_matches_agent = (
            self._matches_claim(claim_details, agent_record)
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
            claim_unit=claim_details["unit"] if claim_details else None,
            claim_precision=claim_details["precision"] if claim_details else None,
            claim_lower_bound=claim_details["lower_bound"] if claim_details else None,
            claim_upper_bound=claim_details["upper_bound"] if claim_details else None,
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
    def _parse_claim(evidence):
        if not evidence:
            return None

        if isinstance(evidence, (list, tuple)):
            if len(evidence) != 1:
                return None
            text = str(evidence[0])
        else:
            text = str(evidence)

        segments = [
            x.strip()
            for x in re.split(r"[;\n]+", text)
            if x.strip()
        ]

        if not segments:
            return None

        primary = segments[0]

        if ":" in primary:
            candidate = primary.split(":", 1)[1].strip()
        else:
            candidate = primary

        pattern = (
            r"(?<![A-Za-z0-9])"
            r"[-+]?"
            r"(?:\d{1,3}(?:,\d{3})+|\d+)"
            r"(?:\.\d+)?"
            r"(?:[eE][-+]?\d+)?"
        )

        matches = list(re.finditer(pattern, candidate))

        if len(matches) != 1:
            return None

        match = matches[0]
        number_text = match.group(0)

        try:
            number = Decimal(number_text.replace(",", ""))
        except InvalidOperation:
            return None

        remainder = candidate[match.end():].strip()
        unit_match = re.match(
            r"^(million|millions|billion|billions|"
            r"thousand|thousands|people|persons|population|"
            r"[KkMmBb])(?![A-Za-z])",
            remainder,
            re.IGNORECASE
        )

        unit = unit_match.group(1).lower() if unit_match else ""

        multipliers = {
            "": Decimal("1"),
            "people": Decimal("1"),
            "persons": Decimal("1"),
            "population": Decimal("1"),
            "thousand": Decimal("1000"),
            "thousands": Decimal("1000"),
            "k": Decimal("1000"),
            "million": Decimal("1000000"),
            "millions": Decimal("1000000"),
            "m": Decimal("1000000"),
            "billion": Decimal("1000000000"),
            "billions": Decimal("1000000000"),
            "b": Decimal("1000000000")
        }

        if unit not in multipliers:
            return None

        multiplier = multipliers[unit]
        value = number * multiplier

        # Determine the displayed rounding quantum.
        mantissa = re.split(r"[eE]", number_text)[0]
        exponent_match = re.search(r"[eE]([-+]?\d+)$", number_text)
        exponent = int(exponent_match.group(1)) if exponent_match else 0

        decimal_places = (
            len(mantissa.split(".", 1)[1])
            if "." in mantissa else 0
        )

        precision = (
            Decimal(10) ** (exponent - decimal_places)
        ) * multiplier

        if precision <= 0:
            return None

        half = precision / Decimal("2")

        return {
            "value": float(value),
            "unit": unit or "base_unit",
            "precision": float(precision),
            "lower_bound": float(value - half),
            "upper_bound": float(value + half)
        }

    @classmethod
    def _extract_claim(cls, evidence):
        parsed = cls._parse_claim(evidence)
        return parsed["value"] if parsed else None

    @staticmethod
    def _matches_claim(claim_details, source_value):
        if claim_details is None:
            return False

        if not isinstance(source_value, (int, float)):
            return False

        if isinstance(source_value, bool):
            return False

        value = float(source_value)

        return (
            claim_details["lower_bound"] <= value
            < claim_details["upper_bound"]
        )

    def _result(self, status, reason, **extra):
        return {
            "version": self.VERSION,
            "source_verification": status,
            "reason": reason,
            **extra
        }
