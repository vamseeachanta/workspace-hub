---
name: crossprovider hermes memory-bridge-fails-on-dirty-submodules-despite-
description: Memory bridge fails on dirty submodules despite high quality score
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-management, git-operations, bridge-workflow, submodules]
---

pre-bridge-quality.sh --fix succeeds with quality >= 70 but internal bridge commit fails when unrelated submodule dirty state exists (even if memory files themselves are clean). Workaround: use pathspec commit `git commit -- .claude/memory/` before bridge, or manually run bridge without internal commit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
