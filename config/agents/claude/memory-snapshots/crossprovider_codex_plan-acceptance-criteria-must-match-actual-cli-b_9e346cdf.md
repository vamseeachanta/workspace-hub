---
name: crossprovider codex plan-acceptance-criteria-must-match-actual-cli-b
description: Plan acceptance criteria must match actual CLI behavior and error codes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-acceptance, cli-verification, acceptance-criteria]
---

Plans claiming acceptance criteria like "run `gemini auth` interactively" must verify the CLI actually has that subcommand before marking it as acceptance. Non-existent commands make acceptance criteria untestable and mask implementation gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
