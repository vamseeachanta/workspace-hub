---
name: prompt-engineering-1-be-specific-and-clear
description: 'Sub-skill of prompt-engineering: 1. Be Specific and Clear (+1).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 1. Be Specific and Clear (+1)

## 1. Be Specific and Clear


```python
# Bad
prompt = "Analyze this."

# Good
prompt = """
Analyze this mooring analysis report for safety compliance.

Check the following:
1. Safety factors meet API RP 2SK requirements (>=1.67 intact, >=1.25 damaged)
2. Fatigue life exceeds 3x design life
3. All load cases are covered

Report:
{report}

Provide findings in a table format.
"""
```


## 2. Use Consistent Formatting


```python
# Establish consistent patterns
STANDARD_SECTIONS = """
