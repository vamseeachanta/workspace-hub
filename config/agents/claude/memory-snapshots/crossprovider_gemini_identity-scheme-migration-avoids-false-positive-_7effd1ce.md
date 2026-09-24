---
name: crossprovider gemini identity-scheme-migration-avoids-false-positive-
description: Identity scheme migration avoids false-positive gaps
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [identity, migration, data-integrity]
---

When migrating identity keys (md5: → sha256:), treat legacy keys as read-only, never as positive match criteria. Unresolved-identity records should not be classified as coverage gaps. Explicit handling prevents false-positive gap reports during transition periods.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
