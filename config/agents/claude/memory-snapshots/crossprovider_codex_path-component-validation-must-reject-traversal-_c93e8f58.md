---
name: crossprovider codex path-component-validation-must-reject-traversal-
description: Path component validation must reject traversal and absolute-path patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [path-safety, traversal-attacks, input-validation]
---

Using external config/map values as path components (e.g., `root / config_val` in #733) is unsafe without validation. Must reject absolute paths, `..`, nested path separators, empty strings, and `.`. Path validation is a security requirement, not optional for maps/configs used as path arguments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
