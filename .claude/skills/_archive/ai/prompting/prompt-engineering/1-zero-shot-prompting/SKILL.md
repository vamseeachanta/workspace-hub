---
name: prompt-engineering-1-zero-shot-prompting
description: 'Sub-skill of prompt-engineering: 1. Zero-Shot Prompting (+1).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 1. Zero-Shot Prompting (+1)

## 1. Zero-Shot Prompting


**Basic Zero-Shot:**
```python
def zero_shot_prompt(task: str, input_text: str) -> str:
    """
    Zero-shot prompting: Direct instruction without examples.
    Best for simple, well-defined tasks.
    """
    prompt = f"""
Task: {task}

Input: {input_text}

Output:
"""
    return prompt

# Usage
prompt = zero_shot_prompt(
    task="Classify this text as positive, negative, or neutral",
    input_text="The mooring analysis passed all safety requirements."
)
# Output: positive
```

**Zero-Shot with Role:**
```python
def zero_shot_with_role(role: str, task: str, input_text: str) -> str:
    """
    Zero-shot with explicit role definition.
    """
    system = f"You are a {role}. You provide expert analysis."

    user = f"""
{task}

{input_text}
"""
    return system, user

# Usage
system, user = zero_shot_with_role(
    role="senior offshore engineer with 20 years experience",
    task="Review this mooring design and identify any concerns:",
    input_text="8-line spread mooring in 150m water depth..."
)
```

**Zero-Shot Classification:**
```python
CLASSIFICATION_TEMPLATE = """
Classify the following engineering report into one of these categories:
- ANALYSIS: Technical analysis or simulation results
- INSPECTION: Field inspection or survey findings
- DESIGN: Design specifications or requirements
- INCIDENT: Incident reports or failure analysis
- MAINTENANCE: Maintenance records or procedures

Report:
{report_text}

Category:
"""

def classify_report(report_text: str) -> str:
    prompt = CLASSIFICATION_TEMPLATE.format(report_text=report_text)
    # Send to LLM
    return prompt
```


## 2. Few-Shot Prompting


**Basic Few-Shot:**
```python
def few_shot_prompt(
    task_description: str,
    examples: list,
    input_text: str
) -> str:
    """
    Few-shot prompting with examples.
    Generally 2-5 examples work best.
    """
    prompt = f"{task_description}\n\n"

    # Add examples
    for i, ex in enumerate(examples, 1):
        prompt += f"Example {i}:\n"
        prompt += f"Input: {ex['input']}\n"
        prompt += f"Output: {ex['output']}\n\n"

    # Add actual input
    prompt += f"Now process this:\n"
    prompt += f"Input: {input_text}\n"
    prompt += f"Output:"

    return prompt

# Usage
examples = [
    {
        "input": "Tension: 2500 kN, Limit: 2800 kN",
        "output": "PASS - Tension is 89% of limit, within acceptable range."
    },
    {
        "input": "Tension: 3100 kN, Limit: 2800 kN",
        "output": "FAIL - Tension exceeds limit by 11%. Redesign required."
    },
    {
        "input": "Tension: 2750 kN, Limit: 2800 kN",
        "output": "WARNING - Tension is 98% of limit, minimal margin."
    }
]

prompt = few_shot_prompt(
    task_description="Evaluate mooring line tension against limits.",
    examples=examples,
    input_text="Tension: 2200 kN, Limit: 2800 kN"
)
```

**Few-Shot with Diverse Examples:**
```python
def create_balanced_few_shot(examples_by_category: dict, input_text: str) -> str:
    """
    Create few-shot prompt with balanced examples across categories.
    """
    prompt = "Classify engineering documents into categories.\n\n"

    # Include one example from each category
    for category, examples in examples_by_category.items():
        ex = examples[0]  # Take first example from each
        prompt += f"Document: {ex['text']}\n"
        prompt += f"Category: {category}\n\n"

    prompt += f"Document: {input_text}\n"
    prompt += f"Category:"

    return prompt

# Usage
examples_by_category = {
    "ANALYSIS": [
        {"text": "FEA results show stress concentration at weld..."}
    ],
    "INSPECTION": [
        {"text": "Visual inspection revealed corrosion on flange..."}
    ],
    "DESIGN": [
        {"text": "The platform shall be designed for 100-year storm..."}
    ]
}

prompt = create_balanced_few_shot(
    examples_by_category,
    input_text="Fatigue analysis indicates 35-year service life..."
)
```
