---
name: crossprovider codex dual-pytest-ini-pyproject-toml-configuration-cre
description: Dual pytest.ini + pyproject.toml configuration creates marker/setting drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, configuration, config-drift, multi-repo]
---

When both files exist in a repo, pytest.ini is authoritative; pyproject.toml pytest settings and markers are ignored but appear valid to code review. Observed in assetutilities and assethold (dual config, divergent marker sets). worldenergydata consolidated to single pyproject.toml source. This divergence is a common source of CI/local test-suite differences and hidden test exclusions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
