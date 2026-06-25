---
name: crossprovider codex configuration-metadata-diverges-between-file-and
description: Configuration metadata diverges between file and live state
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [process, documentation, metadata]
---

Status fields in files (plan frontmatter `status: plan-review`) lag live state (GitHub issue label `status:plan-approved`). Check both file content and live system state before making decisions; file-only checks are unreliable when approval/status is updated via external systems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
