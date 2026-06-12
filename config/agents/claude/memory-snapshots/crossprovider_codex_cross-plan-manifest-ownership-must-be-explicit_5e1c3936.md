---
name: crossprovider codex cross-plan-manifest-ownership-must-be-explicit
description: Cross-plan manifest ownership must be explicit
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [coordination, manifest-design, ownership]
---

When one issue creates a manifest for another to consume (e.g., #605's orcawave_package_manifest vs #606's orcawave_mesh_manifest), plan must state: can consuming plan mutate it? are both written atomically? what's the collision-detection/re-run semantics? Implicit ownership leads to silent data races and unclear cleanup responsibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
