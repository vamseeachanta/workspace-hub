---
name: crossprovider codex tracked-documentation-and-comments-are-publicati
description: Tracked documentation and comments are publication surfaces
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [threat-model, public-safety, artifact-classification]
---

Public-output validators often check only explicit nav/index files, missing that tracked `docs/`, `skills/`, review artifacts, and issue comments are already visible in GitHub/CI logs. Private material can leak in tracked files before explicit publication. Public-gate threat models must scan these surfaces.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
