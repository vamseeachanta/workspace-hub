---
name: crossprovider codex gemini-cli-requires-trust-workspace-env-when-run
description: Gemini CLI requires trust-workspace env when run from non-repo directories
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gemini, cli-quirks, environment]
---

Running `( cd /tmp && gemini -p ... )` triggers trust-directory failures; must set GEMINI_CLI_TRUST_WORKSPACE=true and verify current trust bypass flag (--yolo or documented replacement) is present. Affects review fanout scripts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
