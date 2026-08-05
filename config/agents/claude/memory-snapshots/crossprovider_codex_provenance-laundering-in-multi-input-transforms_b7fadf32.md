---
name: crossprovider codex provenance-laundering-in-multi-input-transforms
description: Provenance laundering in multi-input transforms
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [data-integrity, metadata-decay, transforms]
---

Functions combining multiple sourced inputs (e.g., interpolation) may preserve structure from all inputs but copy only the first input's provenance metadata, allowing placeholder-derived or synthetic data to inherit real-data source labels. Aggregate or validate provenance, don't copy single-input labels.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
