---
name: crossprovider codex default-enforcement-scope-often-excludes-ci-modi
description: Default enforcement scope often excludes CI-modifiable paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-cd, enforcement, scope, github-actions]
---

Enforcement scripts typically scan only narrow paths (`scripts/`, `config/`), but CI pipelines can modify a wider set (workflows in `.github/`, package manifests, deployment configs). If CI runs the script in default scope, it creates gaps that allow violations in out-of-scope paths. Verify that enforced paths cover everything CI can change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
