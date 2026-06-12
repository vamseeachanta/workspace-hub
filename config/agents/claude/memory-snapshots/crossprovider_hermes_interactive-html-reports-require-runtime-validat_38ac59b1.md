---
name: crossprovider hermes interactive-html-reports-require-runtime-validat
description: Interactive HTML reports require runtime validation, not just static parsing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [interactive-reports, javascript, validation-strategy]
---

Reports with JavaScript-rendered state (charts, populated summary fields, vector rotations) can't be validated by static HTML inspection alone. PDFs printed before JS executes show as incomplete/blank. Separate static validation (structure, text) from runtime validation (after JS materialization and user interaction).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
