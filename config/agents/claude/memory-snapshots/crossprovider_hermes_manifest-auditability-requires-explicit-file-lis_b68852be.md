---
name: crossprovider hermes manifest-auditability-requires-explicit-file-lis
description: Manifest auditability requires explicit file listing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [auditability, validation, traceability, manifest-design]
---

Hash-only manifests (file_count + SHA-256) are performant but prevent scope verification. Explicit repo-relative file listing in manifest needed for reviewer auditability and reproducibility.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
