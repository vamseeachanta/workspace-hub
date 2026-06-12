---
name: crossprovider codex hard-block-clearance-gate-for-sensitive-content-
description: Hard-block clearance gate for sensitive content extraction
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, data-extraction, clearance, test-first]
---

Before extracting vendor/TBE/standards content from external sources (SESA LNG, training materials, etc.), implementation must produce a clearance record (`docs/governance/<name>-clearance-<year>.md` or issue comment) signed by responsible owner with: approver name/role, approval date, allowed extraction level per row, prohibited content classes. Tests must verify clearance exists before extraction runs. This is a pre-code gate, not post-validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
