---
name: dspy
description: Compile prompts into self-improving pipelines with signatures, modules, optimizers, evaluation, and reproducible prompt engineering workflows.
version: 1.1.0
author: workspace-hub
category: ai-prompting
type: skill
trigger: manual
auto_execute: false
capabilities:
- signature_definition
- module_composition
- prompt_optimization
- few_shot_learning
- chain_of_thought
- retrieval_integration
- metric_evaluation
- pipeline_compilation
tools:
- Read
- Write
- Bash
- Grep
tags:
- dspy
- prompt-optimization
- llm
- signatures
- modules
- optimizers
- few-shot
- chain-of-thought
platforms:
- python
related_skills:
- langchain
- prompt-engineering
scripts_exempt: true
---

# DSPy

## Overview

DSPy is for building LLM programs where prompt logic should be structured, testable, and optimizable instead of hand-tuned ad hoc. Use it when you need signatures, modules, evaluation, and optimizers working together as a program rather than a pile of prompts.

## Quick Start

```bash
uv add dspy-ai
export OPENAI_API_KEY="***"
```

Minimal example:

```python
import dspy

lm = dspy.LM("openai/gpt-4.1-mini")
dspy.configure(lm=lm)

class AnswerQuestion(dspy.Signature):
    question = dspy.InputField()
    answer = dspy.OutputField(desc="short factual answer")

predict = dspy.Predict(AnswerQuestion)
result = predict(question="What is vortex-induced vibration?")
print(result.answer)
```

## When to Use

Use DSPy when:
- prompt quality materially affects system quality
- you want reproducible optimization instead of manual prompt edits
- you need structured multi-step reasoning pipelines
- you want train/dev sets and metrics to drive prompt/program improvement
- you are building RAG, classification, extraction, or agent workflows with repeatable evaluation

Do not use DSPy when:
- a simple single prompt already works and is easy to maintain
- exact wording control matters more than programmatic optimization
- the workflow is too small to justify the abstraction

## Core Concepts

### 1. Signatures
Define structured input/output contracts.

```python
class SummarizeSpec(dspy.Signature):
    text = dspy.InputField()
    summary = dspy.OutputField(desc="3-sentence summary")
```

### 2. Modules
Compose behavior from signatures.
- `dspy.Predict`
- `dspy.ChainOfThought`
- `dspy.ReAct`
- custom `dspy.Module`

### 3. Evaluation
Use small but representative datasets and explicit metrics.

### 4. Optimization
Use optimizers when you have examples and a measurable target.
Common patterns include BootstrapFewShot and MIPRO-style optimization depending on installed DSPy version.

## Practical Workflow

1. Start with the simplest working signature
2. Build a baseline module with `Predict`
3. Evaluate on a small labeled set
4. Upgrade to `ChainOfThought` or multi-step modules only if needed
5. Optimize with few-shot / compiler workflows
6. Save the compiled program and test it like code

## Example: Chain of Thought

```python
class MathReasoning(dspy.Signature):
    problem = dspy.InputField()
    solution = dspy.OutputField()

solver = dspy.ChainOfThought(MathReasoning)
print(solver(problem="A riser sees 3 cycles/min for 2 hours. How many cycles?").solution)
```

## Example: Retrieval-Augmented Pattern

```python
class AnswerWithContext(dspy.Signature):
    context = dspy.InputField()
    question = dspy.InputField()
    answer = dspy.OutputField()
```

Use retrieved passages as explicit `context` instead of burying retrieval logic in prompt text.

## Best Practices

- Start simple, then optimize
- Use descriptive output-field descriptions
- Keep evaluation sets representative
- Compare baseline vs optimized behavior explicitly
- Save compiled/optimized programs
- Treat DSPy modules as code artifacts with tests and metrics
- Debug with small examples before scaling up

## Common Failure Modes

- Optimization not improving
  - metric too weak
  - examples not representative
  - signature too vague
- Over-complex pipeline
  - reduce steps before adding optimizers
- Hidden prompt drift
  - save compiled artifacts and compare outputs over time

## Resources

- DSPy docs: https://dspy.ai/
- GitHub: https://github.com/stanfordnlp/dspy
- Paper: https://arxiv.org/abs/2310.03714

## Sub-Skills

- [1. Signatures](1-signatures/SKILL.md)
- [2. Modules](2-modules/SKILL.md)
- [3. Retrieval-Augmented Generation](3-retrieval-augmented-generation/SKILL.md)
- [4. Optimizers](4-optimizers/SKILL.md)
- [5. Evaluation and Metrics (+1)](5-evaluation-and-metrics/SKILL.md)
- [1. Start Simple, Then Optimize (+2)](1-start-simple-then-optimize/SKILL.md)
- [Optimization Not Improving (+2)](optimization-not-improving/SKILL.md)
