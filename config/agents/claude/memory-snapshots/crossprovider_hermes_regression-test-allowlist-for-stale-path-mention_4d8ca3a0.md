---
name: crossprovider hermes regression-test-allowlist-for-stale-path-mention
description: Regression test allowlist for stale-path mentions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, regression, stale-paths]
---

Minimal safe allowlist of 4 docs allowed to mention deleted/legacy paths: docs/work-queue-workflow.md, docs/ops/legacy-claude-reference-map.md, docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md, GEMINI.md. Ban stale patterns (scripts/work-queue/new-spec.sh, scripts/agents/*, parse-session-logs.sh, etc.) everywhere else via parameterized pytest test in tests/docs/test_banned_stale_references.py.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
