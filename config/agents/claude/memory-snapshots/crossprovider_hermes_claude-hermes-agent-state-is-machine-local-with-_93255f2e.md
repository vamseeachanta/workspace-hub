---
name: crossprovider hermes claude-hermes-agent-state-is-machine-local-with-
description: Claude/Hermes agent state is machine-local with rsync backup only; no git tracking or restore procedure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agent-state-inventory, backup-risk, portability-gap]
---

3.1 GB of Claude Code memory (~/.claude/projects/) and 124 MB of Hermes sessions (342 files) are untracked, backed by rsync only to remote. Critical untracked: learned patterns, session JSONL history, todos/tasks. Only .claude/skills/ (2,843 files) and exported YAML snapshots are git-tracked. Dual-machine failure = total loss of institutional memory.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
