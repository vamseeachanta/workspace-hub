---
name: crossprovider codex two-tier-legacy-discriminator-for-opt-in-gating
description: Two-tier legacy discriminator for opt-in gating
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-migration, legacy-compatibility, gating]
---

When introducing a breaking change on a field with incomplete historical data, use a separate reliable discriminator (e.g., record ID range, schema version) to identify legacy items as exempt from the new gate. This prevents false positives on legacy records with missing or malformed field values.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
