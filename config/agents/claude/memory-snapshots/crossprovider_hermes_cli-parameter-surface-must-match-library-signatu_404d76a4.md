---
name: crossprovider hermes cli-parameter-surface-must-match-library-signatu
description: CLI parameter surface must match library signature
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cli-library-mismatch, parameter-surface, remote-evidence]
---

`collect_readiness()` library accepts `evidence_dir` but CLI `main()` doesn't expose it. Control plane can't supply remote evidence snapshots via shell invocation. Library and CLI signatures must align.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
