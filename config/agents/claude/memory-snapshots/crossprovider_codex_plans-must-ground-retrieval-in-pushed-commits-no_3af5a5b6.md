---
name: crossprovider codex plans-must-ground-retrieval-in-pushed-commits-no
description: Plans must ground retrieval in pushed commits, not local draft artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [retrieval, artifact-availability, plan-approval]
---

Many Codex reviews could not complete because plan files cited in /mnt paths did not exist on the GitHub main branch. If a plan file is not pushed to the repository, it cannot be verified and the review becomes speculative. Plans must be committed before cross-provider review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
