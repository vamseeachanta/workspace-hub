---
name: crossprovider codex path-hardcoding-breaks-portability-across-machin
description: Path hardcoding breaks portability across machines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-resolution, portability, plan-review]
---

Plans should not hardcode output roots like `data/llm-wiki/changelog/...` when existing code uses path-resolution contracts (e.g., `resolve_wiki_dir()` with env/config/symlink fallbacks). Hardcoding breaks on machines with non-standard mounts or symlink layouts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
