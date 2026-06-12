---
name: crossprovider codex tier-1-repos-require-sibling-dependency-bootstra
description: Tier-1 repos require sibling dependency bootstrap in isolation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [isolation, uv, tier-1-repos, dependencies]
---

When creating isolated clones of tier-1 repos (digitalmodel, assethold, assetutilities) for issue work, projects have uv setup expecting sibling ../dependency repos. Clone both repos into the nested isolated structure so `uv run` resolves all dependencies within isolation. Single-repo clones will fail with missing sibling imports (e.g., '../assetutilities').

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
