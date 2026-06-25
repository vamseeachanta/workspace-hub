---
name: crossprovider codex bsee-api-field-name-join-key
description: BSEE–API field name join key
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [bsee, api, schema, database-join]
---

BSEE deep-water field lease tables (`mv_deep_water_field_leases.bin`) use `FIELD_NAME_CODE`; API well records use `BOTM_FLD_NAME_CD`. This join key bridges BSEE production data to API well metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
