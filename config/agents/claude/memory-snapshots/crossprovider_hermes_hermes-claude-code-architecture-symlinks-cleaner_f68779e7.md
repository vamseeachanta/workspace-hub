---
name: crossprovider hermes hermes-claude-code-architecture-symlinks-cleaner
description: Hermes-Claude Code architecture: symlinks cleaner than dual-write, but Windows-incompatible
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-architecture, symlink-vs-duplication, cross-platform-blocker]
---

Problem: Hermes writes to ~/.hermes/skills/, Claude Code reads .claude/skills/, no bridge. Solution explored: (1) dual-write wastes space and drifts, (2) symlinks are correct architecture — single source in ~/.hermes/skills/, .claude/skills/ symlinks back, git tracks symlinks. Blocker: Windows git doesn't handle symlinks; needs junction-point fallback or dual-write on Windows. Related GitHub issue #1941.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
