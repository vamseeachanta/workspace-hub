---
name: crossprovider codex namespace-package-checkouts-with-spaces-need-quo
description: Namespace-package checkouts with spaces need quoted delegation paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [bash, shell-scripting, edge-cases]
---

When delegating commands to sub-invocations (e.g., script paths with spaces), quoting the path is essential. A spaced-path test initially passing without the fix can hide the regression: verify the fix actually forces a failure first, then observe it passing with the correction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
