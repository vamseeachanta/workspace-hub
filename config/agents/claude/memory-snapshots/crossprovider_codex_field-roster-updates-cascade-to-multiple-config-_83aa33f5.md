---
name: crossprovider codex field-roster-updates-cascade-to-multiple-config-
description: Field roster updates cascade to multiple config and reference files
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [dependencies, config-management, field-roster, maintenance]
---

Adding a field to `config/fields.yml` requires updating dependent baseline YAMLs (`golden_baseline_*.yml`, `lease_mapping_*.yml`), frozen reference workbooks, and report generators. Document the roster's downstream consumers and automate the validation or cascade if the pattern repeats.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
