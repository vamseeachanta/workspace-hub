---
name: crossprovider codex enforcement-scripts-need-explicit-path-scoping
description: enforcement scripts need explicit path scoping
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, scripts, performance]
---

Running enforcement scripts (e.g., `scripts/legal/legal-sanity-scan.sh`) without a target path causes unintended whole-repo scans, noise, and slowness. Use `-- <path>` or explicit path argument to limit scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
