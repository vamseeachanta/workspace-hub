---
name: crossprovider codex portable-sha-256-across-linux-and-macos
description: Portable SHA-256 across Linux and macOS
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, portability, cross-platform]
---

Linux has sha256sum (GNU coreutils), macOS has shasum -a 256. Shell scripts needing hashing should detect and fallback: check `command -v sha256sum` first, then `shasum -a 256`, with explicit error if neither is available.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
