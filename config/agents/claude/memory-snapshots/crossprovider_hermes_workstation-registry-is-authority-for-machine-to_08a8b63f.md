---
name: crossprovider hermes workstation-registry-is-authority-for-machine-to
description: Workstation registry is authority for machine-to-repo assignments, not current filesystem state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [machine-config, source-of-truth, workstation-registry, repo-placement]
---

Machine repo placement decisions should source from `config/workstations/registry.yaml`, not inferred from what repos currently exist on disk. Registry is the source of truth; filesystem state is evidence only. Decisions recorded in GitHub issues reference the registry, then operations follow.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
