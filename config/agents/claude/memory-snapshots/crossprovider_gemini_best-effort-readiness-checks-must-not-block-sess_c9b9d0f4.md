---
name: crossprovider gemini best-effort-readiness-checks-must-not-block-sess
description: Best-effort readiness checks must not block session startup
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [readiness, non-blocking, telemetry, best-effort]
---

Readiness checks like `ai-agent-readiness.sh`, `test-health-check.sh`, and QA closure are meant to surface signal, not gate execution. Always `exit 0`; log failures/warnings to JSONL and stdout only. Return status='warn' for version mismatch or quota >80%, status='ok' for healthy state. Non-blocking pattern prevents CI/session delays from telemetry.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
