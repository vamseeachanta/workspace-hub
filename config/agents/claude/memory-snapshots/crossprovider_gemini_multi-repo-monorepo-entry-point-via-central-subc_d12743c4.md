---
name: crossprovider gemini multi-repo-monorepo-entry-point-via-central-subc
description: Multi-repo monorepo entry point via central subcommand routing table
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cli, monorepo, delegation]
---

Single `ace` CLI with routing dict (prefix → {repo, command, description}). Resolves venv → repo python → fallback to `python -m`. Enables one entry point across 10+ submodules without per-repo wrapper scripts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
