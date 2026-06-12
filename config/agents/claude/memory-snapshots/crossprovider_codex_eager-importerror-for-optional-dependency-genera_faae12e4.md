---
name: crossprovider codex eager-importerror-for-optional-dependency-genera
description: Eager ImportError for optional-dependency generators
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [optional-dependencies, error-handling, generators, python-patterns]
---

When wrapping optional dependencies that feed generators or lazy iterators, raise ImportError eagerly in a private helper before the generator frame, not lazily during iteration. This surfaces errors immediately to callers instead of silently during iteration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
