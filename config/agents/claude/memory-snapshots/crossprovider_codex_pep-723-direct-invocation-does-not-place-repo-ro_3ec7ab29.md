---
name: crossprovider codex pep-723-direct-invocation-does-not-place-repo-ro
description: PEP 723 direct invocation does not place repo root on sys.path
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [python-tooling, packaging, quirk]
---

`uv run script.py` via PEP 723 header skips PYTHONPATH setup; sibling package imports fail with ModuleNotFoundError. Must explicitly set PYTHONPATH or use package-relative imports when scripts depend on repo modules.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
