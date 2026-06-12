---
name: crossprovider hermes enforcement-gate-ci-fix-uv-missing-and-pythonpat
description: Enforcement-gate CI fix: uv missing and PYTHONPATH needed for workspace_hub imports
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [CI, github-actions, uv, python-imports]
---

The `.github/workflows/enforcement-gate.yml` requires (1) explicit `setup-uv@v4` installation step before any `uv` CLI usage, and (2) `PYTHONPATH: src` environment variable set so scripts like `stage_prompt_drift_check.py` can resolve `import workspace_hub` from `src/`. Without both, CI steps fail.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
