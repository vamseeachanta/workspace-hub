---
name: crossprovider codex hugging-face-publishing-requires-strict-contract
description: Hugging Face publishing requires strict contract enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [hugging-face, data-publishing, schema]
---

HF datasets need reproducible schema versioning, source-hash tracking, license metadata, and consistent dataset naming. Mismatches between bundle declaration and publisher code silently break regeneration. Lock down the full contract before implementation: schema version, provenance fields, licensing, and immutable publication revision.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
