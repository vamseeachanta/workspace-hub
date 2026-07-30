---
name: crossprovider codex large-wiki-repos-need-bounded-validation-scans
description: Large wiki repos need bounded validation scans
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [performance, validation, large-repos]
---

Running full-repo legal/validator scans (--diff-only) on large wikis with extensive untracked/generated content hangs without output. Use --paths or --changed-path scoping to stay responsive; full-repo scans are not practical on these scales.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
