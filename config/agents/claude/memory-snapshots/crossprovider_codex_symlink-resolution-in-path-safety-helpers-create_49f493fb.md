---
name: crossprovider codex symlink-resolution-in-path-safety-helpers-create
description: Symlink resolution in path-safety helpers creates authorization bypass
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [security, boundaries, path-safety, validation]
---

Imported path-safety helpers (e.g. `_safe_artifact_path()`) may resolve symlinks and accept the resolved target if it's under an allowed root. When combined with digest pinning in a trust registry, a symlink to a forbidden-source artifact can become authorized. Fail-close on symlinks before delegating to path-safety helpers, not after.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
