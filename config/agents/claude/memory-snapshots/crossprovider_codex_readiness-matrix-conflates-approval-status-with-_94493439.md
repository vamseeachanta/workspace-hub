---
name: crossprovider codex readiness-matrix-conflates-approval-status-with-
description: Readiness matrix conflates approval status with implementation evidence; snapshots drift
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [llm-wiki, readiness-tracking, metadata-freshness]
---

The private-ingest readiness matrix marks rows as `implemented` based on `status:plan-approved` in source-issue snapshots, treating authorization as proof of work. Source snapshots also get stale (missing live labels like `status:implemented`). Matrix must check live `current_gate` field, not infer completion from source snapshot labels, and refresh snapshots after issue state changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
