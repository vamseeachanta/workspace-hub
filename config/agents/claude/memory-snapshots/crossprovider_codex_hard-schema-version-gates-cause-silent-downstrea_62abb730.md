---
name: crossprovider codex hard-schema-version-gates-cause-silent-downstrea
description: Hard schema version gates cause silent downstream regressions on producer upgrades
metadata:
  type: reference
  source: codex
  bridged: 2026-07-26
  tags: [schema-migration, validation-gates, regression]
---

When a data producer upgrades its schema_version but downstream validators use hard equality checks (schema_version == 4 instead of >= 4), all reports using the new schema fail silently in unrelated code paths. Tests miss this if test fixtures remain pinned to the old schema version.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
