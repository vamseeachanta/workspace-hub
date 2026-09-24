---
name: crossprovider gemini input-validation-and-citation-metadata-in-standa
description: Input validation and citation metadata in standards-based calculation modules
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [engineering, standards, validation]
---

Engineering calculations from published standards (DNV-RP-B401, etc.) should validate input categories and zones with ValueError, include full standard source in module docstring, and expose constants with section references. Reject unknown categories at parse time, not silently at compute time.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
