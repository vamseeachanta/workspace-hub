---
name: crossprovider codex wiki-doc-key-frontmatter-required-for-changed-pa
description: Wiki doc_key frontmatter required for changed-path validation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [wiki, frontmatter, validation, governance]
---

Governed wiki repositories enforce `doc_key` frontmatter on all markdown files (including `index.md` and `log.md`). Keys should be deterministic from repo-relative paths (e.g. SHA-256 hashes) rather than arbitrary strings, for reproducibility and stability if tooling is later tightened.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
