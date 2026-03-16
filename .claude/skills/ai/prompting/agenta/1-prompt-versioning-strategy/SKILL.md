---
name: agenta-1-prompt-versioning-strategy
description: 'Sub-skill of agenta: 1. Prompt Versioning Strategy (+2).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 1. Prompt Versioning Strategy (+2)

## 1. Prompt Versioning Strategy


```python
"""Best practices for prompt versioning."""

# DO: Use semantic versioning for prompts
version_naming = {
    "v1.0.0": "Initial production version",
    "v1.1.0": "Added context handling",
    "v1.1.1": "Fixed edge case in formatting",
    "v2.0.0": "Major rewrite with new approach"
}

# DO: Include metadata with versions
def create_versioned_prompt(name: str, template: str, metadata: dict):
    return {
        "name": name,
        "template": template,
        "metadata": {
            "created_by": metadata.get("author"),
            "description": metadata.get("description"),
            "changelog": metadata.get("changelog"),
            "test_results": metadata.get("test_results")
        }
    }

# DO: Test before promoting to production
def promote_to_production(variant_id: str, min_eval_score: float = 0.8):
    # Run evaluation
    score = run_evaluation(variant_id)

    if score >= min_eval_score:
        client.set_default_variant(variant_id)
        return True
    return False
```


## 2. Evaluation Strategy


```python
"""Best practices for prompt evaluation."""

# DO: Define clear evaluation criteria
evaluation_criteria = {
    "accuracy": {"weight": 0.4, "threshold": 0.8},
    "relevance": {"weight": 0.3, "threshold": 0.7},
    "coherence": {"weight": 0.2, "threshold": 0.7},
    "safety": {"weight": 0.1, "threshold": 0.9}
}

# DO: Use diverse test sets
def create_evaluation_set():
    return [
        {"input": "...", "expected": "...", "category": "basic"},
        {"input": "...", "expected": "...", "category": "edge_case"},
        {"input": "...", "expected": "...", "category": "adversarial"}
    ]

# DO: Track evaluation over time
def track_evaluation_history(app_name: str, variant_id: str, results: dict):
    # Store results with timestamp for trend analysis
    pass
```


## 3. A/B Testing Guidelines


```python
"""Best practices for A/B testing prompts."""

# DO: Calculate required sample size
def calculate_sample_size(
    baseline_metric: float,
    minimum_detectable_effect: float,
    alpha: float = 0.05,
    power: float = 0.8
) -> int:
    # Statistical calculation for required samples
    pass

# DO: Use proper statistical tests
def analyze_ab_test(control_results: list, treatment_results: list):
    from scipy import stats

    # T-test for continuous metrics
    t_stat, p_value = stats.ttest_ind(control_results, treatment_results)

    return {
        "significant": p_value < 0.05,
        "p_value": p_value,
        "effect_size": (sum(treatment_results)/len(treatment_results) -
                       sum(control_results)/len(control_results))
    }
```
