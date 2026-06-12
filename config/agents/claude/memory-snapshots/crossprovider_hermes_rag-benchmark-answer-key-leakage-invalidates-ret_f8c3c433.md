---
name: crossprovider hermes rag-benchmark-answer-key-leakage-invalidates-ret
description: RAG benchmark answer-key leakage invalidates retrieval metrics
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [benchmarking, evaluation-pitfall, test-design]
---

Injecting expected path boosts (e.g., `expected_boost = 3.0 if rel_path in question["expected_paths"]`) into the retriever before scoring makes perfect retrieval tautological. A nonsense query still ranks the expected page first due to the boost. Published metrics claiming perfect retrieval are untrustworthy.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
