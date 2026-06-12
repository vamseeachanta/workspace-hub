---
name: crossprovider hermes downstream-dependencies-must-be-repo-tracked
description: Downstream dependencies must be repo-tracked
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependency-chain, rigor, planning-discipline]
---

Plans name downstream issues as unblocking prerequisites (e.g., #2249 depends on #2247) but if no tracked plan/artifact exists for the dependency, the link is unreliable. Require linked GitHub issue + draft plan before approving upstream work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
