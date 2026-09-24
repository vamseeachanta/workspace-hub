---
name: crossprovider gemini gate-verification-tests-can-run-isolated-from-fu
description: Gate verification tests can run isolated from full verifier artifacts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, agent-infrastructure, python]
---

Direct Python calls to check_agent_log_gate() via `uv run --no-project python -c` avoid dependency on complete verifier infrastructure. Test fixtures need only minimal log directories (`.claude/work-queue/logs/{WRK_ID}-{stage}.log` with action fields), not full artifact sets, enabling faster unit-level gate validation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
