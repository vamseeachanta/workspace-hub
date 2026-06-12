---
name: crossprovider codex scheduled-cron-paths-must-remain-read-only-and-l
description: Scheduled cron paths must remain read-only and local-only by default
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cron-safety, read-only-contract, determinism]
---

#2486 blocking findings showed proposals to call writeful `skill-usage-report.py` directly from deterministic `skills-curation` cron path would violate read-only contract. Rule: every v2 signal must consume canonical `weekly_skills_audit.py` inventory or a read-only normalized adapter; no direct calls to writeful helpers from cron.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
