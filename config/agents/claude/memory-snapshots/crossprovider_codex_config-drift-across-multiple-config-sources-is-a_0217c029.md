---
name: crossprovider codex config-drift-across-multiple-config-sources-is-a
description: Config drift across multiple config sources is a common plan defect
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, config-drift, pytest, adversarial-review]
---

Plans frequently miss marker registrations that already exist in alternate config files (e.g., pytest markers defined in both pytest.ini AND pyproject.toml). Always verify claimed missing configs across all config sources before accepting resource-intel claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
