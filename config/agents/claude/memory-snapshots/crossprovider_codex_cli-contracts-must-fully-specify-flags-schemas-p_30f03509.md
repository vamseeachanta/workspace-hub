---
name: crossprovider codex cli-contracts-must-fully-specify-flags-schemas-p
description: CLI contracts must fully specify flags, schemas, paths, exit behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cli-design, contract-specification, implementation-blockers]
---

Abstract pseudocode leaves implementations free to hard-code or diverge from intended genericity. Specify exact flag names, fixture schemas, output path conventions, and exit codes (0 = success, 2 = error) before implementation begins.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
