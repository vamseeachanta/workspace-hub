---
name: crossprovider hermes fact-leakage-testing-pattern-for-rag-synthesis-v
description: Fact-leakage testing pattern for RAG synthesis validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, rag, synthesis, benchmark]
---

When testing or benchmarking LLM synthesis from context (e.g., RAG answers), context snippets can unintentionally become the evaluation gold standard, hiding failures where answers reproduce context instead of correctly retrieving facts. Isolate required facts from context using temporary repos or monkeypatching; verify the synthesis function doesn't scan context for them using targeted unit tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
