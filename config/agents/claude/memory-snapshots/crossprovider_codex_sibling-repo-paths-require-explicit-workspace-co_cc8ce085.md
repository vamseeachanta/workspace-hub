---
name: crossprovider codex sibling-repo-paths-require-explicit-workspace-co
description: Sibling repo paths require explicit workspace context and verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sibling-repos, path-resolution, workspace-context, reproducibility]
---

When a tool (e.g., legal scanner) reads relative paths into sibling repositories, the computed path is fragile without explicit verification. Commands should include the workspace root variable, validate the resolved path exists, and optionally run the tool to confirm success before treating the recipe as reproducible.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
