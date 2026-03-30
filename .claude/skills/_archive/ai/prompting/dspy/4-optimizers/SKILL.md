---
name: dspy-4-optimizers
description: 'Sub-skill of dspy: 4. Optimizers.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 4. Optimizers

## 4. Optimizers


**BootstrapFewShot Optimizer:**
```python
from dspy.teleprompt import BootstrapFewShot

class ClassifyReport(dspy.Signature):
    """Classify engineering report type."""
    report_text = dspy.InputField()
    report_type = dspy.OutputField(
        desc="Type: analysis, inspection, design, or incident"
    )

class ReportClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.classify = dspy.Predict(ClassifyReport)

    def forward(self, report_text):
        return self.classify(report_text=report_text)

# Create training data
trainset = [
    dspy.Example(
        report_text="The mooring analysis shows maximum tensions...",
        report_type="analysis"
    ).with_inputs("report_text"),
    dspy.Example(
        report_text="Visual inspection of Line 3 revealed corrosion...",
        report_type="inspection"
    ).with_inputs("report_text"),
    dspy.Example(
        report_text="The new platform design incorporates...",
        report_type="design"
    ).with_inputs("report_text"),
    dspy.Example(
        report_text="At 14:32, the vessel experienced sudden offset...",
        report_type="incident"
    ).with_inputs("report_text"),
    # Add more examples...
]

# Define metric
def classification_accuracy(example, prediction, trace=None):
    return example.report_type.lower() == prediction.report_type.lower()

# Optimize
optimizer = BootstrapFewShot(
    metric=classification_accuracy,
    max_bootstrapped_demos=4,
    max_labeled_demos=8
)

# Compile optimized module
optimized_classifier = optimizer.compile(
    ReportClassifier(),
    trainset=trainset
)

# Use optimized classifier
result = optimized_classifier(
    report_text="Fatigue analysis indicates remaining life of 15 years..."
)
print(f"Type: {result.report_type}")
```

**BootstrapFewShotWithRandomSearch:**
```python
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

# More thorough optimization with search
optimizer = BootstrapFewShotWithRandomSearch(
    metric=classification_accuracy,
    max_bootstrapped_demos=4,
    max_labeled_demos=8,
    num_candidate_programs=10,
    num_threads=4
)

# This searches for the best combination of examples
optimized = optimizer.compile(
    ReportClassifier(),
    trainset=trainset,
    valset=valset  # Optional validation set
)
```

**MIPRO Optimizer (Advanced):**
```python
from dspy.teleprompt import MIPRO

class ComplexQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.qa = dspy.ChainOfThought("context, question -> answer")

    def forward(self, context, question):
        return self.qa(context=context, question=question)

# MIPRO optimizes both instructions and examples
optimizer = MIPRO(
    metric=answer_quality_metric,
    prompt_model=dspy.OpenAI(model="gpt-4"),
    task_model=dspy.OpenAI(model="gpt-4.1-mini"),
    num_candidates=10,
    init_temperature=1.0
)

optimized_qa = optimizer.compile(
    ComplexQA(),
    trainset=trainset,
    num_batches=5,
    max_bootstrapped_demos=3,
    max_labeled_demos=5,
    eval_kwargs={"num_threads": 4}
)
```
