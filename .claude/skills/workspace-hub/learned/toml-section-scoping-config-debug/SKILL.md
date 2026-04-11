---
name: toml-section-scoping-config-debug
description: Diagnose and fix TOML config errors caused by misplaced key-value pairs in wrong sections
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["toml", "config", "debugging", "scoping"]
---

# TOML Section Scoping Config Debug

When a TOML parser reports type mismatches in a config section (e.g., expecting boolean but got string), check for key-value pairs placed under the wrong `[section]` header. In TOML, all keys after a section header belong to that table until the next header—duplicated keys from the top-level scope sitting inside a section will be parsed as section members. Locate and remove such stray duplicates to resolve the error.

## Prevention pattern

For Codex config maintenance, strip managed root-only keys (currently `model` and `model_reasoning_effort`) from every non-root scope before re-prepending them at the top of the file. Also sanitize any appended template fragments so a template that begins with root keys does not accidentally re-insert them inside the active section. Validate both TOML syntax and parsed key scope after rewriting so future syncs fail fast instead of silently re-corrupting the file.

Additional hardening that proved necessary in practice:
- treat commented section headers like `[status_line] # comment` as real table headers during replacement logic
- keep create-path writes atomic: build/validate in a temp file, then `mv` into place
- make `--dry-run` side-effect free: do not pre-create parent directories
- clean temp files explicitly on validation failure; do not rely on normal success-path cleanup only
- line-based regex sanitizers are not sufficient for TOML: they can corrupt multiline strings and miss inline-table leaks; use TOML-aware/Python-assisted sanitization plus recursive validation over both dicts and lists