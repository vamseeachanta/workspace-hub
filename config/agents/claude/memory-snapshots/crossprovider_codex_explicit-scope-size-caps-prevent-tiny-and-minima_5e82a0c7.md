---
name: crossprovider codex explicit-scope-size-caps-prevent-tiny-and-minima
description: Explicit scope-size caps prevent 'tiny' and 'minimal' creep
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope-boundaries, data-sizing, acceptance-criteria]
---

Issues that claim a dataset will be 'tiny' or 'minimal' without explicit size caps (e.g., '<=12 records') drift during implementation. Encode size limits directly in acceptance criteria and measure them in tests to prevent scope creep.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
