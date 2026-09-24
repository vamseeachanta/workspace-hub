---
name: crossprovider codex same-name-inode-substitution-race
description: Same-name inode substitution race
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [race-condition, security, toctou, directory-operations]
---

After enumerating a directory and attesting an entry's inode, verify that the entry still names the same inode before proceeding. Rename-away + install-same-name can produce stale snapshots. Rescan directory and verify inode identity matches attested value.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
