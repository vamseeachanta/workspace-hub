---
name: crossprovider codex codex-configuration-portability-repo-vs-machine-
description: Codex configuration portability: repo vs machine-local split
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex, hooks, deployment, machine-local, portability]
---

.codex/config.toml model/reasoning/feature-flag defaults travel with repo; ~/.codex/config.yaml hook trust state (trusted_hash entries) is machine-local and must be re-approved per user/machine. Absolute paths in hook command bodies block checkout-path portability; relative paths or env-var substitution required for cross-machine deployment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
