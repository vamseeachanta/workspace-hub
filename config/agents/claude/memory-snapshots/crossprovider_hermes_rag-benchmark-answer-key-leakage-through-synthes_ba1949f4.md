---
name: crossprovider hermes rag-benchmark-answer-key-leakage-through-synthes
description: RAG benchmark answer-key leakage through synthesize_answer
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [rag-validation, llm-wiki, architectural-defect]
---

The `synthesize_answer()` function reads gold `required_facts` during answer generation, making the grading circular: it manufactures passing answers from the rubric rather than measuring true synthesis capability. Fix: restrict synthesis to retrieved-context-derived text only; keep `required_facts` strictly in evaluator logic.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
