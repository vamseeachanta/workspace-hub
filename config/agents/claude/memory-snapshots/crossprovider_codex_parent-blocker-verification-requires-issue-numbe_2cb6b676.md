---
name: crossprovider codex parent-blocker-verification-requires-issue-numbe
description: Parent blocker verification requires issue-number-to-evidence matching, not path existence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [parent-blocker, gate-mechanics, issue-matching]
---

A shell command `check-completeness-before-close.sh 736` can exist and run, but the gate runner validates the issue argument against the target record's `issue_number` field. Wrong argument number (e.g., passing child #736 when parent #725 completeness is the target) makes the gate return true for the wrong issue. Always verify gate runner logic, not just command existence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
