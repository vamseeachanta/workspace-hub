---
name: crossprovider codex manifest-version-and-schema-hash-validation-must
description: Manifest version and schema hash validation must be exact, not advisory
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, reproducibility, versioning]
---

Saying a plan "requires v2" is insufficient; manifests must carry and every consumer must validate `contract_version`, schema hash, input hashes, producer commit, and generated-at policy. Advisory versioning permits silent divergence and breaks reproducibility across boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
