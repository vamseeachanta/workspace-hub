---
name: crossprovider codex audit-freshness-signals-hide-liveness-failures
description: Audit freshness signals hide liveness failures
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [observability, audits, monitoring]
---

Systems reporting healthy status based on recent file timestamps alone mask operational failures. A background job in dry-run mode produces fresh output files while the actual system is broken. Always verify liveness (does it actually work?) independently from freshness (are files recent?)—double audit false-greens can hide entire subsystem failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
