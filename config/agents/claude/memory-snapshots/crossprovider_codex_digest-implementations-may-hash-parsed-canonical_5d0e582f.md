---
name: crossprovider codex digest-implementations-may-hash-parsed-canonical
description: Digest implementations may hash parsed/canonical forms instead of source bytes — loses distinctions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hash-semantics, content-identity, canonical-form-hazard]
---

Hashing parsed CSV rows after rejoin collapses delimiter, quote style, whitespace, and line-ending differences. Two files with different formatting but same parsed content get the same digest. Hash source bytes or exact decoded text, not canonicalized forms.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
