---
name: crossprovider codex artifact-metadata-must-match-file-tracking-state
description: Artifact metadata must match file tracking state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [metadata-consistency, git-state, artifact-safety]
---

Index/log files can reference content not staged for commit, and frontmatter keys can duplicate (e.g., duplicate page_count). Verify `git status` before accepting index/log changes that touch content references; metadata tracking state must align with actual file tracking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
