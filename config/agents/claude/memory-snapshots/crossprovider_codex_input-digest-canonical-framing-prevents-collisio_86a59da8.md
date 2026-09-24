---
name: crossprovider codex input-digest-canonical-framing-prevents-collisio
description: Input digest canonical framing prevents collisions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hashing, serialization, canonicalization, collision-safety]
---

Digest serialization must be versioned, length-framed, byte-sorted with a closed input set. Prevents deserialization ambiguity and hash collisions that cause silent mismatches in caching or deduplication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
