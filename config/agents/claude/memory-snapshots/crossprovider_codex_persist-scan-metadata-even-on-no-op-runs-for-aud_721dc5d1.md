---
name: crossprovider codex persist-scan-metadata-even-on-no-op-runs-for-aud
description: Persist scan metadata even on no-op runs for audit verification
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [state-management, nightly-cron, observability]
---

When nightly jobs track last-seen state, update `last_scan_at` and `last_scan_by` on every run, even when no changes detected. Without this, state files stay stale on no-op nights, making it impossible to distinguish 'no changes detected' from 'cron didn't run'.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
