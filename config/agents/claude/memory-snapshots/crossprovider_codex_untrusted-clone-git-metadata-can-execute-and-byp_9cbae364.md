---
name: crossprovider codex untrusted-clone-git-metadata-can-execute-and-byp
description: Untrusted clone Git metadata can execute and bypass attestation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, git-safety]
---

Repository-controlled hooks, `.git/objects/info/alternates`, graft/shallow metadata, and replacement refs can all execute or influence Git semantics. When finalizing or validating an untrusted clone, use plumbing that invokes no hooks and explicitly rejects alternate object sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
