---
name: crossprovider codex exact-readme-heading-match-via-grep-anchors-prev
description: Exact README heading match via grep anchors prevents false positives
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [validation, pattern]
---

For README validation, use `grep -qEi "^#+[[:space:]]*${section}$"` to match only markdown headings (anchors ^ and $), not section keywords in body text. Reduces false PASS on incomplete docs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
