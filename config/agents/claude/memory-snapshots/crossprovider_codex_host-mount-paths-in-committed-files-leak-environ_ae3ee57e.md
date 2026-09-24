---
name: crossprovider codex host-mount-paths-in-committed-files-leak-environ
description: Host mount paths in committed files leak environment configuration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [invariants, configuration, security]
---

Tracked repository files should not contain host-specific mount paths like `/mnt/ace/client-a/` or absolute paths tied to a single machine. These are configuration/environment artifacts, not code. A simple invariant check: no tracked files should contain `file paths matching /mnt/ or other host-specific prefixes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
