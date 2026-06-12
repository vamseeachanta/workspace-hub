---
name: crossprovider hermes bare-python3-drift-systematic-across-shell-and-d
description: Bare python3 drift systematic across shell and doc files
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [python, uv, drift, policy, shell-scripts]
---

All instances of python3 and uv run python3 need replacement with uv run --no-project python. Affects 10+ files: scripts/readiness/, scripts/productivity/, scripts/enforcement/, scripts/ai/, scripts/standards/, .claude/CONFIGURATION.md. Some require --with <package> (pyyaml for yaml parsing, pymupdf/rank_bm25 for search). Standardize quoted heredoc style when replacing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
