---
name: crossprovider gemini canonical-identity-join-contract-with-legacy-com
description: Canonical identity join contract with legacy compatibility reads
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-migration, identity-contract, legacy-compatibility]
---

For data migration from legacy hashes (md5) to canonical (sha256), read both formats but only canonically-formatted keys enter matching/coverage logic. Bare hex and legacy hashes get explicit status tags (warnings, identity-unresolved) rather than false positives. Pattern applies to any legacy-to-canonical data migration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
