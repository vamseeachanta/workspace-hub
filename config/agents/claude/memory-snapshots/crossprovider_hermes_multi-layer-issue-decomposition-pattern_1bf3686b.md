---
name: crossprovider hermes multi-layer-issue-decomposition-pattern
description: Multi-layer issue decomposition pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [issue-planning, architecture, workspace-hub]
---

Complex issue chains naturally decompose into three layers: (1) unit/per-tool validation and fixtures, (2) cross-unit normalization/rollup and artifact generation, (3) actionability/governance/reporting and trend analysis. Each layer feeds into the next. After reaching layer 2, evaluate whether next issues belong in layer 2 (e.g., more normalization) or jump to layer 3 (e.g., trend/ownership reporting) rather than proposing redundant sibling work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
