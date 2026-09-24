---
name: crossprovider codex distinguish-additive-schema-changes-from-breakin
description: Distinguish additive schema changes from breaking ones
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, backward-compatibility, planning]
---

When modifying YAML, frontmatter, or other data schemas, explicitly label changes as additive (safe, backward-compatible) vs. breaking (require migration). Example: adding `canonical_title` or `title_aliases` to optional frontmatter fields is additive; removing required fields breaks existing consumers. Additive changes can ship without coordinated migration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
