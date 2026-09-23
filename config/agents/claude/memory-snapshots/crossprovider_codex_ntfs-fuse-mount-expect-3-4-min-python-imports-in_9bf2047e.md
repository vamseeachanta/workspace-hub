---
name: crossprovider codex ntfs-fuse-mount-expect-3-4-min-python-imports-in
description: NTFS-FUSE mount: expect 3–4 min Python imports; interrupt >10 min blocks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [environment, performance]
---

Imports on this mounted venv take ~3–4 minutes consistently; retries produce identical slowness. After ~10 minutes blocked with no output, acceptable to interrupt and re-run with reduced scope (e.g., plugin-disabled pytest).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
