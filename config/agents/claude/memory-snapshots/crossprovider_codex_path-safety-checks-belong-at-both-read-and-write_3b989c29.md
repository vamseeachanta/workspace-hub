---
name: crossprovider codex path-safety-checks-belong-at-both-read-and-write
description: Path safety checks belong at both read and write boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, path-traversal, symlinks]
---

Symlink and path-traversal safety must be enforced when both reading and writing evidence files. Applying `_safe_artifact_path()` only to request pointers but not to evidence reads allows an attacker to read outside the repo via the evidence path argument.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
