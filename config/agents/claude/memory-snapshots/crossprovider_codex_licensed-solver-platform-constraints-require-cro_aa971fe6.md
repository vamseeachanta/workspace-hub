---
name: crossprovider codex licensed-solver-platform-constraints-require-cro
description: Licensed solver platform constraints require cross-machine routing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [licensing, solver-routing, cross-platform, ci-cd]
---

OrcaFlex and similar licensed solvers are platform-specific (Windows only; no Linux API). Linux CI/runners cannot execute directly. Plan deterministic case bundles routed to licensed Windows workers; de-identify and return results to Linux for verification and publication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
