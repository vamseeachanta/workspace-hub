---
name: crossprovider codex caller-selected-registry-paths-in-apis-create-ra
description: Caller-selected registry paths in APIs create race and authority hazards
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, race-conditions, API-design, access-control]
---

APIs that accept registry paths as caller input risk fabricated schema files granting themselves roots and repository posture unless the parameter is bound to a trusted canonical registry. Implementation must guard descriptor-level and Git bindings against concurrent modification and unauthorized schema promotion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
