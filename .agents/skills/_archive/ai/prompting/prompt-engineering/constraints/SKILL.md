---
name: prompt-engineering-constraints
description: 'Sub-skill of prompt-engineering: Constraints.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# Constraints

## Constraints


{chr(10).join(f"- {c}" for c in constraints)}
"""

    return prompt

# Usage
system_prompt = create_role_system_prompt(
    role="senior offshore structural engineer",
    expertise=[
        "Mooring system design and analysis",
        "Fatigue assessment per DNV standards",
        "API and ISO offshore codes",
        "Finite element analysis"
    ],
    personality="thorough, safety-conscious, and educational",
    constraints=[
        "Always cite relevant standards when applicable",
        "Recommend consulting specialists for critical decisions",
        "Flag any safety concerns prominently"
    ]
)
```

**Task-Specific System Prompt:**
```python
CODE_REVIEW_SYSTEM = """
You are an expert code reviewer specializing in Python and engineering software.
