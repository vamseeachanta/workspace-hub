---
name: crossprovider hermes each-subrepo-has-contract-level-test-commands-no
description: Each subrepo has contract-level test commands; not interchangeable
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, subrepos, ci-cd, pytest]
---

Test invocations are repo-specific contracts: `digitalmodel` requires `PYTHONPATH=src uv run pytest`, `assethold` uses `--noconftest`, `worldenergydata` needs adjacent `assetutilities` in PYTHONPATH. Deviations cause silent failures or import hangs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
