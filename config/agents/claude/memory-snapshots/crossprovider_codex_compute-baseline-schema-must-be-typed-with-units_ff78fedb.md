---
name: crossprovider codex compute-baseline-schema-must-be-typed-with-units
description: Compute baseline schema must be typed with units
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [compute-schema, baseline-specification, units]
---

Conformance checking requires typed fields (cores_min, ram_gib_min, disk_free_gb_min, gpu_required) with explicit units (GB vs GiB); string coercion without schema allows silent comparison failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
