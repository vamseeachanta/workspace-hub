---
name: crossprovider codex machine-gated-pipeline-architecture-with-tdd
description: Machine-gated pipeline architecture with TDD
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, gating, environment-split, tdd]
---

When a pipeline must run partially on restricted machines (licensed, hardware-specific), split into two lanes: license-free (any machine) and license-bound (specific machine). Write tests for both skip-behavior (non-restricted) and success-behavior (restricted) BEFORE implementation. Use explicit machine checks, not implicit failure-driven behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
