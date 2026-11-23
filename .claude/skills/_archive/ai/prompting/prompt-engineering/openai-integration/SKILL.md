---
name: prompt-engineering-openai-integration
description: 'Sub-skill of prompt-engineering: OpenAI Integration (+1).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# OpenAI Integration (+1)

## OpenAI Integration


```python
import openai

def create_openai_caller(model: str = "gpt-4", temperature: float = 0.7):
    """Create OpenAI API caller."""
    client = openai.OpenAI()

    def call(prompt: str, system: str = None) -> str:
        messages = []
        if system:

*See sub-skills for full details.*

## Anthropic Integration


```python
import anthropic

def create_anthropic_caller(model: str = "claude-3-opus-20240229"):
    """Create Anthropic API caller."""
    client = anthropic.Anthropic()

    def call(prompt: str, system: str = None) -> str:
        response = client.messages.create(
            model=model,

*See sub-skills for full details.*
