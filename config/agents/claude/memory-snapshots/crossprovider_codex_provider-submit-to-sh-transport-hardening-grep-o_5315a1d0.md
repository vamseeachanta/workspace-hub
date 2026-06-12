---
name: crossprovider codex provider-submit-to-sh-transport-hardening-grep-o
description: Provider submit-to-*.sh transport hardening: grep over rg, explicit fallbacks
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cross-provider, orchestration, portability]
---

Cross-provider review scripts (submit-to-codex.sh, submit-to-gemini.sh) need portable failure classification (grep for error patterns instead of rg for portability), explicit fallback chains (uv run → python3 direct), and documented exit code contracts per provider. Codex failure classification uses grep -q for pattern matching; run_renderer falls back to python3 if uv fails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
