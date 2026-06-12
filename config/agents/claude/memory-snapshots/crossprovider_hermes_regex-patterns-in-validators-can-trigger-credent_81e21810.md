---
name: crossprovider hermes regex-patterns-in-validators-can-trigger-credent
description: Regex patterns in validators can trigger credential scanners
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [regex, scanner, pre-commit, credential-detection]
---

Unused constants matching security-sensitive terms (e.g., `TITLE_RE` with raw-string patterns) inadvertently trigger pre-commit credential scanners. Fix by removing unused constants or updating scanner allowlist explicitly; prevents false-positive blocks on valid code.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
