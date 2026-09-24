---
name: crossprovider codex output-residency-enforcement-should-use-positive
description: Output residency enforcement should use positive whitelist, not negative blacklist
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [file-paths, output-gating, defect-class]
---

Blocking specific bad destinations (e.g., /mnt/ace) does not guarantee repo-tracked or controlled residency; arbitrary allowed destinations like /tmp and $HOME still bypass intent. Require explicit whitelist of allowed output paths instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
