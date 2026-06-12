---
name: crossprovider hermes memory-bridge-quality-gate-auto-compact-commit-p
description: Memory bridge: quality-gate → auto-compact → commit pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-bridging, quality-gate, git-scoping]
---

When bridging Hermes memory to .claude/memory/: run quality-gate script; if 50–70 quality score, auto-compact (e.g. USER.md 1375→1019 chars) before bridge; if ≥70, bridge directly. Unrelated untracked files can block internal commit; use `stash` recovery to extract narrow scope (e.g. .claude/memory/ only) and commit separately. Retest drift after bridge.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
