---
name: crossprovider gemini generated-artifacts-should-live-in-cache-not-con
description: Generated artifacts should live in cache, not config directories
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [file-organization, gitignore, build-artifacts]
---

Ephemeral generated files (symbol indexes, coverage reports, build outputs) should be written to .cache/, .index/, or similar directories, not config/. Config/ files get committed and reviewed; generated files clutter PRs and risk accidental persistence.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
