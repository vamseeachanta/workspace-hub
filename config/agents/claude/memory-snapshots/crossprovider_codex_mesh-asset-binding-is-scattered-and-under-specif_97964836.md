---
name: crossprovider codex mesh-asset-binding-is-scattered-and-under-specif
description: Mesh asset binding is scattered and under-specified; clarify single-source-of-truth before plan approval
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, mesh-handling]
---

Issue #609 identifies that `control_surface`, `damping_lid`, and `free_surface_zone` mesh references appear in both `VesselSpec` and `BodySpec`, but runner/backend only copies/validates vessel-level assets. Plans accepting these mesh types without specifying vessel-level-only or body-level-only binding will silently lose auxiliary meshes. Define binding rules and deprecation path explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
