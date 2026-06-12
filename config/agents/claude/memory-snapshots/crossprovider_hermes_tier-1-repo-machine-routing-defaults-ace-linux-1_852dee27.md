---
name: crossprovider hermes tier-1-repo-machine-routing-defaults-ace-linux-1
description: Tier-1 repo machine routing defaults: ace-linux-1 primary, ace-linux-2 requires readiness check
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [machine-routing, execution-defaults, readiness-gate]
---

All planning packets default execution to ace-linux-1 (Hermes control-plane). ace-linux-2 is overflow-only after explicit readiness gate (auth, tools, paths verified). This consistent routing prevents environmental surprises.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
