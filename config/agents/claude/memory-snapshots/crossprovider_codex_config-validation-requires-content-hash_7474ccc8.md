---
name: crossprovider codex config-validation-requires-content-hash
description: Config validation requires content hash
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, security, configuration, integrity]
---

Validating config identity (inode + mode + type) alone cannot prevent in-place edits. Include cryptographic hash of config content in attestation. Accept config only if inode, mode, type, AND content hash all match the trusted reference.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
