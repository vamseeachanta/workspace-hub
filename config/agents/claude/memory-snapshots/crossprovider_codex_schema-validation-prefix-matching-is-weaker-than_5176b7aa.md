---
name: crossprovider codex schema-validation-prefix-matching-is-weaker-than
description: Schema validation prefix-matching is weaker than exact keyword match
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation-semantics, keyword-matching, schema-enforcement]
---

Accepting any text starting with 'required' (e.g., 'required when available', 'required if X') passes as unconditionally required. Correct fields like title/last_updated/doc_key need strict `required:` not `required: ...conditional text...`. Fix: require exact keyword match for core fields, reserve conditional text only for optional fields, and test negative cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
