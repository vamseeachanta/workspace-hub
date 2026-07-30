---
name: crossprovider codex plans-must-verify-prerequisites-against-current-
description: Plans must verify prerequisites against current live state
metadata:
  type: reference
  source: codex
  bridged: 2026-07-20
  tags: [planning, prerequisites, validation]
---

Approved plans can conflict with live state: manifests may still have `status: pending` while the plan assumes approval; plans may pin file hashes while proposing mutations to those files. Before execution, verify live state against plan assumptions, especially status fields, contract metadata, and approval gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
