---
name: crossprovider hermes canonical-workstation-registry-prevents-config-d
description: Canonical workstation registry prevents config drift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, configuration, multi-machine]
---

Designate single canonical registry (`config/workstations/registry.yaml`) as source-of-truth for machine dispatch configuration. Competing ad-hoc registries cause dispatch readiness failures and token/env var mismatches. Enforce registry-first lookups in all readiness checks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
