---
name: dspy
description: Compile prompts into self-improving pipelines with signatures, modules,
  optimizers, and programmatic prompt engineering
version: 1.0.0
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
see_also:
- dspy-dspy-philosophy
- dspy-example-1-engineering-report-analysis-pipeline
- dspy-integration-with-langchain
---

# Dspy

## Quick Start

```bash
# Install DSPy
pip install dspy-ai

# Optional: For retrieval
pip install chromadb faiss-cpu

# Set API key
export OPENAI_API_KEY="your-api-key"
```

## When to Use This Skill

**USE when:**
- Need to optimize prompts programmatically rather than manually
- Building pipelines where prompt quality is critical to success
- Want reproducible, testable prompt engineering
- Working with complex multi-step reasoning tasks
- Need to automatically find effective few-shot examples
- Building systems that improve with more training data
- Require systematic evaluation and comparison of prompt strategies
- Want to abstract away prompt engineering from application logic

**DON'T USE when:**
- Simple single-shot prompts that work well as-is
- Need fine-grained control over exact prompt wording
- Building applications with minimal LLM interactions
- Prototyping where rapid iteration is more important than optimization
- Resource-constrained environments (optimization requires API calls)

## Prerequisites

```bash
# Core installation
pip install dspy-ai>=2.4.0

# For vector retrieval
pip install chromadb>=0.4.0 faiss-cpu>=1.7.0

# For different LLM providers
pip install openai>=1.0.0 anthropic>=0.5.0

# For evaluation
pip install pandas>=2.0.0 scikit-learn>=1.0.0

# Environment setup
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Resources

- **DSPy Documentation**: https://dspy-docs.vercel.app/
- **DSPy GitHub**: https://github.com/stanfordnlp/dspy
- **DSPy Paper**: https://arxiv.org/abs/2310.03714
- **Examples**: https://github.com/stanfordnlp/dspy/tree/main/examples

---

## Version History

- **1.0.0** (2026-01-17): Initial release with signatures, modules, optimizers, and RAG

## Sub-Skills

- [1. Signatures](1-signatures/SKILL.md)
- [2. Modules](2-modules/SKILL.md)
- [3. Retrieval-Augmented Generation](3-retrieval-augmented-generation/SKILL.md)
- [4. Optimizers](4-optimizers/SKILL.md)
- [5. Evaluation and Metrics (+1)](5-evaluation-and-metrics/SKILL.md)
- [1. Start Simple, Then Optimize (+2)](1-start-simple-then-optimize/SKILL.md)
- [Optimization Not Improving (+2)](optimization-not-improving/SKILL.md)

## Sub-Skills

- [DSPy Philosophy](dspy-philosophy/SKILL.md)
- [Example 1: Engineering Report Analysis Pipeline (+2)](example-1-engineering-report-analysis-pipeline/SKILL.md)
- [Integration with LangChain (+1)](integration-with-langchain/SKILL.md)
