---
name: crossprovider codex targeted-probes-catch-parser-state-machine-edge-
description: Targeted probes catch parser state-machine edge cases
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, parser, edge-cases]
---

Parser testing with broad suites misses state transitions around syntax edges (quoted keys, multiline comments, inline-table scope changes). Narrow probes for each scope/syntax combination surface silent-loss bugs that full suite repeatability doesn't catch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
