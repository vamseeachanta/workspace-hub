---
name: prompt-engineering-5-persona-design
description: 'Sub-skill of prompt-engineering: 5. Persona Design.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 5. Persona Design

## 5. Persona Design


**Expert Persona:**
```python
def create_expert_persona(
    name: str,
    title: str,
    experience_years: int,
    specializations: list,
    notable_work: list = None,
    communication_style: str = None
) -> str:
    """
    Create a detailed expert persona for the AI.
    """
    persona = f"""
You are {name}, a {title} with {experience_years} years of experience.
