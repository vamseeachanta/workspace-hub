---
name: crossprovider codex use-grep-for-transport-failure-classification-in
description: Use grep for transport failure classification in cross-review scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cross-review, codex, tooling, robustness]
---

When classifying transport failures in submit-to-codex.sh, use grep instead of rg for reliable pattern matching. Grep's behavior is more predictable for this detection path, while rg diverges in edge cases that matter for failure classification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
