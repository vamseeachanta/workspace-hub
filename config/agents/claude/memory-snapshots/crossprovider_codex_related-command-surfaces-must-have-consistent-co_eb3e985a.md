---
name: crossprovider codex related-command-surfaces-must-have-consistent-co
description: Related command surfaces must have consistent coverage in QA gates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [command-surface, coverage, sibling-consistency]
---

#608 adds mesh QA to `run-orcawave` but omits `batch-orcawave` which calls the same `OrcaWaveRunner` internally. QA gates covering one entrypoint but not sibling callers create bypass paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
