---
name: toml-section-scoping-debug
description: Identify and fix TOML configuration errors caused by misplaced keys inside section headers
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["toml", "config", "debugging"]
---

# Debug TOML Section Scoping Errors

When a TOML parser reports unexpected types for config values (e.g., "expected boolean, got string"), check if the offending keys are accidentally placed inside a `[section]` header. In TOML, all keys after a section header belong to that table until the next header—duplicated keys inside wrong sections will be parsed as nested and cause type mismatches. Search the config file for duplicate key-value pairs, identify which ones are misplaced inside sections, and remove or move them to the correct top-level scope.