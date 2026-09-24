---
name: crossprovider gemini nfs-atomicity-pattern-os-replace-os-fsync-dirfd-
description: NFS atomicity pattern: os.replace() + os.fsync(dirfd) + fallback
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [filesystem, atomicity, shared-storage, reliability]
---

For checkpoint/durability work on shared filesystems: use os.replace() for atomic swap, os.fsync(dirfd) to force directory metadata sync, and explicit fallback when mount is detected as NFS/SMB (which have weaker atomicity guarantees). Checkpoint durability is explicitly tested under NFS conditions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
