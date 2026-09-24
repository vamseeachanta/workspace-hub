---
name: crossprovider codex pytest-sys-path-does-not-include-repo-root-by-de
description: Pytest sys.path does not include repo root by default
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, environment, python]
---

Running pytest directly in this repo may fail test collection if the repository root is not on sys.path. Remedy: explicitly set PYTHONPATH=. before pytest invocation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
