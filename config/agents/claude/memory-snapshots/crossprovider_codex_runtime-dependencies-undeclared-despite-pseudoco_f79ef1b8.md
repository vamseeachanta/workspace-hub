---
name: crossprovider codex runtime-dependencies-undeclared-despite-pseudoco
description: Runtime dependencies undeclared despite pseudocode usage
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [dependencies, executability, environment]
---

Pseudocode uses CLIs like `sha256sum`, `gh`, `git`, `sed`, `awk`, `readlink` without a declared Dependencies section identifying them as required tools or platform assumptions. Plans must enumerate all new external CLIs, libraries, and environment assumptions upfront.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
