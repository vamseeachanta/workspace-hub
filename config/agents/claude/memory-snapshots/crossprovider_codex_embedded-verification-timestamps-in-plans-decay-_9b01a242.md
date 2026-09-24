---
name: crossprovider codex embedded-verification-timestamps-in-plans-decay-
description: Embedded verification timestamps in plans decay and cause approval-review ambiguity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-evidence, staleness, verification]
---

Plans that include verification results embedded at draft time (e.g., "#2550 — OPEN as of 2026-04-29") become stale when reviewed days later. Approval review should rely on fresh attested evidence, not cached timestamps. If issue-body or label claims are needed, add verification commands that can be re-run.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
