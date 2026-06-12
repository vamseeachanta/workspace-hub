---
name: crossprovider codex config-duplication-across-pytest-ini-and-pyproje
description: Config duplication across pytest.ini and pyproject.toml creates silent contradictions
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [configuration, pytest, drift-risk]
---

Codex found plans claiming 'marker not registered' when pytest.ini already had it, while pyproject.toml defined it separately. Plans touching pytest config must verify ALL sources (pytest.ini, pyproject.toml, conftest.py) and resolve which is canonical. Duplicated configs create silent failures when one is updated and the other drifts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
