---
name: crossprovider codex substring-matching-in-tests-is-too-weak-for-stru
description: Substring matching in tests is too weak for structural validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validation, assertion-design]
---

Assertions like `assert "keyword" in text.lower()` pass on unrelated occurrences and cannot detect removal of intended file references or malformed YAML structure. Use line-based or AST-level parsing for validating frontmatter delimiters, file paths, or structured data in tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
