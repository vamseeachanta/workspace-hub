---
name: crossprovider codex scheduler-mutation-authority-must-distinguish-su
description: Scheduler mutation authority must distinguish substring vs exact-state verification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [scheduler-mutations, verification-contracts, workspace-architecture]
---

Substring-based scheduler authority (command_contains, cwd_contains) must remain migration-required status; preservation-only verification (checking multiplicity of preserved/ignore lines) is distinct from exact-state verification (rendered state == planned). Modeling these separately in transaction contracts prevents later certification of weaker guarantees as full compliance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
