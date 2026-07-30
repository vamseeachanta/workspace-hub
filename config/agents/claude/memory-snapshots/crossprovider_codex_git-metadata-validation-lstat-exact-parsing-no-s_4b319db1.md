---
name: crossprovider codex git-metadata-validation-lstat-exact-parsing-no-s
description: Git metadata validation: lstat, exact parsing, no symlinks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, security, input-validation]
---

Use `lstat` (not `is_dir`), exact single-line parsing without trimming valid whitespace, real non-symlink file/directory checks, explicit `.git` common-directory validation. Reject symlinks, multiline content, control chars, missing dirs, forged paths. Explicit RED→GREEN test coverage for each unsafe layout (9+ adversarial cases).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
