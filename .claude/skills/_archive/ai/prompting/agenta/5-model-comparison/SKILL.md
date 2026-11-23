---
name: agenta-5-model-comparison
description: 'Sub-skill of agenta: 5. Model Comparison.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 5. Model Comparison

## 5. Model Comparison


**Comparing Different LLM Models:**
```python
"""
Compare performance across different LLM models.
"""
import agenta as ag
from agenta import Agenta
from typing import Dict, List, Any
from dataclasses import dataclass
import time

@dataclass
class ModelResult:
    """Result from a single model run."""
    model: str
    output: str
    latency: float
    tokens: int
    cost: float


class ModelComparator:
    """
    Compare prompts across different models.
    """

    # Cost per 1K tokens (approximate)
    MODEL_COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4.1": {"input": 0.01, "output": 0.03},
        "gpt-4.1-mini": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
    }

    def __init__(self, models: List[str] = None):
        self.models = models or ["gpt-4", "gpt-4.1-mini"]
        self.results: Dict[str, List[ModelResult]] = {m: [] for m in self.models}

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a model run."""
        costs = self.MODEL_COSTS.get(model, {"input": 0.01, "output": 0.03})
        return (input_tokens / 1000 * costs["input"] +
                output_tokens / 1000 * costs["output"])

    def run_comparison(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 200
    ) -> Dict[str, ModelResult]:
        """
        Run the same prompt across all models.

        Args:
            prompt: Prompt to test
            temperature: Temperature setting
            max_tokens: Maximum output tokens

        Returns:
            Results for each model
        """
        results = {}

        for model in self.models:
            start_time = time.time()

            try:
                response = ag.llm.complete(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                latency = time.time() - start_time

                # Get token counts
                input_tokens = len(prompt.split()) * 1.3  # Rough estimate
                output_tokens = len(response.text.split()) * 1.3

                if hasattr(response, 'usage'):
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens

                result = ModelResult(
                    model=model,
                    output=response.text,
                    latency=latency,
                    tokens=int(input_tokens + output_tokens),
                    cost=self._estimate_cost(model, input_tokens, output_tokens)
                )

            except Exception as e:
                result = ModelResult(
                    model=model,
                    output=f"Error: {str(e)}",
                    latency=0,
                    tokens=0,
                    cost=0
                )

            results[model] = result
            self.results[model].append(result)

        return results

    def run_benchmark(
        self,
        prompts: List[str],
        temperature: float = 0.3
    ) -> Dict[str, Dict]:
        """
        Run benchmark across multiple prompts.

        Args:
            prompts: List of prompts to test
            temperature: Temperature setting

        Returns:
            Aggregated benchmark results
        """
        for prompt in prompts:
            self.run_comparison(prompt, temperature)

        return self.get_summary()

    def get_summary(self) -> Dict[str, Dict]:
        """Get summary statistics for all models."""
        summary = {}

        for model, results in self.results.items():
            if not results:
                continue

            valid_results = [r for r in results if r.latency > 0]

            if not valid_results:
                continue

            summary[model] = {
                "runs": len(valid_results),
                "avg_latency": sum(r.latency for r in valid_results) / len(valid_results),
                "avg_tokens": sum(r.tokens for r in valid_results) / len(valid_results),
                "total_cost": sum(r.cost for r in valid_results),
                "min_latency": min(r.latency for r in valid_results),
                "max_latency": max(r.latency for r in valid_results)
            }

        return summary

    def recommend_model(
        self,
        priority: str = "balanced"
    ) -> str:
        """
        Recommend best model based on priority.

        Args:
            priority: "speed", "cost", "quality", or "balanced"

        Returns:
            Recommended model name
        """
        summary = self.get_summary()

        if not summary:
            return self.models[0]

        if priority == "speed":
            return min(summary.keys(), key=lambda m: summary[m]["avg_latency"])
        elif priority == "cost":
            return min(summary.keys(), key=lambda m: summary[m]["total_cost"])
        elif priority == "quality":
            # Assume larger models = better quality
            quality_order = ["gpt-4", "claude-3-opus", "gpt-4.1", "claude-3-sonnet", "gpt-4.1-mini"]
            for model in quality_order:
                if model in summary:
                    return model
        else:  # balanced
            # Score based on normalized latency and cost
            scores = {}
            max_latency = max(s["avg_latency"] for s in summary.values())

*Content truncated — see parent skill for full reference.*
