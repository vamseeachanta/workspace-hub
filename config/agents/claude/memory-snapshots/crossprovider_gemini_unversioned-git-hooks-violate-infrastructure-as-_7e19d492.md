---
name: crossprovider gemini unversioned-git-hooks-violate-infrastructure-as-
description: Unversioned git hooks violate infrastructure-as-code
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git-hooks, config-management, workspace-hub]
---

`.git/hooks/*` that aren't version-controlled create environment drift and onboarding friction. Use `.pre-commit-config.yaml` with `stages: [push]` or symlink from a version-controlled script in the repo. Every machine must have the same behavior.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
