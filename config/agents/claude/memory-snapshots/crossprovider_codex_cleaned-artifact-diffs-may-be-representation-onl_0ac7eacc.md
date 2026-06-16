---
name: crossprovider codex cleaned-artifact-diffs-may-be-representation-onl
description: Cleaned artifact diffs may be representation-only, not semantic changes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [cleanup, audit, manifest]
---

Manifest diffs from cleanup can show path-escaping differences (quoted backslashes vs live names) without data inconsistency. Always verify removed paths are absent on the filesystem; compare actual content, not formatting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
