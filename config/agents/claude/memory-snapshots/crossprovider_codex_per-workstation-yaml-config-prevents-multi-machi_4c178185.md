---
name: crossprovider codex per-workstation-yaml-config-prevents-multi-machi
description: Per-workstation YAML config prevents multi-machine drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [configuration-pattern, multi-machine-deployment]
---

Declaring workstation-specific properties (paths, SSH targets, reports) in a YAML config is cleaner and less error-prone than conditional branching in scripts. Centralizes platform divergence in one source of truth rather than ad-hoc per-machine handling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
