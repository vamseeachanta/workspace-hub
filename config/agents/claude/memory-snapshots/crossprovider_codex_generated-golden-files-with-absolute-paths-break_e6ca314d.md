---
name: crossprovider codex generated-golden-files-with-absolute-paths-break
description: Generated golden files with absolute paths break portability
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [generated-files, testing, fixtures, portability]
---

Test result fixtures/goldens (YAML, CSV, HTML) embedding absolute machine paths like `/mnt/local-analysis/assetutilities/…` fail when committed and checked out on different machines or paths. Normalize paths relative or use symlink-safe staging before writing fixtures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
