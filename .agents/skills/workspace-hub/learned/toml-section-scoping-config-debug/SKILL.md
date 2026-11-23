---
name: toml-section-scoping-config-debug
description: Diagnose TOML config errors caused by misplaced keys in table sections
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["config", "toml", "debugging", "type-mismatch"]
---

# TOML Section Scoping Config Debug

When a TOML config parser reports type mismatches (e.g., expects boolean, got string), check if key-value pairs are accidentally placed inside a `[section]` table instead of at top-level or in their intended section. In TOML, all keys after a section header belong to that table until the next header. Look for duplicate keys at different scopes—remove duplicates from unintended sections. This is a common gotcha when editing TOML by hand without proper section awareness.