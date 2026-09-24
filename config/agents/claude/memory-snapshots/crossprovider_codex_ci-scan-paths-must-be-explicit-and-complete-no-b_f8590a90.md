---
name: crossprovider codex ci-scan-paths-must-be-explicit-and-complete-no-b
description: CI scan paths must be explicit and complete, no broad exemptions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [CI, validation, completeness]
---

Public-leak and validation checks must explicitly name every artifact created by the plan in `.github/workflows/` scan-path entries. Whole-directory rules or blanket exemptions create validation gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
