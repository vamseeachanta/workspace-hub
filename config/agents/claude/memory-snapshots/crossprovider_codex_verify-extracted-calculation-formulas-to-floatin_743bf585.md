---
name: crossprovider codex verify-extracted-calculation-formulas-to-floatin
description: Verify extracted calculation formulas to floating-point precision
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [evidence-handling, spreadsheet-extraction, verification]
---

When pulling formulas from legacy workbooks, independently recompute every cell and sensitivity table to floating-point precision. Record exact cell references and embedded constants. Verify the source hash/timestamp remained unchanged. This catches transcription errors and creates an auditable record of what was extracted.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
