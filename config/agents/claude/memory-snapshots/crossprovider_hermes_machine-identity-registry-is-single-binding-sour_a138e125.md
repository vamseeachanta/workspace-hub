---
name: crossprovider hermes machine-identity-registry-is-single-binding-sour
description: Machine identity registry is single binding source of truth
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [config, inventory, single-source-of-truth]
---

`config/workstations/registry.yaml` is the canonical machine identity/capability record (hostnames, OS, workspace roots, auth state). Creating parallel host registries or metadata files creates divergence hazard. Extend the registry in place, don't duplicate.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
