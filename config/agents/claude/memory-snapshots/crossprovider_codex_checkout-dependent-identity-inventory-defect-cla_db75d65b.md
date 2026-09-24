---
name: crossprovider codex checkout-dependent-identity-inventory-defect-cla
description: Checkout-dependent identity inventory defect class in reproducible systems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [identity-hash, inventory, reproducibility, defect-class, environment-dependency]
---

When rendering identity hashes or inventory for reproducibility (scheduler operations, artifact attestation), environment variables like $WORKSPACE_HUB create path-dependent outputs that fail across checkout locations. Use registry-backed workspace_root consistently across inventory generation, apply, audit, and enforcement paths to enforce deterministic identity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
