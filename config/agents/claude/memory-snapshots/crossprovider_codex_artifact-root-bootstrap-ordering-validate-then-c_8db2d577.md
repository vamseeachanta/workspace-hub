---
name: crossprovider codex artifact-root-bootstrap-ordering-validate-then-c
description: Artifact root bootstrap ordering: validate, then create
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-safety, artifact-validation, initialization]
---

When emitting/writing to an artifact root path, validate parent existence with `strict=True` AFTER parent directory creation, not before. Validating with `strict=True` before `mkdir` causes production paths to fail if the parent doesn't exist, forcing users to pre-create directories outside the application. Reverse the validation order or use `strict=False` during initial emit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
