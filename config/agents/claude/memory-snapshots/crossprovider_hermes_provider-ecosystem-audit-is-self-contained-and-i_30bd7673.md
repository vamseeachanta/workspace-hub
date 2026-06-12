---
name: crossprovider hermes provider-ecosystem-audit-is-self-contained-and-i
description: Provider ecosystem audit is self-contained and independently runnable
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, provider, audit]
---

Cross-provider session health (Claude/Codex/Hermes/Gemini) is audited via `uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py --stdout`. The `hermes-session-export.sh` wrapper may fail (exit code 1 with no diagnostics), but the audit script itself completes successfully and tracks provider health status independently.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
