---
name: dspy-1-start-simple-then-optimize
description: 'Sub-skill of dspy: 1. Start Simple, Then Optimize (+2).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 1. Start Simple, Then Optimize (+2)

## 1. Start Simple, Then Optimize


```python
# 1. Start with basic Predict
basic = dspy.Predict("question -> answer")

# 2. Add ChainOfThought if needed
cot = dspy.ChainOfThought("question -> answer")

# 3. Optimize only after baseline is established
optimized = optimizer.compile(cot, trainset=data)
```


## 2. Quality Training Data


```python
def create_training_example(question, answer, inputs=["question"]):
    """Create well-formed training example."""
    example = dspy.Example(
        question=question,
        answer=answer
    )
    return example.with_inputs(*inputs)

# Include diverse examples
trainset = [
    create_training_example("Simple question?", "Simple answer"),
    create_training_example("Complex technical question?", "Detailed answer..."),
    create_training_example("Edge case question?", "Careful handling..."),
]
```


## 3. Meaningful Metrics


```python
def comprehensive_metric(example, prediction, trace=None):
    """Combine multiple evaluation dimensions."""
    scores = {
        "correctness": check_correctness(example, prediction),
        "completeness": check_completeness(prediction),
        "format": check_format(prediction),
        "citations": check_citations(prediction)
    }

    weights = {"correctness": 0.4, "completeness": 0.3, "format": 0.15, "citations": 0.15}

    return sum(scores[k] * weights[k] for k in scores)
```
