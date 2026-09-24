---
name: crossprovider codex git-clone-local-creates-hardlinked-objects-not-i
description: git clone --local creates hardlinked objects, not isolation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, isolation, security]
---

`git clone --local` hardlinks files under `.git/objects` with the source repo, sharing inodes. True isolation requires `--no-hardlinks` or explicit inode verification after clone. Any write-capable process in the destination can mutate inodes reachable from the source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
