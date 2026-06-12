---
name: crossprovider codex timestamp-based-event-ordering-needs-explicit-ti
description: Timestamp-based event ordering needs explicit tie-break and source rules
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [correctness, governance, design]
---

Governance designs using timestamps to order events (approval vs revert, first approval vs later approval) break on equal timestamps and mixed evidence sources (git commit-date vs GitHub label-changed vs marker-file mtime). Define canonical source and tie-break.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
