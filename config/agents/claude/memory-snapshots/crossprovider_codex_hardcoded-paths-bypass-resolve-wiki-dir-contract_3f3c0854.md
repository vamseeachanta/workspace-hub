---
name: crossprovider codex hardcoded-paths-bypass-resolve-wiki-dir-contract
description: Hardcoded paths bypass resolve_wiki_dir() contracts for portability
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [path-portability, wiki-root-contract, cross-machine]
---

#2125 (Orcina refresh) hardcoded changelog at `data/llm-wiki/changelog/` but the entrypoint uses `resolve_wiki_dir()` with env/config/symlink fallbacks. On any machine not writing to repo-local `data/llm-wiki`, the changelog and wiki state would diverge. Plans must use the same resolution contract as the entrypoint.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
