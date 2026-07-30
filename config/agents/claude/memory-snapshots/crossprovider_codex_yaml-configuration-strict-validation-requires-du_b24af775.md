---
name: crossprovider codex yaml-configuration-strict-validation-requires-du
description: YAML configuration strict validation requires duplicates AND types
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [security, configuration, yaml-parsing, schema-validation]
---

Standard yaml.safe_load() with equality checks (e.g., `schema_version == 1`) is not strict: duplicate keys silently use last-value-wins, and type comparisons miss type mismatches (true == 1 == 1.0). Use a SafeLoader subclass that raises ValueError on duplicate keys, plus exact type() checks; add regression tests for both duplicate keys and mistyped scalars.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
