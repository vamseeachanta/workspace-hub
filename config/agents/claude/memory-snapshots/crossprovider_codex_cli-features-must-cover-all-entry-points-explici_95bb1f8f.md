---
name: crossprovider codex cli-features-must-cover-all-entry-points-explici
description: CLI features must cover all entry points explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cli, testing, entry-points]
---

Adding validation to run-orcawave CLI doesn't auto-apply to batch-orcawave or library OrcaWaveRunner. Must enumerate all paths (commands, batch APIs, library calls) and test each separately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
