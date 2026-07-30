---
name: crossprovider codex batch-migrated-generated-files-require-synchrono
description: Batch-migrated generated files require synchronous template updates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [generated-code, migrations, templates, brand]
---

Brand-token migration changed 51 committed HTML outputs but left 19 generator templates with redeclared tokens (`--navy:#0B3D91;--teal:#0f8a7e`). Regenerating these files produces different HTML than the migrated committed versions. When migrating generated outputs, identify and update all source templates and builders simultaneously; use a checker that compares regenerated output to committed output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
