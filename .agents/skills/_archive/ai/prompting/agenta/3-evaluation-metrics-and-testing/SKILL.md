---
name: agenta-3-evaluation-metrics-and-testing
description: 'Sub-skill of agenta: 3. Evaluation Metrics and Testing.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 3. Evaluation Metrics and Testing

## 3. Evaluation Metrics and Testing


**Automated Evaluation Pipeline:**
```python
"""
Evaluate prompts with automated metrics.
"""
import agenta as ag
from agenta import Agenta
from typing import List, Dict, Callable, Any
from dataclasses import dataclass
import json

@dataclass
class EvaluationResult:
    """Result of an evaluation."""
    metric_name: str
    score: float
    details: Dict[str, Any]


class MetricEvaluator:
    """Base class for evaluation metrics."""

    def __init__(self, name: str):
        self.name = name

    def evaluate(
        self,
        output: str,
        expected: str = None,
        context: Dict = None
    ) -> EvaluationResult:
        raise NotImplementedError


class ExactMatchMetric(MetricEvaluator):
    """Exact match evaluation."""

    def __init__(self):
        super().__init__("exact_match")

    def evaluate(self, output: str, expected: str = None, context: Dict = None) -> EvaluationResult:
        if expected is None:
            return EvaluationResult(self.name, 0.0, {"error": "No expected value"})

        match = output.strip().lower() == expected.strip().lower()

        return EvaluationResult(
            metric_name=self.name,
            score=1.0 if match else 0.0,
            details={"match": match}
        )


class ContainsMetric(MetricEvaluator):
    """Check if output contains expected keywords."""

    def __init__(self, keywords: List[str]):
        super().__init__("contains_keywords")
        self.keywords = keywords

    def evaluate(self, output: str, expected: str = None, context: Dict = None) -> EvaluationResult:
        output_lower = output.lower()
        found = [kw for kw in self.keywords if kw.lower() in output_lower]
        score = len(found) / len(self.keywords)

        return EvaluationResult(
            metric_name=self.name,
            score=score,
            details={
                "found_keywords": found,
                "missing_keywords": [kw for kw in self.keywords if kw.lower() not in output_lower]
            }
        )


class LengthMetric(MetricEvaluator):
    """Evaluate output length."""

    def __init__(self, min_length: int = 10, max_length: int = 500):
        super().__init__("length")
        self.min_length = min_length
        self.max_length = max_length

    def evaluate(self, output: str, expected: str = None, context: Dict = None) -> EvaluationResult:
        length = len(output.split())

        if self.min_length <= length <= self.max_length:
            score = 1.0
        elif length < self.min_length:
            score = length / self.min_length
        else:
            score = max(0, 1 - (length - self.max_length) / self.max_length)

        return EvaluationResult(
            metric_name=self.name,
            score=score,
            details={
                "word_count": length,
                "min_length": self.min_length,
                "max_length": self.max_length
            }
        )


class LLMJudgeMetric(MetricEvaluator):
    """Use an LLM to judge output quality."""

    def __init__(self, criteria: str = "helpfulness"):
        super().__init__(f"llm_judge_{criteria}")
        self.criteria = criteria

    def evaluate(self, output: str, expected: str = None, context: Dict = None) -> EvaluationResult:
        judge_prompt = f"""Evaluate the following response on {self.criteria}.
Score from 0.0 to 1.0.

Response:
{output}

{f'Expected: {expected}' if expected else ''}

Provide your evaluation as JSON: {{"score": 0.0-1.0, "reasoning": "..."}}
"""

        response = ag.llm.complete(
            prompt=judge_prompt,
            model="gpt-4",
            temperature=0
        )

        try:
            result = json.loads(response.text)
            score = float(result.get("score", 0.5))
            reasoning = result.get("reasoning", "")
        except (json.JSONDecodeError, ValueError):
            score = 0.5
            reasoning = "Failed to parse judge response"

        return EvaluationResult(
            metric_name=self.name,
            score=score,
            details={"reasoning": reasoning, "criteria": self.criteria}
        )


class EvaluationPipeline:
    """
    Pipeline for running multiple evaluations.
    """

    def __init__(self, app_name: str):
        self.app_name = app_name
        self.client = Agenta()
        self.metrics: List[MetricEvaluator] = []

    def add_metric(self, metric: MetricEvaluator) -> 'EvaluationPipeline':
        """Add a metric to the pipeline."""
        self.metrics.append(metric)
        return self

    def evaluate_single(
        self,
        output: str,
        expected: str = None,
        context: Dict = None
    ) -> Dict[str, EvaluationResult]:
        """
        Evaluate a single output with all metrics.

        Args:
            output: Generated output
            expected: Expected output (optional)
            context: Additional context

        Returns:
            Dictionary of metric results
        """
        results = {}

        for metric in self.metrics:
            result = metric.evaluate(output, expected, context)
            results[metric.name] = result

        return results


*Content truncated — see parent skill for full reference.*
