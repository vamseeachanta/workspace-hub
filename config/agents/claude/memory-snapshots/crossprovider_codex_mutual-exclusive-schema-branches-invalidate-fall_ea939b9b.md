---
name: crossprovider codex mutual-exclusive-schema-branches-invalidate-fall
description: Mutual-exclusive schema branches invalidate fallback logic
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, fallback-logic, mutual-exclusion]
---

When schema forbids simultaneous fields (e.g., DiffractionSpec.vessel and DiffractionSpec.bodies), fallback chains treating them as independent sources fail. Multi-site precedence logic like "spec.vessel.control_surface → body.vessel.control_surface → body.control_surface" is impossible if vessel and bodies are XOR; verify schema constraints before designing fallback chains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
