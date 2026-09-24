---
name: crossprovider codex architecture-drift-between-plan-and-implementati
description: Architecture drift between plan and implementation is a critical blocker
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, architecture-drift, blocking-issue]
---

Phase 2 plan (#2847) designed around `.claude/dispatch/<dead_leader>.yaml` JSONL leases but origin/main now has `scripts/operations/dispatch_lease.py` with CAS + fencing semantics. Proceeding without reconciling the lease architecture adds a second failover model instead of integrating or replacing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
