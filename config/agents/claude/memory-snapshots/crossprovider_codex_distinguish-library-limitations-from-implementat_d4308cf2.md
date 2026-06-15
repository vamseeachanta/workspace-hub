---
name: crossprovider codex distinguish-library-limitations-from-implementat
description: Distinguish library limitations from implementation choices in skill documentation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [documentation, skills, accuracy]
---

When a skill describes format-loss (e.g., xlsx formula extraction), be precise: 'openpyxl does not preserve Excel formulas' (library limit) vs 'this script extracts cell values only' (implementation choice). Overclaiming library capability misguides future users and conflates controllable and uncontrollable constraints.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
