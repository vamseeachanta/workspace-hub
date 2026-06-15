---
name: crossprovider hermes cross-repo-artifact-pipeline-coordination
description: Cross-repo artifact pipeline coordination
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [proj-a, artifact-generation, cross-repo]
---

proj-a outputs are generated in digitalmodel repo but need to be copied to workspace-hub/acma/ subdirectory as part of the artifact production phase. This requires explicit routing logic rather than generating directly to the final destination, likely due to repo structure constraints.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
