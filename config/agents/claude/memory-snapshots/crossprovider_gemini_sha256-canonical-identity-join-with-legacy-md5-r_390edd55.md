---
name: crossprovider gemini sha256-canonical-identity-join-with-legacy-md5-r
description: Sha256 canonical identity join with legacy md5 read-only
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-join, identity, legacy-migration, data-contract]
---

For identity joins across source inventories and wiki coverage, use sha256:<64hex> as sole positive match key. Accept md5:<hex> for reads but never as positive match. Normalize bare hex to sha256: with warning; emit unresolved identity as identity-unresolved status, not false-gap. Avoids false positives during legacy migrations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
