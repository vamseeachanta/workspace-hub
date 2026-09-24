---
name: crossprovider codex git-metadata-hardening-lstat-based-validation
description: Git metadata hardening: lstat-based validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-validation, malformed-input-handling, security-testing]
---

Validating `.git` metadata requires `lstat` (not `is_dir`/`is_file`), exact single-line parsing without trimming valid whitespace, real file/directory type checks, and explicit validation of common-directory entries. Symlinks, multiline/control characters, or missing entries produce false-green results without these checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
