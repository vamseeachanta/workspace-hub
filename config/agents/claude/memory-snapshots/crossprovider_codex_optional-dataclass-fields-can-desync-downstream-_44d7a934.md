---
name: crossprovider codex optional-dataclass-fields-can-desync-downstream-
description: Optional dataclass fields can desync downstream validators via asdict()
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [dataclass, json, schema-drift, serialization]
---

Adding optional fields to a dataclass increases sidecar serialization via `asdict()`, but downstream validators written before the field may skip validation for that key entirely. This creates schema drift where extra metadata is accepted but unvalidated. Document the contract explicitly when adding optional fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
