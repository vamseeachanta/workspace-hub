---
name: crossprovider codex frontmatter-regex-parsing-accepts-first-valid-oc
description: Frontmatter regex parsing accepts first valid occurrence, missing malformed duplicates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [yaml-parsing, regex-hazard, duplicate-detection, frontmatter-validation]
---

Regex-based YAML frontmatter extraction finds only the first match. A page with valid first `doc_key: sha256:...` and later duplicate malformed `doc_key: garbage` passes validation. Strict duplicate rejection requires full YAML parse or explicit collection of all matching lines. The pattern `re.search(DOC_KEY_LINE_RE, text)` returns one match; contract validation counts duplicates as handled if the first is valid.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
