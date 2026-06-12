---
name: crossprovider hermes artifact-freshness-guards-prevent-stale-checked-
description: Artifact freshness guards prevent stale checked-in outputs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-coverage, artifact-freshness, generated-content]
---

Generated artifacts can drift from source code if regeneration doesn't follow updates. Add tests comparing artifact manifest/provenance against live generation. B1528 SIROCCO: source code updated to describe current-vs-rudder comparison, but checked-in Markdown/HTML still described rudder-only scope, risking consumer misunderstanding.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
