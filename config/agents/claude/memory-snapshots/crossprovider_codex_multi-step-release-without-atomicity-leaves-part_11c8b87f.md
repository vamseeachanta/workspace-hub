---
name: crossprovider codex multi-step-release-without-atomicity-leaves-part
description: Multi-step release without atomicity leaves partial state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [release, git, error-recovery, atomicity]
---

Committing and tagging a submodule before updating the parent-repo manifest creates a partial-release state where the submodule is tagged but hub metadata is stale. If later steps fail, the submodule remains tagged and committed in an inconsistent state. Transactional guards or rollback logic are needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
