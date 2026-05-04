---
name: dspy-integration-with-langchain
description: 'Sub-skill of dspy: Integration with LangChain (+1).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# Integration with LangChain (+1)

## Integration with LangChain


```python
import dspy
from langchain_core.runnables import RunnableLambda

# Create DSPy module
class DSPyQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.qa = dspy.ChainOfThought("context, question -> answer")


*See sub-skills for full details.*

## FastAPI Deployment


```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import dspy

app = FastAPI()

# Load optimized module
class QAModule(dspy.Module):
    def __init__(self):

*See sub-skills for full details.*
