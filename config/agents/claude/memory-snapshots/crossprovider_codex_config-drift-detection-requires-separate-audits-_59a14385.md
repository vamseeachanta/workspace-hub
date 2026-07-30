---
name: crossprovider codex config-drift-detection-requires-separate-audits-
description: Config drift detection requires separate audits: canonical vs local vs repo-local
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [config, audit, drift]
---

Do not assume config propagation. Audit canonical config (source of truth), machine-local user config (~/.codex/config.toml), AND repo-local config (.codex/config.toml) as three independent sources. A setting present in canonical but missing in repo-local is a real gap, not an inheritance. Record each source separately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
