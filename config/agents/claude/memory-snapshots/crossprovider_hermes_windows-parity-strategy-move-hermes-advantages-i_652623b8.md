---
name: crossprovider hermes windows-parity-strategy-move-hermes-advantages-i
description: Windows parity strategy: move Hermes advantages into git-tracked repo
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [windows, cross-agent, architecture]
---

Architecture: shared memory lives in `.claude/memory/` (auto-synced from Hermes), skills in `.claude/skills/` (symlinked by Codex/Gemini), session exports in `logs/orchestrator/`. Windows gets parity on `git pull` without local Hermes. Gaps remain (Windows export/sync not automated), but strategy is proven.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
