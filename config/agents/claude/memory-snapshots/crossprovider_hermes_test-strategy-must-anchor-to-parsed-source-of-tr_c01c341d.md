---
name: crossprovider hermes test-strategy-must-anchor-to-parsed-source-of-tr
description: Test strategy must anchor to parsed source-of-truth, not string presence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, source-of-truth, drift-prevention]
---

Tests checking string presence (e.g., "'eia' appears in manifest") are brittle and reintroduce drift. Instead: parse source-of-truth structure (AST, YAML, config), derive expectations, and test the derived output. For CLI: parse `main.py` registrations and assert docs match.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
