---
name: crossprovider codex bounded-audit-commands-avoid-fuse-scan-paralysis
description: Bounded audit commands avoid FUSE scan paralysis
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [audit, fuse-mount, performance, procedures]
---

Avoid `find /mnt/local-analysis`, recursive grep, or `ls -R` during read-only audits on FUSE mounts. Instead, use targeted `/proc` queries (`ps -eo ppid,stat,etimes,%cpu`), bounded crontab reads (`crontab -l`), and exact path grep on known config files. Enumerate repositories from registry data, not by scanning directories.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
