---
name: crossprovider codex read-only-audits-preserve-parallel-session-state
description: Read-only audits preserve parallel session state
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [workflow, multi-session, safety]
---

When auditing upstream work (e.g., issue #166) while parallel implementation lanes are active, use read-only agents and operations only. Do not modify files, GitHub state, or worktrees. This preserves active parallel sessions and allows independent audit results to inform sequencing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
