---
name: crossprovider codex relocated-directories-referenced-in-tracked-code
description: Relocated directories referenced in tracked code create reproducibility debt
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [relocation, reproducibility, code-references, maintenance-debt]
---

When a directory containing tracked code dependencies is relocated (e.g., `ocr-lane` with hardcoded runner paths), the references in tracked code must be updated in the same commit. Otherwise the moved code becomes unreproducible—future maintainers will find runner scripts still pointing at deleted paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
