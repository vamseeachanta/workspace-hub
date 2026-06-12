---
name: crossprovider hermes provider-session-audit-pipeline-exports-hermes-c
description: Provider session audit pipeline exports Hermes/Codex/Gemini sequentially, then patches skills
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-audit, learning-pipeline, skill-ecosystem]
---

The full ecosystem audit workflow: `hermes-session-export.sh --all` → `codex-session-export.sh --all` → `gemini-session-export.sh --all` → `provider-session-ecosystem-audit.sh` → `scripts/learning/comprehensive-learning.sh`. Runs only on designated hosts (dev-primary, ace-linux-1). Identify remediation rules (path drift, context drift) and patch scripts/docs/tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
