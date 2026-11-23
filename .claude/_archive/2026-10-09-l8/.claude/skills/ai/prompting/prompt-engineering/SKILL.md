---
name: prompt-engineering
description: Comprehensive prompting techniques including chain-of-thought, few-shot,
  zero-shot, system prompts, persona design, and evaluation patterns
version: 1.0.0
author: workspace-hub
category: ai-prompting
type: skill
trigger: manual
auto_execute: false
tags:
- prompting
- llm
- chain-of-thought
- few-shot
- zero-shot
- system-prompts
- personas
- evaluation
related_skills:
- langchain
- dspy
capabilities:
- chain_of_thought
- few_shot_learning
- zero_shot_prompting
- system_prompt_design
- persona_creation
- structured_output
- prompt_templates
- evaluation_patterns
- iterative_refinement
tools:
- Read
- Write
- Bash
- Grep
platforms:
- python
- api
requires: []
scripts_exempt: true
---

# Prompt Engineering

## Quick Start

```python
import openai

client = openai.OpenAI()

# Basic prompt
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert engineer."},
        {"role": "user", "content": "Explain mooring systems."}
    ]
)

print(response.choices[0].message.content)
```

## When to Use This Skill

**USE when:**
- Designing prompts from scratch for any use case
- Learning core principles applicable across all LLMs
- Need portable patterns not tied to specific frameworks
- Building simple LLM integrations without heavy dependencies
- Optimizing existing prompts for better results
- Creating reusable prompt templates for teams
- Debugging underperforming LLM applications
- Teaching prompt engineering to others

**DON'T USE when:**
- Need framework-specific features (use LangChain/DSPy)
- Require programmatic optimization (use DSPy)
- Building production RAG systems (use LangChain)
- Need conversation memory management (use frameworks)

## Prerequisites

```bash
# OpenAI
pip install openai>=1.0.0
export OPENAI_API_KEY="sk-..."

# Anthropic
pip install anthropic>=0.5.0
export ANTHROPIC_API_KEY="sk-ant-..."

# Azure OpenAI
pip install openai>=1.0.0
export AZURE_OPENAI_ENDPOINT="https://..."
export AZURE_OPENAI_KEY="..."

# Optional: For testing prompts
pip install pytest promptfoo
```

## Resources

- **OpenAI Prompt Engineering Guide**: https://platform.openai.com/docs/guides/prompt-engineering
- **Anthropic Prompt Engineering**: https://docs.anthropic.com/claude/docs/prompt-engineering
- **Prompt Engineering Guide**: https://www.promptingguide.ai/
- **Learn Prompting**: https://learnprompting.org/

---

## Version History

- **1.0.0** (2026-01-17): Initial release with comprehensive prompting patterns

## Sub-Skills

- [1. Zero-Shot Prompting (+1)](1-zero-shot-prompting/SKILL.md)
- [3. Chain-of-Thought Prompting](3-chain-of-thought-prompting/SKILL.md)
- [1. Be Specific and Clear (+1)](1-be-specific-and-clear/SKILL.md)
- [Inconsistent Outputs (+2)](inconsistent-outputs/SKILL.md)

## Sub-Skills

- [Anatomy of a Prompt (+1)](anatomy-of-a-prompt/SKILL.md)
- [Understanding](understanding/SKILL.md)
- [Approach](approach/SKILL.md)
- [Calculation](calculation/SKILL.md)
- [Verification](verification/SKILL.md)
- [4. System Prompt Design](4-system-prompt-design/SKILL.md)
- [Expertise](expertise/SKILL.md)
- [Communication Style](communication-style/SKILL.md)
- [Constraints](constraints/SKILL.md)
- [Your Task](your-task/SKILL.md)
- [Response Format](response-format/SKILL.md)
- [Guidelines](guidelines/SKILL.md)
- [Your Task](your-task/SKILL.md)
- [Response Format](response-format/SKILL.md)
- [5. Persona Design](5-persona-design/SKILL.md)
- [Background](background/SKILL.md)
- [Notable Experience](notable-experience/SKILL.md)
- [Communication Style](communication-style/SKILL.md)
- [Approach](approach/SKILL.md)
- [Communication Adaptation](communication-adaptation/SKILL.md)
- [6. Structured Output (+2)](6-structured-output/SKILL.md)
- [Example 1: Multi-Stage Document Processor (+1)](example-1-multi-stage-document-processor/SKILL.md)
- [Summary](summary/SKILL.md)
- [Findings](findings/SKILL.md)
- [Recommendations](recommendations/SKILL.md)
- [OpenAI Integration (+1)](openai-integration/SKILL.md)
- [Input](input/SKILL.md)
- [Task](task/SKILL.md)
- [Output Format](output-format/SKILL.md)
- [3. Provide Context (+1)](3-provide-context/SKILL.md)
