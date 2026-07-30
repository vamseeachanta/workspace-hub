---
name: crossprovider codex git-command-cwd-capture-risk-in-artifact-metadat
description: Git command cwd capture risk in artifact metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [git, artifacts, metadata, tooling-quirk]
---

Calling `git` in process cwd to capture revision metadata can record the wrong repository's revision if invoked outside the intended repo. Always verify or document the repository path constraint when capturing revision info in generated artifacts or manifests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
