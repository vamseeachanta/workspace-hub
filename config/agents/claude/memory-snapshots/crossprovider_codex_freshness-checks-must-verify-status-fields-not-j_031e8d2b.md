---
name: crossprovider codex freshness-checks-must-verify-status-fields-not-j
description: Freshness checks must verify status fields, not just timestamps; missing status checks hide failed jobs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-integrity, testing, manifest-semantics]
---

Checking only `last_success_ts` without verifying `status == 'success'` allows failed or skipped jobs to report as fresh. Requires explicit negative test coverage for non-success manifest cases (e.g., a manifest with `status: 'failure'` but recent timestamp) to catch this defect before production.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
