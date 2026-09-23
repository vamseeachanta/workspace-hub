---
name: crossprovider codex dependency-direction-blocks-code-convergence
description: Dependency direction blocks code convergence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [architecture, dependencies, refactoring]
---

worldenergydata-bsee depends on core, but core cannot import bsee modules without creating a prohibited reverse edge. War-rig-days logic in core's export path blocks convergence of legacy core functions onto the public bsee module.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
