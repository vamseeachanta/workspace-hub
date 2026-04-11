---
name: debug-toml-section-scoping-errors
description: Identify and fix TOML config errors caused by misplaced key-value pairs in wrong sections
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["toml", "config", "debugging"]
---

# Debug TOML Section Scoping Errors

When a TOML parser reports an unexpected type error in a section (e.g., "expected a boolean, got string"), check if keys are incorrectly placed inside a `[section]` header instead of at the top level. In TOML, all key-value pairs after a section header belong to that section until the next header. Look for duplicate or stray keys that should exist in the top-level scope, remove them from the wrong section, and verify the fix by re-running the application.