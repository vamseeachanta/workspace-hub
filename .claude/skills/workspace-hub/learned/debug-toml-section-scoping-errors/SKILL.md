---
name: debug-toml-section-scoping-errors
description: Diagnose and fix TOML configuration errors caused by misplaced key-value pairs in named sections
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["toml", "config", "debugging"]
---

# Debug TOML Section Scoping Errors

When a TOML parser reports unexpected type errors (e.g., "expected boolean, got string"), check if key-value pairs are accidentally nested inside a `[section]` header where they don't belong. In TOML, all keys after a section header belong to that table until the next header appears. Remove duplicate keys that should only exist at the top-level scope, or move them above the section header if they're needed in the parent context.