---
name: crossprovider codex orcawave-backend-result-contract-fragmentation
description: OrcaWave backend result-contract fragmentation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [orcawave, result-contract, technical-debt, backend-integration]
---

API saves .owr and .dat but neither is captured in RunResult today. log_file is overloaded (API path → .owr, subprocess path → actual log). Different backends need unified result contract with explicit field semantics to avoid dual-validation hazards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
