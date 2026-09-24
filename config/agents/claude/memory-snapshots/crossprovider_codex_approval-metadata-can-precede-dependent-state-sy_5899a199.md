---
name: crossprovider codex approval-metadata-can-precede-dependent-state-sy
description: Approval metadata can precede dependent state synchronization
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, coordination, metadata-sync]
---

Approval status (`status:plan-approved`) can be recorded before linked schema/docs/tests update, creating inconsistent governance signals only discoverable via local state inspection. This sequencing hazard in multi-file coordination gates requires discovery-first scans when approval markers precede related artifact sync.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
