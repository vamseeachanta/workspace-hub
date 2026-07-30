---
name: crossprovider codex collision-free-versioned-inventory-serialization
description: Collision-free versioned inventory serialization for infrastructure state
metadata:
  type: reference
  source: codex
  bridged: 2026-07-13
  tags: [schema, serialization, infrastructure, git-safety]
---

Schema managing critical state (mutations, configuration, discovery) must version the format, length-frame payloads, byte-sort input, and document closed input sets. For git-based transport, use NUL-safe flags (`git cat-file --batch-command -Z`) to handle odd-byte filenames and non-UTF-8 data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
