---
name: crossprovider codex execution-evidence-must-be-git-tracked-not-inlin
description: Execution evidence must be git-tracked, not inline
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, governance, durable-artifacts]
---

Plans that reference execution evidence (e.g., `scripts/review/results/2026-05-20-execute-2745-evidence.md`) must commit those artifacts to the repo. Inline session evidence is not durable; post-execution closeout reviews cannot verify completion without accessible repo artifacts. #2745 closeout found critical AC verification impossible because the cited evidence file was 404.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
