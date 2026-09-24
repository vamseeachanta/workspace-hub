---
name: crossprovider codex path-traversal-in-private-mapping-logic
description: Path traversal in private mapping logic
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, path-safety, governance]
---

When mapping opaque IDs to filesystem paths (e.g., lane IDs → folder names), validate that mapped values reject absolute paths, `../`, nested components, and empty strings before walking them. Off-repo mappings create traversal authority risk if not strictly constrained to immediate child names.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
