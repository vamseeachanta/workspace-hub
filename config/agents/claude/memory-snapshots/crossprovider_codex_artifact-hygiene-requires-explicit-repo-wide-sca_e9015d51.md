---
name: crossprovider codex artifact-hygiene-requires-explicit-repo-wide-sca
description: Artifact hygiene requires explicit repo-wide scanner or validator
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, artifact-validation, governance]
---

`git status` alone is insufficient for detecting secrets, leaked paths, and session tokens. Implement a repo-wide scanner or artifact-specific validator that rejects raw local paths, credentials, and sensitive metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
