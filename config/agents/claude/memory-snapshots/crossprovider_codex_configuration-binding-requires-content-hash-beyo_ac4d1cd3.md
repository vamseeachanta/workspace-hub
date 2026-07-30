---
name: crossprovider codex configuration-binding-requires-content-hash-beyo
description: Configuration binding requires content hash beyond inode
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [configuration, verification, hard-links, mutation-detection]
---

Configuration files validated by inode/device alone can be mutated in-place on hard links or same-inode replacements. Include content hash (via descriptor fstat + hash) in authorization state so in-place edits after initial validation are detected.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
