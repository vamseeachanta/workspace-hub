---
name: crossprovider codex multi-repo-quality-tools-must-run-from-each-repo
description: Multi-repo quality tools must run from each repo's root so pyproject.toml and local dependencies are in scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-repo-tooling, execution-context, uv-tools, WRK-1056]
---

Running `uv tool run ruff` or `uv tool run mypy` from the workspace root with a repo path argument will not give tools access to that repo's installed dependencies, import roots, or pyproject.toml configuration. Instead, cd into each repo and run tools from that repo root, especially critical for repos with local path sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
