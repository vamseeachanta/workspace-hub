---
name: crossprovider codex github-event-timeline-is-authoritative-for-audit
description: GitHub event timeline is authoritative for audit evidence, not filesystem timestamps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit, evidence-model, chronology]
---

Compliance audits fail when they rely on commit/artifact timestamps instead of GitHub issue timeline (creation, label date, comment time). Retrofitted labels, amended commits, and missing artifacts break timestamp-based logic. Reconcile evidence against GitHub timeline, not the reverse.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
