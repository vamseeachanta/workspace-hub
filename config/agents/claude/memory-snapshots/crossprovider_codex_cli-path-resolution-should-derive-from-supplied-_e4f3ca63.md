---
name: crossprovider codex cli-path-resolution-should-derive-from-supplied-
description: CLI path resolution should derive from supplied inputs, not execution context
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cli-design, path-resolution, portability]
---

Using Path.cwd() in CLI tools breaks when invoked from directories outside the repo root, even when all input/output paths are supplied explicitly as absolutes. Infer repo root from manifest/config location or a required input argument instead. The fragility can survive tests if tests only run from repo root.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
