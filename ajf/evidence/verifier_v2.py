"""AJF Evidence Verifier V2: deterministic evidence classification."""

import re
from typing import Dict, Any, List


class EvidenceVerifierV2:
    VERSION = "AJF-EVIDENCE-VERIFIER-002"
    NUMERICAL_TOLERANCE = 0.05

    METRICS = {
        "population": ("population", "pop"),
        "gdp": ("gdp", "gross domestic product"),
        "water": ("water", "freshwater"),
    }

    MULTIPLIERS = {
        "million": 1_000_000,
        "billion": 1_000_000_000,
        "thousand": 1_000,
        "m": 1_000_000,
        "bn": 1_000_000_000,
    }

    def _metric(self, text: str):
        text = text.lower()
        for metric, terms in self.METRICS.items():
            if any(term in text for term in terms):
                return metric
        return None

    def _year(self, text: str):
        match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        return int(match.group(1)) if match else None

    def _number(self, text: str):
        pattern = (
            r"(?<![A-Za-z])"
            r"(\d+(?:,\d{3})*(?:\.\d+)?)"
            r"\s*(million|billion|thousand|bn|m)?\b"
        )

        matches = re.findall(pattern, text.lower())

        for number, unit in matches:
            value = float(number.replace(",", ""))

            # Ignore calendar years.
            if not unit and 1900 <= value <= 2100:
                continue

            value *= self.MULTIPLIERS.get(unit, 1)
            return value

        return None

    def _classify(
        self,
        expected_text: str,
        evidence_text: str,
        expected_metric: str,
        expected_year
    ) -> Dict[str, Any]:

        evidence_metric = self._metric(evidence_text)
        evidence_year = self._year(evidence_text)

        if evidence_metric and evidence_metric != expected_metric:
            return {
                "classification": "IRRELEVANT",
                "reason": "Different subject metric."
            }

        if evidence_year and expected_year and evidence_year != expected_year:
            return {
                "classification": "IRRELEVANT",
                "reason": "Different reporting year."
            }

        if evidence_metric is None:
            return {
                "classification": "UNCERTAIN",
                "reason": "Evidence metric cannot be identified."
            }

        expected_value = self._number(expected_text)
        evidence_value = self._number(evidence_text)

        if expected_value is None or evidence_value is None:
            return {
                "classification": "UNCERTAIN",
                "reason": "Numerical comparison unavailable."
            }

        if expected_value == 0:
            return {
                "classification": "UNCERTAIN",
                "reason": "Invalid expected numerical baseline."
            }

        relative_difference = abs(
            evidence_value - expected_value
        ) / abs(expected_value)

        if relative_difference <= self.NUMERICAL_TOLERANCE:
            return {
                "classification": "SUPPORTING",
                "reason": "Numerical value is within tolerance.",
                "relative_difference": round(relative_difference, 4)
            }

        return {
            "classification": "CONTRADICTORY",
            "reason": "Numerical value exceeds tolerance.",
            "relative_difference": round(relative_difference, 4)
        }

    def verify(
        self,
        task: Dict[str, Any],
        agent_output: Dict[str, Any]
    ) -> Dict[str, Any]:

        raw = agent_output.get("retrieved_evidence", [])

        if isinstance(raw, list):
            evidence = [
                str(item).strip()
                for item in raw
                if item is not None and str(item).strip()
            ]
        elif raw is not None and str(raw).strip():
            evidence = [str(raw).strip()]
        else:
            evidence = []

        expected = str(task.get("expected_outcome", ""))
        description = str(task.get("description", ""))

        expected_metric = (
            self._metric(expected) or self._metric(description)
        )
        expected_year = self._year(expected) or self._year(description)

        if not evidence:
            classifications = []
            aggregate = "NOT_ASSESSABLE"
        elif expected_metric is None:
            classifications = [
                {
                    "evidence_index": i,
                    "classification": "UNCERTAIN",
                    "reason": "Task metric cannot be identified."
                }
                for i, _ in enumerate(evidence)
            ]
            aggregate = "UNCERTAIN"
        else:
            classifications = []

            for index, item in enumerate(evidence):
                result = self._classify(
                    expected,
                    item,
                    expected_metric,
                    expected_year
                )
                result["evidence_index"] = index
                classifications.append(result)

            labels = [
                item["classification"] for item in classifications
            ]

            supporting = labels.count("SUPPORTING")
            contradictory = labels.count("CONTRADICTORY")
            irrelevant = labels.count("IRRELEVANT")
            uncertain = labels.count("UNCERTAIN")

            if supporting and contradictory:
                aggregate = "MIXED"
            elif contradictory:
                aggregate = "CONTRADICTORY"
            elif supporting:
                aggregate = (
                    "PARTIALLY_SUPPORTED"
                    if irrelevant or uncertain
                    else "SUPPORTING"
                )
            elif irrelevant and not uncertain:
                aggregate = "IRRELEVANT"
            else:
                aggregate = "UNCERTAIN"

        count = len(evidence)
        relevant_count = sum(
            x["classification"] == "SUPPORTING"
            for x in classifications
        )

        tool_calls = agent_output.get("tool_calls", [])

        return {
            "verifier_id": self.VERSION,
            "agent_id": agent_output.get("agent_id", "UNKNOWN"),
            "task_id": task.get("task_id", "UNKNOWN"),
            "evidence_count": count,
            "evidence_presence": "present" if count else "absent",
            "claim_matching": aggregate,
            "individual_evidence_scores": classifications,
            "relevant_evidence_count": relevant_count,
            "irrelevant_evidence_count": sum(
                x["classification"] == "IRRELEVANT"
                for x in classifications
            ),
            "contradictory_evidence_count": sum(
                x["classification"] == "CONTRADICTORY"
                for x in classifications
            ),
            "uncertain_evidence_count": sum(
                x["classification"] == "UNCERTAIN"
                for x in classifications
            ),
            "evidence_relevance_ratio": (
                round(relevant_count / count, 3) if count else 0.0
            ),
            "source_metadata": (
                "partial"
                if task.get("reference_source") and tool_calls
                else "incomplete"
            ),
            "reference_source": task.get("reference_source"),
            "tool_trace_available": bool(tool_calls),
            "source_verification": "not_performed",
            "verification_scope": (
                "deterministic_metric_and_numerical_comparison"
            )
        }
