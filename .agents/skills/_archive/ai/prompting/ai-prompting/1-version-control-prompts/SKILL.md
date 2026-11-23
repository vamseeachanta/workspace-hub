---
name: ai-prompting-1-version-control-prompts
description: 'Sub-skill of ai-prompting: 1. Version Control Prompts (+3).'
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# 1. Version Control Prompts (+3)

## 1. Version Control Prompts

```yaml
# prompts/summarize_v2.yaml
version: 2.0.0
model: gpt-4
temperature: 0.3
template: |
  Summarize the following text...
metrics:
  avg_quality: 0.87
  latency_p95: 2.3s
```


## 2. Evaluation-Driven Development

```python
def evaluate_prompt(prompt_template, test_cases):
    results = []
    for case in test_cases:
        output = generate(prompt_template.format(**case.input))
        score = evaluate_output(output, case.expected)
        results.append(score)
    return {
        "mean": sum(results) / len(results),
        "min": min(results),
        "failed_cases": [c for c, s in zip(test_cases, results) if s < 0.7]
    }
```


## 3. Cost Monitoring

```python
class CostTracker:
    def __init__(self, budget_limit=100.0):
        self.total_cost = 0
        self.budget_limit = budget_limit

    def track(self, tokens_in, tokens_out, model):
        cost = calculate_cost(tokens_in, tokens_out, model)
        self.total_cost += cost
        if self.total_cost > self.budget_limit * 0.8:
            logger.warning(f"Approaching budget limit: ${self.total_cost:.2f}")
```


## 4. Graceful Degradation

```python
def get_response(query, context):
    try:
        return advanced_rag_pipeline(query, context)
    except ModelOverloadError:
        return simpler_model_fallback(query, context)
    except Exception:
        return cached_similar_response(query)
```
