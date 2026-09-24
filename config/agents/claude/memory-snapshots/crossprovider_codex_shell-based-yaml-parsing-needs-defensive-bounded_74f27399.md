---
name: crossprovider codex shell-based-yaml-parsing-needs-defensive-bounded
description: Shell-based YAML parsing needs defensive bounded extraction
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, schema-parsing, robustness]
---

Parsing structured data (YAML frontmatter, enum fields) in bash with regex is brittle without careful handling of CRLF, duplicate keys, and malformed input. Extract via Python/jq, normalize line endings, detect duplicates, and fail closed on ambiguity rather than guessing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
