---
name: crossprovider gemini hard-line-limits-require-module-extraction-not-d
description: Hard line limits require module extraction, not deferral
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [refactoring, constraints, modularity]
---

Code exceeding 400-line hard limit needs refactoring, not future-work tickets. Extract new functionality to separate module (e.g., feature_tree.py for feature-tree logic). Keeps main script under limit and enables reuse.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
