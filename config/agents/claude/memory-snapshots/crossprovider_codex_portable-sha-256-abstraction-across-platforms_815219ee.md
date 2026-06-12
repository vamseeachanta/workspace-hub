---
name: crossprovider codex portable-sha-256-abstraction-across-platforms
description: Portable SHA-256 abstraction across platforms
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, portability, linux-vs-macos]
---

Prefer sha256sum (Linux coreutils) over shasum (macOS). Wrap in a _sha256() function that tries sha256sum first, falls back to shasum -a 256. Bail if neither is found.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
