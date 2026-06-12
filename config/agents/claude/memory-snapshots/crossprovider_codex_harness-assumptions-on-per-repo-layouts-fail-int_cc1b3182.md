---
name: crossprovider codex harness-assumptions-on-per-repo-layouts-fail-int
description: Harness assumptions on per-repo layouts fail integration
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [integration, multi-repo, config]
---

Harness code that assumes uniform source trees, coverage output paths, or tool configs fails when repos vary (e.g., assethold→coverage.json vs worldenergydata→reports/coverage/coverage.json). Delegate path resolution to per-repo config or auto-discovery; avoid hardcoded assumptions like `--cov=src` or `coverage.json` location.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
