---
name: crossprovider codex field-by-field-validation-prevents-upstream-bypa
description: Field-by-field validation prevents upstream bypass
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [validation, data-integrity, privacy]
---

Copying fields from upstream sources without individual validation can bypass denylist checks. Session 1: `sensitivity` field copied from semantic-index alongside validated `category`, slipped validation because only composed rows were checked, not per-field constraints. Lesson: validate every copied field independently, not just the row it came from.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
