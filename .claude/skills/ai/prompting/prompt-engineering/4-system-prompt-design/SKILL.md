---
name: prompt-engineering-4-system-prompt-design
description: 'Sub-skill of prompt-engineering: 4. System Prompt Design.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 4. System Prompt Design

## 4. System Prompt Design


**Role-Based System Prompt:**
```python
def create_role_system_prompt(
    role: str,
    expertise: list,
    personality: str = "professional and helpful",
    constraints: list = None
) -> str:
    """
    Create a role-based system prompt.
    """
    prompt = f"""You are a {role}.
