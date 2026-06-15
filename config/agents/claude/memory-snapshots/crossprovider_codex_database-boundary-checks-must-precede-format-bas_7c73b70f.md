---
name: crossprovider codex database-boundary-checks-must-precede-format-bas
description: Database boundary checks must precede format-based classification rules
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [classification, boundary-enforcement, logic-ordering]
---

Safe-format files (PDFs, Office docs) from database-routed sources (e.g., Newly Classed Vessels, Type Approval records) may not be static public documents. Classification logic must check database boundaries first before deciding a file is safe based on extension.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
