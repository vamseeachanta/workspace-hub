---
name: crossprovider hermes relative-path-bug-in-cli-tools-with-repo-root
description: Relative path bug in CLI tools with --repo-root
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cli-bugs, reproducibility, path-resolution]
---

When a CLI tool accepts --repo-root and relative output paths, it may resolve the output path against the current working directory, not the repo root. This breaks command reproducibility if the tool is invoked from different directories. Always explicitly resolve output/state paths against the passed --repo-root argument before returning paths or writing documentation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
