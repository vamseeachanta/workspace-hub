---
name: crossprovider codex blocking-dependency-status-must-be-verified-from
description: Blocking dependency status must be verified from live labels, not README prose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependency-verification, status-staleness, approval-markers]
---

Live GitHub issue labels (`status:plan-approved`, `status:draft`) and local approval markers (`.planning/plan-approved/NN.md`) are authoritative. README rows can drift. Plans blocked by upstream issues must check live status before draft approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
