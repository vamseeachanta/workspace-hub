---
name: crossprovider hermes path-rglob-follows-symlinked-directories-explici
description: Path.rglob follows symlinked directories; explicit resolution gates needed
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [path-traversal, symlinks, llm-wiki]
---

LLM-wiki #77: `iter_pages()` uses `root.rglob('*.md')` with `os.path.abspath` normalization, allowing symlinked files under repo root to ingest external content. `abspath` keeps the string under the repo root even if the target is outside. Need `os.path.realpath` + symlink-detection gates, or explicit allow-list for symlink targets.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
