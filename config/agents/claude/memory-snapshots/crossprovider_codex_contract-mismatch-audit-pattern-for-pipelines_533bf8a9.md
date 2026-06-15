---
name: crossprovider codex contract-mismatch-audit-pattern-for-pipelines
description: Contract mismatch audit pattern for pipelines
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [audit-pattern, scheduler, contract-mismatch]
---

When auditing scheduler/freshness pipelines, systematically identify discrepancies between what health/cron scripts expect vs what code actually writes. Example: scheduler audit found cron expects manifest.json with last_success_ts but code writes _metadata.json to different paths. Always cite file:line evidence and separate 'missing downloader' from 'runtime/credential blocked'.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
