---
name: crossprovider hermes python3-python-normalization-safe-in-uv-contexts
description: Python3→python normalization safe in uv contexts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [python, normalization, uv]
---

Repo-wide pattern overwhelmingly uses `uv run --no-project python` not python3. Two files (skill-evals.sh, migrate-memory-to-knowledge.sh) can safely normalize `uv run --no-project python3` → `uv run --no-project python`. This is low-risk internal consistency fix, validated by grep across shell scripts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
