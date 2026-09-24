---
name: crossprovider codex derived-dimensions-from-bounding-geometry-requir
description: Derived dimensions from bounding geometry require full metadata context
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [geometry-processing, dimension-extraction, metadata-dependency]
---

Extracting principal dimensions (L/B/T) from a bounding box requires: units (ft/mm/m), symmetry flags (half/quarter mesh?), axis orientation, reference datum (waterline/keel), and submerged depth. Without this context, derived specs are ambiguous or wrong. Capture this metadata or fail closed with an override requirement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
