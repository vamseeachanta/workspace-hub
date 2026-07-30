---
name: crossprovider codex generation-bound-coverage-artifacts-prevent-alia
description: Generation-bound coverage artifacts prevent alias overwrites
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [artifact-generation, replay-prevention, publication-atomicity]
---

Coverage evidence must carry the generation digest and reject same-ID outputs from different generations before any ledger access. This prevents silent upgrade of stale/mismatched output and requires structured atomic publication (no-follow opens, descriptor-relative, atomic replace).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
