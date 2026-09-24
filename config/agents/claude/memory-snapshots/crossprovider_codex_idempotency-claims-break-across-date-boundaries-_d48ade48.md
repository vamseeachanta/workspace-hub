---
name: crossprovider codex idempotency-claims-break-across-date-boundaries-
description: Idempotency claims break across date boundaries when runtime files embed timestamps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [idempotency, timestamp, runtime-state, plan-verification]
---

Plans claiming "rerun produces zero changes except baseline timestamp" fail when setup scripts rewrite home runtime files (e.g., `~/.claude/CLAUDE.md`) with embedded date stamps (`date +%Y-%m-%d`). Re-running on a different date mutates the file. Idempotency audits must enumerate all home-runtime file mutations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
