---
name: crossprovider codex backfill-must-be-explicit-about-what-it-populate
description: Backfill must be explicit about what it populates and what it leaves untouched
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [data-migration, testing, specification]
---

Backfills that only normalize existing data (e.g., 'only fill if non-empty') silently leave required fields blank. Document and test exactly which scenarios the backfill handles; silent non-population of required fields is invisible data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
