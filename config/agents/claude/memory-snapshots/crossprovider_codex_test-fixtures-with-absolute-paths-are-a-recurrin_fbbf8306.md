---
name: crossprovider codex test-fixtures-with-absolute-paths-are-a-recurrin
description: Test fixtures with absolute paths are a recurring portability hazard
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-fixtures, portability, generated-outputs, path-hardcoding]
---

Generated test goldens embedding hardcoded paths like `/mnt/local-analysis/` break when run on different machines or checkouts. This is recurring across multiple repos (assetutilities, digitalmodel, worldenergydata). Use relative paths, opaque handles, or exclude from commits. Absolute paths in version-controlled fixtures are a sign that golden generation needs decoupling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
