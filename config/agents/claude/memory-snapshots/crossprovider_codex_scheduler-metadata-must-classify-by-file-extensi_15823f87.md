---
name: crossprovider codex scheduler-metadata-must-classify-by-file-extensi
description: Scheduler metadata must classify by file extension, not format string
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [metadata-accuracy, file-classification]
---

`_write_refresh_metadata()` rglobs all output files except `_metadata.json`/`manifest.json`, then marks all as `format: "csv"`. This conflates `.csv` payloads with `.json` sidecars. Keep sidecars in a separate `sidecar_files` key with distinct format classification; downstream consumers depend on accurate format attribution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
