---
name: dspy-5-evaluation-and-metrics
description: 'Sub-skill of dspy: 5. Evaluation and Metrics (+1).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 5. Evaluation and Metrics (+1)

## 5. Evaluation and Metrics


**Custom Metrics:**
```python
import dspy
from typing import Optional

def answer_correctness(
    example: dspy.Example,
    prediction: dspy.Prediction,
    trace: Optional[list] = None
) -> float:
    """
    Evaluate answer correctness.

    Args:
        example: Ground truth example
        prediction: Model prediction
        trace: Optional execution trace

    Returns:
        Score between 0 and 1
    """
    # Exact match
    if example.answer.lower().strip() == prediction.answer.lower().strip():
        return 1.0

    # Partial match using overlap
    expected_words = set(example.answer.lower().split())
    predicted_words = set(prediction.answer.lower().split())

    if not expected_words:
        return 0.0

    overlap = len(expected_words & predicted_words)
    return overlap / len(expected_words)

def answer_relevance(
    example: dspy.Example,
    prediction: dspy.Prediction,
    trace: Optional[list] = None
) -> float:
    """Evaluate answer relevance using an LLM judge."""

    judge = dspy.Predict("question, answer -> relevance_score")

    result = judge(
        question=example.question,
        answer=prediction.answer
    )

    try:
        score = float(result.relevance_score)
        return min(max(score, 0.0), 1.0)
    except ValueError:
        return 0.5

def combined_metric(example, prediction, trace=None) -> float:
    """Combined metric with multiple factors."""
    correctness = answer_correctness(example, prediction, trace)
    relevance = answer_relevance(example, prediction, trace)

    # Weighted combination
    return 0.6 * correctness + 0.4 * relevance
```

**Systematic Evaluation:**
```python
from dspy.evaluate import Evaluate

def evaluate_module(module, testset, metric, num_threads=4):
    """
    Systematically evaluate a module on a test set.
    """
    evaluator = Evaluate(
        devset=testset,
        metric=metric,
        num_threads=num_threads,
        display_progress=True,
        display_table=5  # Show top 5 examples
    )

    score = evaluator(module)

    print(f"\nOverall Score: {score:.2%}")

    return score

# Usage
testset = [
    dspy.Example(
        question="What is the minimum safety factor?",
        context="API RP 2SK requires SF >= 1.67 for intact...",
        answer="1.67 for intact conditions"
    ).with_inputs("question", "context"),
    # More test cases...
]

score = evaluate_module(
    module=optimized_qa,
    testset=testset,
    metric=answer_correctness
)
```


## 6. Saving and Loading


**Save Optimized Modules:**
```python
import json
from pathlib import Path

def save_module(module, path: str):
    """Save an optimized DSPy module."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    module.save(path)
    print(f"Module saved to {path}")

def load_module(module_class, path: str):
    """Load a saved DSPy module."""
    module = module_class()
    module.load(path)
    print(f"Module loaded from {path}")
    return module

# Save
save_module(optimized_classifier, "models/report_classifier.json")

# Load
loaded_classifier = load_module(ReportClassifier, "models/report_classifier.json")

# Verify
result = loaded_classifier(report_text="Test report...")
print(result.report_type)
```
