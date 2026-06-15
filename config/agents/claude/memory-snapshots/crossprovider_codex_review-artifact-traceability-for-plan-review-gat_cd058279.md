---
name: crossprovider codex review-artifact-traceability-for-plan-review-gat
description: Review artifact traceability for plan-review gate
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, review-gates, verification]
---

Plans cannot move to status:plan-review if they name review artifacts that are non-existent, stale, or unverified. Require concrete traceability: each artifact must be non-empty, cite the reviewed plan SHA, return no MAJOR findings, and pass repo-local privacy/legal scans. Named but absent artifacts block the gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
