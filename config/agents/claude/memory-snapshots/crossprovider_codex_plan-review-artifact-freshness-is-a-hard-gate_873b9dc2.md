---
name: crossprovider codex plan-review-artifact-freshness-is-a-hard-gate
description: Plan-review artifact freshness is a hard gate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, gates, artifact-traceability]
---

Plans cannot move to status:plan-review if review artifacts are missing, stale, empty, or self-declare MAJOR/FAIL status. Artifacts must cite the reviewed plan SHA, contain no MAJOR verdicts, and pass privacy/legal scans. This is a load-bearing gate that repeatedly blocked advancement in llm-wiki adversarial reviews.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
