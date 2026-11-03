import re
from typing import Any, Dict


class EvidenceVerifierV5:
    VERSION = "AJF-EVIDENCE-VERIFIER-005"

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

    def _contains(self, text: str, term: str) -> bool:
        pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
        return re.search(pattern, text) is not None

    def _detect(self, text, terms):
        matches = []

        for canonical, aliases in terms.items():
            candidates = [canonical] + list(aliases)

            if any(self._contains(text, self._normalize(x))
                   for x in candidates):
                matches.append(canonical)

        return matches

    def _parse_quantity(self, value, unit=None):
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

    def _extract_year(self, text):
        matches = list(
            re.finditer(r"\b(19\d{2}|20\d{2})\b", text)
        )

        if len(matches) == 1:
            return int(matches[0].group())

        return None

    def _extract_value(self, text, metric):
        year_matches = list(
            re.finditer(r"\b(19\d{2}|20\d{2})\b", text)
        )

        cleaned = text

        for match in reversed(year_matches):
            cleaned = (
                cleaned[:match.start()]
                + " " * (match.end() - match.start())
                + cleaned[match.end():]
            )

        pattern = re.compile(
            r"(?<![A-Za-z0-9])"
            r"[-+]?\d[\d,]*(?:\.\d+)?"
            r"(?:\s*(?:million|millions|billion|billions|"
            r"thousand|thousands|bn|m)\b)?",
            re.IGNORECASE
        )

        candidates = []

        for match in pattern.finditer(cleaned):
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
            return None, None

        metric_match = re.search(
            r"(?<!\w)" + re.escape(metric) + r"(?!\w)",
            cleaned
        )

        if not metric_match:
            return None, None

        after_metric = [
            item for item in candidates
            if item["position"] >= metric_match.end()
        ]

        if len(after_metric) == 1:
            selected = after_metric[0]
        elif len(after_metric) > 1:
            return None, "Multiple numerical candidates"
        elif len(candidates) == 1:
            selected = candidates[0]
        else:
            return None, "Ambiguous numerical candidates"

        return selected["value"], selected["raw_value"]

    def _classify(self, evidence, spec):
        if isinstance(evidence, dict):
            text = self._normalize(evidence.get("text", ""))
            explicit_entity = evidence.get("entity")
            explicit_metric = evidence.get("metric")
            year = evidence.get("year")
            value = evidence.get("value")
            unit = evidence.get("unit")
            raw_value = value
        else:
            text = self._normalize(evidence)
            explicit_entity = None
            explicit_metric = None
            year = self._extract_year(text)
            value = None
            unit = None
            raw_value = None

        entity_terms = spec.get("known_entities", {})
        metric_terms = spec.get("known_metrics", {})

        detected_entities = self._detect(text, entity_terms)
        detected_metrics = self._detect(text, metric_terms)

        if explicit_entity is not None:
            detected_entities = [self._normalize(explicit_entity)]

        if explicit_metric is not None:
            detected_metrics = [self._normalize(explicit_metric)]

        expected_entity = self._normalize(spec["entity"])
        expected_metric = self._normalize(spec["metric"])

        if not detected_entities:
            return {
                "classification": "UNCERTAIN",
                "reason": "Entity could not be identified."
            }

        if expected_entity not in [
            self._normalize(x) for x in detected_entities
        ]:
            return {
                "classification": "IRRELEVANT",
                "reason": "Different entity.",
                "detected_entities": detected_entities
            }

        if not detected_metrics:
            return {
                "classification": "UNCERTAIN",
                "reason": "Metric could not be identified."
            }

        if expected_metric not in [
            self._normalize(x) for x in detected_metrics
        ]:
            return {
                "classification": "IRRELEVANT",
                "reason": "Different metric.",
                "detected_metrics": detected_metrics
            }

        if year is None:
            return {
                "classification": "UNCERTAIN",
                "reason": "Year could not be identified."
            }

        if int(year) != int(spec["year"]):
            return {
                "classification": "IRRELEVANT",
                "reason": "Different year."
            }

        if value is None:
            value, raw_value = self._extract_value(
                text, expected_metric
            )

        if value is None:
            return {
                "classification": "UNCERTAIN",
                "reason": (
                    raw_value if isinstance(raw_value, str)
                    else "Numerical value could not be identified."
                )
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
            "raw_value": raw_value if raw_value is not None else value,
            "actual_value_normalized": actual,
            "expected_value_normalized": expected,
            "relative_difference": round(difference, 6),
            "detected_entities": detected_entities,
            "detected_metrics": detected_metrics,
            "detected_year": year
        }

    def verify(self, task: Dict, agent_output: Dict) -> Dict:
        spec = task.get("verification_spec")

        if not spec:
            raise ValueError("Task is missing verification_spec")

        for field in (
            "entity", "metric", "year", "expected_value",
            "known_entities", "known_metrics"
        ):
            if field not in spec:
                raise ValueError(
                    "verification_spec missing field: " + field
                )

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

        labels = (
            "SUPPORTING",
            "IRRELEVANT",
            "CONTRADICTORY",
            "UNCERTAIN"
        )

        counts = {
            label: sum(
                1 for item in scores
                if item["classification"] == label
            )
            for label in labels
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
                "known_entity_metric_year_and_contextual_numerical_comparison"
            )
        }
