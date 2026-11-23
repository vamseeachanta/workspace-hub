---
name: agenta-2-ab-testing-prompts
description: 'Sub-skill of agenta: 2. A/B Testing Prompts.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 2. A/B Testing Prompts

## 2. A/B Testing Prompts


**Setting Up A/B Tests:**
```python
"""
Configure and run A/B tests on prompt variations.
"""
import agenta as ag
from agenta import Agenta
from typing import Dict, List, Optional
from dataclasses import dataclass
import random

@dataclass
class ABTestConfig:
    """Configuration for A/B test."""
    name: str
    variants: Dict[str, float]  # variant_id: traffic_percentage
    metrics: List[str]
    min_samples: int = 100


class ABTestRunner:
    """
    Run A/B tests on prompt variants.
    """

    def __init__(self, app_name: str):
        self.app_name = app_name
        self.client = Agenta()
        self.results: Dict[str, List[Dict]] = {}

    def create_test(
        self,
        name: str,
        control_variant: str,
        treatment_variant: str,
        traffic_split: float = 0.5
    ) -> ABTestConfig:
        """
        Create an A/B test.

        Args:
            name: Test name
            control_variant: Control variant ID
            treatment_variant: Treatment variant ID
            traffic_split: Percentage for treatment (0-1)

        Returns:
            ABTestConfig
        """
        config = ABTestConfig(
            name=name,
            variants={
                control_variant: 1 - traffic_split,
                treatment_variant: traffic_split
            },
            metrics=["response_quality", "latency", "cost"]
        )

        # Initialize results tracking
        for variant in config.variants.keys():
            self.results[variant] = []

        return config

    def route_request(self, config: ABTestConfig) -> str:
        """
        Route a request to a variant based on traffic split.

        Args:
            config: A/B test configuration

        Returns:
            Selected variant ID
        """
        rand = random.random()
        cumulative = 0

        for variant_id, percentage in config.variants.items():
            cumulative += percentage
            if rand <= cumulative:
                return variant_id

        # Fallback to first variant
        return list(config.variants.keys())[0]

    def run_request(
        self,
        config: ABTestConfig,
        input_data: str
    ) -> Dict:
        """
        Run a single request in the A/B test.

        Args:
            config: A/B test configuration
            input_data: Input for the prompt

        Returns:
            Result dictionary with variant and output
        """
        import time

        # Route to variant
        variant_id = self.route_request(config)
        variant = self.client.get_variant(variant_id)

        # Prepare prompt
        prompt = variant.config.get("template", "").format(input=input_data)

        # Run with timing
        start_time = time.time()
        response = ag.llm.complete(prompt=prompt)
        latency = time.time() - start_time

        result = {
            "variant_id": variant_id,
            "input": input_data,
            "output": response.text,
            "latency": latency,
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
        }

        # Store result
        self.results[variant_id].append(result)

        return result

    def get_test_results(self, config: ABTestConfig) -> Dict:
        """
        Get aggregated results for an A/B test.

        Args:
            config: A/B test configuration

        Returns:
            Aggregated results by variant
        """
        summary = {}

        for variant_id, results in self.results.items():
            if not results:
                continue

            latencies = [r["latency"] for r in results]
            tokens = [r["tokens_used"] for r in results]

            summary[variant_id] = {
                "sample_count": len(results),
                "avg_latency": sum(latencies) / len(latencies),
                "avg_tokens": sum(tokens) / len(tokens) if tokens else 0,
                "min_latency": min(latencies),
                "max_latency": max(latencies)
            }

        return summary

    def declare_winner(self, config: ABTestConfig) -> Optional[str]:
        """
        Analyze results and declare a winner.

        Args:
            config: A/B test configuration

        Returns:
            Winner variant ID or None if inconclusive
        """
        summary = self.get_test_results(config)

        # Check minimum samples
        for variant_id, stats in summary.items():
            if stats["sample_count"] < config.min_samples:
                print(f"Insufficient samples for {variant_id}")
                return None

        # Simple winner selection based on latency
        # In production, use statistical significance tests
        best_variant = min(
            summary.keys(),
            key=lambda v: summary[v]["avg_latency"]
        )

        return best_variant



*Content truncated — see parent skill for full reference.*
