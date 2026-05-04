---
name: prompt-engineering-6-structured-output
description: 'Sub-skill of prompt-engineering: 6. Structured Output (+2).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 6. Structured Output (+2)

## 6. Structured Output


**JSON Output:**
```python
JSON_OUTPUT_TEMPLATE = """
Analyze the following engineering data and return your analysis as JSON.

Data:
{input_data}

Return a JSON object with this exact structure:
{{

*See sub-skills for full details.*

## 7. Prompt Templates


**Reusable Template Class:**
```python
from string import Template
from typing import Dict, Any, Optional
import json

class PromptTemplate:
    """
    Reusable prompt template with validation and versioning.
    """

*See sub-skills for full details.*

## 8. Evaluation and Iteration


**Prompt Testing Framework:**
```python
from dataclasses import dataclass
from typing import Callable, List
import json

@dataclass
class TestCase:
    """Single test case for prompt evaluation."""
    input_data: dict

*See sub-skills for full details.*
