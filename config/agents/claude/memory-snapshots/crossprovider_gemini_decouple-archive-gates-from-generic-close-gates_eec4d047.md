---
name: crossprovider gemini decouple-archive-gates-from-generic-close-gates
description: Decouple archive gates from generic close gates
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gates, phases, orchestration]
---

Archive operations use a separate `--phase archive` (not `--phase close`), allowing archive-specific constraint checks (merge status, remote sync, evidence validation) to be independently hardened without affecting other closure workflows. Prevents cross-concern leakage and enables targeted validation as archive infrastructure matures.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
