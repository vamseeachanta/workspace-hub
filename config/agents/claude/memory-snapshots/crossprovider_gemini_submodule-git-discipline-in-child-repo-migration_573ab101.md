---
name: crossprovider gemini submodule-git-discipline-in-child-repo-migration
description: Submodule Git discipline in child-repo migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git, submodules, workflow]
---

When migrating specs from child-repo submodule to root specs/, commit deletions/pointer-README changes in the submodule first (`git -C child commit`), then update the hub pointer. Prevents orphaned submodule history and preserves revert capability per submodule semantics.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
