---
name: prompt-engineering-3-provide-context
description: 'Sub-skill of prompt-engineering: 3. Provide Context (+1).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 3. Provide Context (+1)

## 3. Provide Context


```python
# Include relevant background
context = """
This is a mooring analysis for an FPSO in the Gulf of Mexico.
Water depth: 1500m
Mooring type: Polyester-chain hybrid
Design life: 25 years
Applicable standard: API RP 2SK 4th Edition
"""
```

## 4. Iterate Based on Failures


```python
# Keep track of failures
failures = []

def log_failure(prompt, expected, actual, notes):
    failures.append({
        "prompt": prompt,
        "expected": expected,
        "actual": actual,
        "notes": notes

*See sub-skills for full details.*
