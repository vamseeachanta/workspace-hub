---
name: crossprovider codex citation-infrastructure-fail-closed-validation-a
description: Citation infrastructure: fail-closed validation against wiki frontmatter
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [citations, standards, validation]
---

Standards-derived constants use `Citation(code_id, publisher, revision, section, wiki_path)` and `CitedValue(value, citation)` with fail-closed validation: `validate_citation()` reads wiki page frontmatter at `wiki_path` and rejects mismatched sections. Tests use vendored fixtures to avoid live wiki dependency. Pattern is reusable across standards-driven calc modules.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
