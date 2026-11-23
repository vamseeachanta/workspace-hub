---
name: dspy-optimization-not-improving
description: 'Sub-skill of dspy: Optimization Not Improving (+2).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# Optimization Not Improving (+2)

## Optimization Not Improving


```python
# Increase number of training examples
# Ensure diverse, high-quality examples
# Try different optimizer settings

optimizer = BootstrapFewShotWithRandomSearch(
    metric=metric,
    max_bootstrapped_demos=8,  # Increase
    num_candidate_programs=20,  # More search
    num_threads=8
)
```


## Module Too Slow


```python
# Use faster model for compilation
compile_lm = dspy.OpenAI(model="gpt-4.1-mini")
deploy_lm = dspy.OpenAI(model="gpt-4")

with dspy.settings.context(lm=compile_lm):
    optimized = optimizer.compile(module, trainset=data)

# Deploy with stronger model
dspy.settings.configure(lm=deploy_lm)
```


## Out of Memory


```python
# Process in batches
batch_size = 10
for i in range(0, len(trainset), batch_size):
    batch = trainset[i:i+batch_size]
    process_batch(batch)
```
