---
name: crossprovider hermes missing-data-sources-degrade-gracefully-indexed-
description: Missing data sources degrade gracefully; indexed artifact tracking safer than fixing sources
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, data-quality, indexing, graceful-degradation]
---

When archive/reference data is missing or empty, generating an index of available artifacts is safer and more maintainable than patching the data source. Index tracks work-item, stages, prompt paths, existence flags, and evidence files—enabling graceful reporting even when underlying data is sparse.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
