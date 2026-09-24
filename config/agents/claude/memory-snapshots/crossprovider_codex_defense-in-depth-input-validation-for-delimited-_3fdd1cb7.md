---
name: crossprovider codex defense-in-depth-input-validation-for-delimited-
description: Defense-in-depth input validation for delimited output protocols
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, input-validation, data-corruption, defensive-programming]
---

When a function outputs pipe-delimited or other structured text (e.g., `repo|status|version`), validate input to prevent protocol corruption. Guard against empty strings, `.` and `..`, absolute paths (`/`), traversal (`../`), and literal pipe chars in repo names — even though the data source is internal config, this catches mistakes and prevents silent corruption of parsing downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
