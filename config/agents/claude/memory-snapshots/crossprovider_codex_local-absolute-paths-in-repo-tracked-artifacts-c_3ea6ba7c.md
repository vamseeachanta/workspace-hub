---
name: crossprovider codex local-absolute-paths-in-repo-tracked-artifacts-c
description: Local absolute paths in repo-tracked artifacts create portability and disclosure risks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, portability, repo-governance]
---

Plans, reviews, and command transcripts committed to the repo should not expose machine-local paths like `/home/vamsee/...`. Use relative paths or generic descriptors (e.g., `<issue-NNN-worktree>`) to keep artifacts machine-agnostic and avoid unintended disclosure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
