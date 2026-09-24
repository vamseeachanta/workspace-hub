---
name: crossprovider codex explicit-anomaly-reporting-prevents-silent-incom
description: Explicit anomaly reporting prevents silent incompleteness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, accounting, system-design]
---

Records silently skipped without counts make totals appear valid while incomplete. In critical paths (accounting, audit, compliance), explicitly report skipped-record counts and anomaly types in structured output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
