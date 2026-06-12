---
name: crossprovider hermes delegation-is-independent-from-repo-placement-de
description: Delegation is independent from repo placement decisions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, architecture, multi-machine, workspace-hub]
---

When planning per-machine tier-1 repo placement, treat provisioning and dispatch-readiness decisions as orthogonal to repo-copy and registry decisions. Avoid coupling agent-delegation scope with physical repo-relocation scope.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
