---
name: crossprovider codex tracked-workflows-cannot-reference-untracked-imp
description: Tracked workflows cannot reference untracked implementation files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-safety, git-workflow, deployment-hazard]
---

If a tracked CI workflow or validator script imports or invokes untracked implementation files, CI will fail on clean checkout even if local builds succeed. Always verify all files referenced in workflows exist in HEAD.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
