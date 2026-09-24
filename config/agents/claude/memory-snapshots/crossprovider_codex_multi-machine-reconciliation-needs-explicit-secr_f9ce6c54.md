---
name: crossprovider codex multi-machine-reconciliation-needs-explicit-secr
description: Multi-machine reconciliation needs explicit secret/config boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-machine, reconciliation, secrets, configuration]
---

When converging machine-local state across fleet via reconcilers, must classify what's git-managed, machine-private, and secret. Don't bulk-promote auth files or credentials to git; use templated injection patterns instead. Reconcilers can accidentally commit tokens or overwrite local device config.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
