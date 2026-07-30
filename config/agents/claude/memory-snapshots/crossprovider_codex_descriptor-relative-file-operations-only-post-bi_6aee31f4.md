---
name: crossprovider codex descriptor-relative-file-operations-only-post-bi
description: Descriptor-relative file operations only post-bind
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, file-operations]
---

For security-critical operations, use descriptor-relative paths only *after* the directory is descriptor-bound via an open file descriptor. Pre-bind races (between validation and open) and parent-swap TOCTOU are acknowledged risks; post-bind operations are safe.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
