---
name: crossprovider codex backfill-incompleteness-deriving-missing-values-
description: Backfill incompleteness: deriving missing values vs. normalizing existing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, backfill-pattern]
---

Backfill logic that only normalizes existing values while leaving blanks untouched is incomplete. True backfill must actively derive missing values from authoritative sources, not just clean up what's already present. This affects data integrity when legacy/incomplete data is being upgraded.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
