---
name: prompt-engineering-3-chain-of-thought-prompting
description: 'Sub-skill of prompt-engineering: 3. Chain-of-Thought Prompting.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 3. Chain-of-Thought Prompting

## 3. Chain-of-Thought Prompting


**Basic Chain-of-Thought:**
```python
COT_TEMPLATE = """
Solve this problem step by step.

Problem: {problem}

Let me think through this carefully:

Step 1: First, I'll identify the key information...
Step 2: Next, I'll determine the approach...
Step 3: Then, I'll perform the calculations...
Step 4: Finally, I'll verify and state the answer...

Solution:
"""

def chain_of_thought_prompt(problem: str) -> str:
    return COT_TEMPLATE.format(problem=problem)

# Usage
prompt = chain_of_thought_prompt(
    problem="""
    A mooring line has a breaking load of 5000 kN.
    The maximum tension is 2800 kN.
    What is the safety factor, and does it meet the API RP 2SK
    requirement of 1.67 for intact conditions?
    """
)
```

**Zero-Shot Chain-of-Thought:**
```python
def zero_shot_cot(question: str) -> str:
    """
    Zero-shot CoT: Simply append "Let's think step by step"
    Surprisingly effective for many reasoning tasks.
    """
    return f"{question}\n\nLet's think step by step."

# Usage
prompt = zero_shot_cot(
    "If a vessel offsets 50m from its mean position, and the "
    "mooring stiffness is 100 kN/m, what is the restoring force?"
)
```

**Structured Chain-of-Thought:**
```python
STRUCTURED_COT_TEMPLATE = """
Analyze this engineering problem using structured reasoning.

Problem: {problem}
