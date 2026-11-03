import re
from typing import Any, Dict, List


class EvidenceVerifierV3:
    VERSION = "AJF-EVIDENCE-VERIFIER-003"

    UNIT_FACTORS = {
        "person": 1,
        "persons": 1,
        "people": 1,
        "million": 1_000_000,
        "millions": 1_000_000,
        "billion": 1_000_000_000,
        "billions": 1_000_000_000,
        "thousand": 1_000,
        "thousands": 1_000,
    }

    def _normalize(self, value: Any) -> str:
        return re.sub(r"\s+", " ", str(value).lower()).strip()

    def _number(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).lower().replace(",", "").strip()
        match = re.search(r"[-+]?\d+(?:\.\d+)?", text)

        if not match:
            raise ValueError("No numerical value found")

        number = float(match.group())

        suffix = text[match.end():].strip()
        suffix_match = re.match(
            r"(million|millions|billion|billions|thousand|thousands|m|bn|b)\b",
            suffix
        )

        if suffix_match:
            unit = suffix_match.group(1)
            factors = {
                "m": 1_000_000,
                "bn": 1_000_000_000,
                "b": 1_000_000_000,
                **self.UNIT_FACTORS
            }
            number *= factors[unit]

        return number

    def _extract_year(self, text: str):
        match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        return int(match.group(1)) if match else None

    def _classify(self, evidence: Any, spec: Dict[str, Any]) -> Dict:
        if isinstance(evidence, dict):
            text = self._normalize(evidence.get("text", ""))
            entity = evidence.get("entity")
            metric = evidence.get("metric")
            year = evidence.get("year")
            value = evidence.get("value")
            unit = evidence.get("unit")
        else:
            text = self._normalize(evidence)
            entity = None
            metric = None
            year = self._extract_year(text)
            value = None
            unit = None

        expected_entity = self._normalize(spec["entity"])
        expected_metric = self._normalize(spec["metric"])
        expected_year = int(spec["year"])

        # Extract information from unstructured text when possible.
        if entity is None:
            if expected_entity in text:
                entity = expected_entity

        if metric is None:
            if expected_metric in text:
                metric = expected_metric

        if year is None:
            year = self._extract_year(text)

        if value is None:
            try:
                value = self._number(text)
            except ValueError:
                value = None

        # Explicit metadata mismatches indicate irrelevance.
        if entity is not None:
            if self._normalize(entity) != expected_entity:
                return {
                    "classification": "IRRELEVANT",
                    "reason": "Different entity."
                }

        if metric is not None:
            if self._normalize(metric) != expected_metric:
                return {
                    "classification": "IRRELEVANT",
                    "reason": "Different metric."
                }

        if year is not None and int(year) != expected_year:
            return {
                "classification": "IRRELEVANT",
                "reason": "Different year."
            }

        # Missing required dimensions prevent a reliable comparison.
        if entity is None or metric is None or year is None or value is None:
            return {
                "classification": "UNCERTAIN",
                "reason": "Insufficient entity, metric, year, or numerical evidence."
            }

        try:
            actual = self._number(value)

            if unit:
                factor = self.UNIT_FACTORS.get(self._normalize(unit))
                if factor is None:
                    return {
                        "classification": "UNCERTAIN",
                        "reason": "Unsupported evidence unit."
                    }
                actual *= factor

            expected = self._number(spec["expected_value"])

            expected_unit = self._normalize(spec.get("unit", "persons"))
            factor = self.UNIT_FACTORS.get(expected_unit, 1)
            expected *= factor

        except (ValueError, TypeError):
            return {
                "classification": "UNCERTAIN",
                "reason": "Numerical value or unit could not be normalized."
            }

        if expected == 0:
            difference = 0.0 if actual == 0 else float("inf")
        else:
            difference = abs(actual - expected) / abs(expected)

        tolerance = float(spec.get("tolerance", 0.05))

        if difference <= tolerance:
            classification = "SUPPORTING"
            reason = "Numerical value is within the specified tolerance."
        else:
            classification = "CONTRADICTORY"
            reason = "Numerical value exceeds the specified tolerance."

        return {
            "classification": classification,
            "reason": reason,
            "actual_value_normalized": actual,
            "expected_value_normalized": expected,
            "relative_difference": round(difference, 6)
        }

    def verify(self, task: Dict, agent_output: Dict) -> Dict:
        spec = task.get("verification_spec")

        if not spec:
            raise ValueError("Task is missing verification_spec")

        evidence = agent_output.get("retrieved_evidence") or []

        if not isinstance(evidence, list):
            evidence = [evidence]

        scores = [
            {
                "evidence_index": index,
                **self._classify(item, spec)
            }
            for index, item in enumerate(evidence)
        ]

        counts = {
            label: sum(
                1 for item in scores
                if item["classification"] == label
            )
            for label in (
                "SUPPORTING",
                "IRRELEVANT",
                "CONTRADICTORY",
                "UNCERTAIN"
            )
        }

        support = counts["SUPPORTING"]
        irrelevant = counts["IRRELEVANT"]
        contradictory = counts["CONTRADICTORY"]
        uncertain = counts["UNCERTAIN"]

        if not evidence:
            overall = "NOT_ASSESSABLE"
        elif support and contradictory:
            overall = "MIXED"
        elif contradictory:
            overall = "CONTRADICTORY"
        elif support and (irrelevant or uncertain):
            overall = "PARTIALLY_SUPPORTED"
        elif support:
            overall = "SUPPORTING"
        elif irrelevant and not uncertain:
            overall = "IRRELEVANT"
        else:
            overall = "UNCERTAIN"

        assessable = support + irrelevant + contradictory

        return {
            "verifier_id": self.VERSION,
            "agent_id": agent_output.get("agent_id", "UNKNOWN"),
            "task_id": task.get("task_id"),
            "evidence_count": len(evidence),
            "evidence_presence": "present" if evidence else "absent",
            "claim_matching": overall,
            "individual_evidence_scores": scores,
            "relevant_evidence_count": support,
            "irrelevant_evidence_count": irrelevant,
            "contradictory_evidence_count": contradictory,
            "uncertain_evidence_count": uncertain,
            "evidence_relevance_ratio": (
                round(support / assessable, 3) if assessable else 0.0
            ),
            "verification_spec": spec,
            "source_verification": "not_performed",
            "verification_scope": (
                "explicit_entity_metric_year_and_numerical_comparison"
            )
        }
