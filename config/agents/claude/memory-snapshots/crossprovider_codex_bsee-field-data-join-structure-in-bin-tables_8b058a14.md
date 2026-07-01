---
name: crossprovider codex bsee-field-data-join-structure-in-bin-tables
description: BSEE field data join structure in .bin tables
metadata:
  type: reference
  source: codex
  bridged: 2026-06-27
  tags: [bsee-data, join-keys, field-well-linkage]
---

`FIELD_NAME_CODE` in `mv_deep_water_field_leases.bin` joins to `BOTM_FLD_NAME_CD` in API well records; leases, area, and block provide bridges into production datasets. Enables field-well-production linkage from BSEE serialized data at `/mnt/ace/worldenergydata/data/modules/bsee/bin/`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
