---
name: crossprovider codex constraint-combinations-must-be-validated-as-a-m
description: Constraint combinations must be validated as a matrix, not independently
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [validation-architecture, constraint-coupling, row-semantics]
---

Checking that `visibility` is a valid enum and `route_target` is a valid enum is not enough. Combinations like `visibility=public` + `route_target=metadata_only` without #63 canary evidence, or ingestion metrics with `status=not_applicable_control_plane`, must fail as a holistic constraint. Each dimension check passes independently but the pair is invalid.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
