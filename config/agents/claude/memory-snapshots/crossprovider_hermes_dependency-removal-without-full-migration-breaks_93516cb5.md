---
name: crossprovider hermes dependency-removal-without-full-migration-breaks
description: Dependency removal without full migration breaks installed distributions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependencies, pyproject, distribution, regression]
---

Removing a top-level dependency like `pylife>=2.2,<3.0` from pyproject.toml while code still imports it across multiple shipped modules (`fatigue/sn_curves.py`, `fatigue/damage.py`, etc.) silently breaks wheels for end-users. Current environment may already have the dep, masking the break locally. Requires either restoring the dependency or reworking all imports and API.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
