---
name: crossprovider codex advisory-non-blocking-behavior-must-exit-0-not-1
description: Advisory/non-blocking behavior must exit 0, not 1
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [scripting, semantics, unix-conventions]
---

Exit code 1 is a failure status in shells and CI. If a workflow or script is truly advisory and non-blocking, it must exit 0; advisory warnings belong in the output text or structured report, not the exit code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
