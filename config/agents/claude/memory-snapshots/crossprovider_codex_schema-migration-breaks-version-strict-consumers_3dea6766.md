---
name: crossprovider codex schema-migration-breaks-version-strict-consumers
description: Schema migration breaks version-strict consumers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-migration, version-compatibility, test-coverage-gap]
---

Schema-5 collector output from `collect-equality.sh:441` breaks `build-equality-matrix.py:522` provider capability rows because version gate hard-rejects anything except schema 4. Same provider report returns PARITY at schema 4 and MISSING-EVIDENCE at schema 5. Tests miss this because fixture providers are pinned to schema 4 while collector schema tests only assert top-level version.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
