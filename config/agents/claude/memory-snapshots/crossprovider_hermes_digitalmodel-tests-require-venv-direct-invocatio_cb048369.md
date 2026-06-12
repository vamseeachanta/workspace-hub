---
name: crossprovider hermes digitalmodel-tests-require-venv-direct-invocatio
description: digitalmodel tests require venv direct invocation, not editable install
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [digitalmodel, testing]
---

Must use `PYTHONPATH=src /mnt/local-analysis/workspace-hub/digitalmodel/.venv/bin/python -m pytest` not editable installs. Editable paths cause assetutilities import failures. Applies to all GTM demo validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
