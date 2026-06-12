---
name: crossprovider hermes toml-section-headers-create-implicit-table-conte
description: TOML section headers create implicit table contexts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [toml, config-parsing, debugging]
---

Keys placed after a section header (e.g., [tui.model_availability_nux]) are interpreted as members of that table, not top-level keys. If those values don't match the expected type for the table, TOML parsing fails with a type error. Remove duplicate keys or restructure to avoid placing unrelated keys after section headers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
