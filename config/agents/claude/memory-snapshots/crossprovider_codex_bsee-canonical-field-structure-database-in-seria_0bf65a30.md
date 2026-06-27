---
name: crossprovider codex bsee-canonical-field-structure-database-in-seria
description: BSEE canonical field/structure database in serialized `.bin` files
metadata:
  type: reference
  source: codex
  bridged: 2026-06-26
  tags: [bsee-database, field-schema, join-keys]
---

Located at `/mnt/ace/worldenergydata/data/modules/bsee/bin/`: `mv_deep_water_field_leases.bin` (698 field records with water depth, operators) and `platstruc/mv_platstruc_structures.bin`. Join key: `FIELD_NAME_CODE` (field leases) ↔ `BOTM_FLD_NAME_CD` (API well records). This is the authoritative BSEE source for field-structure joins.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
