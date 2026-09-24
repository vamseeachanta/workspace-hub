---
name: crossprovider codex verify-sibling-state-before-proposing-umbrella-w
description: Verify sibling state before proposing umbrella work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, verification, code-review]
---

When reviewing umbrella/lane-tracking issues, explicitly enumerate the current state (OPEN/CLOSED) of referenced child issues rather than treating plan claims as authoritative. State shifts (e.g., completed child issues) may mean proposed work duplicates existing deliverables or is already closed. Grep or `git ls-files` to verify artifact existence before accepting plan assertions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
