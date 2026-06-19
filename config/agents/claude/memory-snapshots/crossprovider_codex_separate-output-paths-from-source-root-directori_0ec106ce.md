---
name: crossprovider codex separate-output-paths-from-source-root-directori
description: Separate output paths from source root directories
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [ingest, testing, file-isolation]
---

Scripts generating reports under source roots (e.g., `O&G-Standards/_reports/`) can mutate original data during iteration. Use strict sibling separation: outputs to entirely different mounts or with filesystem enforcement preventing writes to source trees. Test verifies source files are unchanged.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
