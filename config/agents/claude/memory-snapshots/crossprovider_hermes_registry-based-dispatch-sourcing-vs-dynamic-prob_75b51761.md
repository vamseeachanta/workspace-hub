---
name: crossprovider hermes registry-based-dispatch-sourcing-vs-dynamic-prob
description: Registry-based dispatch sourcing vs. dynamic probing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, dispatch, configuration, source-of-truth]
---

Workstation capabilities (repo paths, installed tools, AI-provider auth state) are sourced from static config/workstations/registry.yaml rather than runtime discovery. Registry is source of truth; dynamic checks are validation only.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
