---
name: dspy-example-1-engineering-report-analysis-pipeline
description: 'Sub-skill of dspy: Example 1: Engineering Report Analysis Pipeline (+2).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# Example 1: Engineering Report Analysis Pipeline (+2)

## Example 1: Engineering Report Analysis Pipeline


```python
import dspy
from dspy.teleprompt import BootstrapFewShot
from typing import List
import json

# Configure DSPy
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4", max_tokens=2000))

# Define signatures

*See sub-skills for full details.*

## Example 2: Optimized Technical Q&A System


```python
import dspy
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
from dspy.retrieve.chromadb_rm import ChromadbRM

# Setup retriever
retriever = ChromadbRM(
    collection_name="engineering_knowledge",
    persist_directory="./chroma_db",
    k=5

*See sub-skills for full details.*

## Example 3: Comparison with Baseline


```python
import dspy
from dspy.evaluate import Evaluate
from dspy.teleprompt import BootstrapFewShot
import pandas as pd

class SimpleQA(dspy.Module):
    """Baseline: Simple prediction without optimization."""
    def __init__(self):
        super().__init__()

*See sub-skills for full details.*
