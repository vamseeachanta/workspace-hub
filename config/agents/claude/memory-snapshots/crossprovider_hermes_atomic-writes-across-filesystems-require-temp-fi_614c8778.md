---
name: crossprovider hermes atomic-writes-across-filesystems-require-temp-fi
description: Atomic writes across filesystems require temp file in target directory
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-safety, atomic-writes, filesystems]
---

Mktemp defaults to /tmp. If target and /tmp are on different filesystems, `mv temp target` degrades to copy+unlink (non-atomic). Create temp in target's dirname: `mktemp "$(dirname "$target")/.temp.XXXXXX"`. Ensures atomic replace within one filesystem.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
