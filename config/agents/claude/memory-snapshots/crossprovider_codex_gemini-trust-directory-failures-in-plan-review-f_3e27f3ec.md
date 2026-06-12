---
name: crossprovider codex gemini-trust-directory-failures-in-plan-review-f
description: Gemini trust-directory failures in plan-review-fanout need environment flags
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gemini-cli, sandbox-trust, plan-review-fanout]
---

plan-review-fanout.sh runs Gemini with `( cd /tmp && gemini -p ... )` which triggers trust-directory failures. Fix requires setting `GEMINI_CLI_TRUST_WORKSPACE=true` environment variable plus the current non-interactive trust bypass flag from the installed CLI (historically `--yolo`, verify current version's documented replacement).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
