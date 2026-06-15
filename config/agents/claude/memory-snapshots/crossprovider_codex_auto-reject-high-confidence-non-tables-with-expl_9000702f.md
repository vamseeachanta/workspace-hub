---
name: crossprovider codex auto-reject-high-confidence-non-tables-with-expl
description: Auto-reject high-confidence non-tables with explicit guards
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [auto-reject, false-positive-prevention, heuristics]
---

Safely retire front-matter (ISBN/ICS/copyright markers + zero numeric cells) and empty amendment forms to terminal rejected status. Explicitly exclude false-positive zones: single-column content tables and empty CSVs (may be failed extractions).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
