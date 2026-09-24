---
name: crossprovider codex shared-dataset-contains-internal-metadata-rows-e
description: Shared dataset contains internal metadata rows (e.g., separators) requiring explicit classification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-extraction, metadata-handling, cataloging]
---

Real worksheets like Rod Detail Table.xlsx contain internal formatting rows such as `==========` that are not equipment data. These must be explicitly classified and rejected in the extractor, not coerced or dropped invisibly. Preserve every safe row with lineage; quarantine non-keyable entries to expose the real shape.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
