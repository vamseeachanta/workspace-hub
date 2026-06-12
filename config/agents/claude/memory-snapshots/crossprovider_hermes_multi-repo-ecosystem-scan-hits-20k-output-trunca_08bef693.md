---
name: crossprovider hermes multi-repo-ecosystem-scan-hits-20k-output-trunca
description: Multi-repo ecosystem scan hits ~20k output truncation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gh-api, tooling-quirk, large-repo]
---

Single-shot JSON queries for 8-repo inventory fail to parse when output exceeds ~20k characters (workspace-hub, digitalmodel). Use streaming/pagination or reduce batch scope per repo to avoid truncation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
