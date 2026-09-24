---
name: crossprovider gemini nfs-file-durability-requires-os-replace-fsync
description: NFS file durability requires os.replace() + fsync
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [file-operations, reliability, platform-specific]
---

Cross-platform file operations on NFS/SMB mounts require os.replace(atomic_write) plus os.fsync(dirfd) for durability guarantees. os.rename() alone is insufficient on networked filesystems.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
