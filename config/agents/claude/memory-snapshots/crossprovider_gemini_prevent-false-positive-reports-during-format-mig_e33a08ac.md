---
name: crossprovider gemini prevent-false-positive-reports-during-format-mig
description: Prevent false-positive reports during format migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-migration, backwards-compatibility, reporting]
---

When migrating to canonical identity formats (e.g., sha256: doc keys), accept legacy formats on read, normalize for canonical operations, and classify unresolved identities as diagnostic warnings not coverage gaps. Eliminates false-positive gap reports during migration and provides clear upgrade path.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
