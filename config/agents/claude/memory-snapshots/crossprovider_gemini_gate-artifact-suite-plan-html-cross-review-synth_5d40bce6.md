---
name: crossprovider gemini gate-artifact-suite-plan-html-cross-review-synth
description: Gate artifact suite: plan HTML, cross-review synthesis, test results, legal scan, claim evidence
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gate-artifacts, validation, work-queue]
---

Each WRK must produce: draft plan HTML, final plan HTML, cross-review synthesis, variation test results, legal scan, and claim evidence YAML. These live in `.claude/work-queue/assets/WRK-XXX/` alongside stage logs in `.claude/work-queue/logs/WRK-XXX-*.log`. The `verify-gate-evidence.py` validator checks for artifact presence and frontmatter consistency.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
