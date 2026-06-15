---
name: crossprovider codex approved-plan-artifacts-must-sanitize-machine-lo
description: Approved plan artifacts must sanitize machine-local absolute paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [documentation, governance, portability]
---

Avoid exposing absolute paths like `/home/vamsee/...` in repo-tracked plan text, review results, and command transcripts. Use generic references (`<issue-627-worktree>`, branch names, `<home>`) to keep the artifact portable and avoid disclosing machine-specific structure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
