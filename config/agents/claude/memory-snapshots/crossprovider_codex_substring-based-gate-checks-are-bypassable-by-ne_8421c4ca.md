---
name: crossprovider codex substring-based-gate-checks-are-bypassable-by-ne
description: Substring-based gate checks are bypassable by negation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [gate-enforcement, schema-validation, security-gates]
---

Gates that validate by substring presence (checking if text contains '#62 requires X') fail when text is negated or reordered ('does not require' passes). Require structural parsing of schemas, not text search.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
