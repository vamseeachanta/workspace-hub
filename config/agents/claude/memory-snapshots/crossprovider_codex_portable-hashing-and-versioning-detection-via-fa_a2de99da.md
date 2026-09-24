---
name: crossprovider codex portable-hashing-and-versioning-detection-via-fa
description: Portable hashing and versioning detection via fallback chains
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, portability, version-detection, cross-platform]
---

Combine `command -v X` with fallbacks: prefer `sha256sum` (Linux coreutils), fall back to `shasum -a 256` (macOS). For version detection, strip non-semver suffixes with sed (`sed 's/[^0-9.].*$//'`), then use `sort -V` for semver comparison — if the minimum appears first in sorted output, actual ≥ minimum.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
