---
name: crossprovider codex untracked-output-files-require-explicit-inclusio
description: Untracked output files require explicit inclusion verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, reproducibility, testing]
---

Generated artifacts written as untracked files will not land in the repo without explicit `git add`. Review and test cycles may pass on local outputs while the repo remains clean; verification that all generated files are staged is necessary before merge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
