---
name: crossprovider codex bsee-field-data-join-via-field-name-code-botm-fl
description: BSEE field data: join via FIELD_NAME_CODE / BOTM_FLD_NAME_CD; SubseaIQ not in standard tables
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [bsee-data, field-identifiers]
---

BSEE .bin tables under `/mnt/ace/worldenergydata/data/modules/bsee/bin/` (e.g., `mv_deep_water_field_leases.bin`, `platstruc/mv_platstruc_structures.bin`) use `FIELD_NAME_CODE` as field identifier. No SubseaIQ column exists in BSEE standard exports; external mapping required if SubseaIQ data is needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
