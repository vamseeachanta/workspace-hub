---
name: crossprovider codex command-verifiers-need-token-aware-parsing-not-r
description: Command verifiers need token-aware parsing, not regex
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [command-parsing, ci-verification]
---

Simple regex like `flake8 .` can be bypassed by appending args (e.g., `flake8 src tests .`). Parse command tokens and enforce constraints on all occurrences; position-based regex fails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
