---
name: crossprovider codex scoped-privacy-audits-reduce-false-positives-on-
description: Scoped privacy audits reduce false positives on historical metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [privacy, auditing, methodology]
---

Searching entire files for sensitive data patterns hits pre-existing metadata outside newly-generated sections (page frontmatter, historical references). Scope searches to newly-added lines or bounded generated-section markers only; if whole-file scope is needed, report hit counts and line numbers only, not content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
