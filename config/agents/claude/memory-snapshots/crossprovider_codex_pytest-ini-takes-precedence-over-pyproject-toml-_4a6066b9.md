---
name: crossprovider codex pytest-ini-takes-precedence-over-pyproject-toml-
description: pytest.ini takes precedence over pyproject.toml, silently shadowing config
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [pytest, configuration, testing, visibility]
---

pytest's config discovery selects pytest.ini first; any testpaths, norecursedirs, or markers in pyproject.toml become dead code when pytest.ini exists. Repos declaring settings in both end up with mismatched effective vs declared config. Consolidate to one per repository.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
