---
name: crossprovider codex multiple-closed-upstream-issues-create-merged-co
description: Multiple closed upstream issues create merged-contract risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-issue-dependencies, contract-composition, scope-drift]
---

When downstream work depends on multiple closed upstream issues (e.g., #52 consuming #61, #63, #67, #70), the implementation must thread ALL those contracts consistently. Implementation can silently consume only one gate (e.g., #67 firewall shape) while violating another (e.g., #63 canary, #70 trusted evidence). Contract check must verify all named dependencies are actually enforced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
