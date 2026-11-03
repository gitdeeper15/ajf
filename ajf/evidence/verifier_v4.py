import re
from typing import Any, Dict


class EvidenceVerifierV4:
    VERSION = "AJF-EVIDENCE-VERIFIER-004"

    FACTORS = {
        "person": 1,
        "persons": 1,
        "people": 1,
        "million": 1_000_000,
        "millions": 1_000_000,
        "billion": 1_000_000_000,
        "billions": 1_000_000_000,
        "thousand": 1_000,
        "thousands": 1_000,
        "m": 1_000_000,
        "bn": 1_000_000_000,
    }

    def _normalize(self, value: Any) -> str:
        return re.sub(r"\s+", " ", str(value).lower()).strip()

    def _parse_quantity(self, value: Any, unit=None) -> float:
        if isinstance(value, (int, float)):
            number = float(value)
        else:
            text = str(value).lower().replace(",", "").strip()
            match = re.search(r"[-+]?\d+(?:\.\d+)?", text)

            if not match:
                raise ValueError("No numerical value found")

            number = float(match.group())

            suffix = text[match.end():].strip()
            unit_match = re.match(
                r"(million|millions|billion|billions|"
                r"thousand|thousands|persons|person|people|m|bn)\b",
                suffix
            )

            if unit_match:
                unit = unit_match.group(1)

        if unit:
            factor = self.FACTORS.get(self._normalize(unit))
            if factor is None:
                raise ValueError("Unsupported unit")
            number *= factor

        return number

    def _find_year(self, text):
        matches = list(re.finditer(r"\b(19\d{2}|20\d{2})\b", text))
        return matches

    def _extract_text_value(self, text, metric):
        # Remove years before searching for numerical values.
        year_matches = self._find_year(text)
        year = int(year_matches[0].group()) if len(year_matches) == 1 else None

        cleaned = text
        for match in reversed(year_matches):
            cleaned = cleaned[:match.start()] + (
                " " * (match.end() - match.start())
            ) + cleaned[match.end():]

        number_pattern = re.compile(
            r"(?<![A-Za-z0-9])"
            r"[-+]?\d[\d,]*(?:\.\d+)?"
            r"(?:\s*(?:million|millions|billion|billions|"
            r"thousand|thousands|bn|m)\b)?",
            re.IGNORECASE
        )

        candidates = []

        for match in number_pattern.finditer(cleaned):
            raw = match.group().strip()

            try:
                value = self._parse_quantity(raw)
            except ValueError:
                continue

            candidates.append({
                "value": value,
                "raw_value": raw,
                "position": match.start()
            })

        if not candidates:
            return year, None, None

        metric_match = re.search(
            r"\b" + re.escape(metric) + r"\b",
            cleaned
        )

        if not metric_match:
            return year, None, None

        # Prefer the first numerical candidate following the metric.
        after_metric = [
            item for item in candidates
            if item["position"] >= metric_match.end()
        ]

        if len(after_metric) == 1:
            selected = after_metric[0]
        elif len(after_metric) > 1:
            return year, None, "Multiple numerical candidates"
        elif len(candidates) == 1:
            selected = candidates[0]
        else:
            return year, None, "Ambiguous numerical candidates"

        return year, selected["value"], selected["raw_value"]

    def _classify(self, evidence, spec):
        expected_entity = self._normalize(spec["entity"])
        expected_metric = self._normalize(spec["metric"])
        expected_year = int(spec["year"])

        if isinstance(evidence, dict):
            text = self._normalize(evidence.get("text", ""))
            entity = evidence.get("entity")
            metric = evidence.get("metric")
            year = evidence.get("year")
            value = evidence.get("value")
            unit = evidence.get("unit")
            raw_value = value
        else:
            text = self._normalize(evidence)
            entity = None
            metric = None
            unit = None

            if expected_entity in text:
                entity = expected_entity

            if re.search(
                r"\b" + re.escape(expected_metric) + r"\b", text
            ):
                metric = expected_metric

            year, value, raw_value = self._extract_text_value(
                text, expected_metric
            )

        if entity is None or metric is None:
            return {
                "classification": "UNCERTAIN",
                "reason": "Entity or metric could not be identified."
            }

        if self._normalize(entity) != expected_entity:
            return {
                "classification": "IRRELEVANT",
                "reason": "Different entity."
            }

        if self._normalize(metric) != expected_metric:
            return {
                "classification": "IRRELEVANT",
                "reason": "Different metric."
            }

        if year is None:
            return {
                "classification": "UNCERTAIN",
                "reason": "Year could not be identified."
            }

        if int(year) != expected_year:
            return {
                "classification": "IRRELEVANT",
                "reason": "Different year."
            }

        if value is None:
            return {
                "classification": "UNCERTAIN",
                "reason": "Numerical value could not be identified."
            }

        try:
            actual = self._parse_quantity(value, unit)
            expected = self._parse_quantity(
                spec["expected_value"],
                spec.get("unit", "persons")
            )
        except (ValueError, TypeError):
            return {
                "classification": "UNCERTAIN",
                "reason": "Numerical value or unit could not be normalized."
            }

        difference = (
            abs(actual - expected) / abs(expected)
            if expected != 0
            else (0.0 if actual == 0 else float("inf"))
        )

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
            "raw_value": raw_value,
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
                "entity_metric_year_and_contextual_numerical_comparison"
            )
        }
