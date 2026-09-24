---
name: crossprovider gemini deterministic-scripts-replace-repeated-llm-prose
description: Deterministic scripts replace repeated LLM prose operations
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [prose-to-script, 25-percent-rule, determinism, lsystem-patterns]
---

When the same LLM-driven operation (read YAML, compute age, filter results, lookup entries) recurs across multiple skills or session flows, replace with deterministic shell/Python scripts. WRK-5027 found 5 such candidates (quota-status, snapshot-age, repo-map-context). Use 25% Repetition Rule as trigger.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
