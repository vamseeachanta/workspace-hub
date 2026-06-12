---
name: crossprovider hermes three-terminal-parallel-work-minimizes-git-conte
description: Three-terminal parallel work minimizes git contention via file separation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-work, git-contention, workflow-optimization]
---

Optimal parallel pattern: Terminal 1 (Claude) = high-context orchestration (logs, cron configs, deployment history), Terminal 2 (Codex) = bounded coding tasks (scripts, new modules), Terminal 3 (Codex/Gemini) = audit/research (read-only, no writes). Avoids merge races by targeting non-overlapping file sets. T1 → scripts/monitoring/ + logs/, T2 → scripts/ai/, T3 → .claude/skills/ (read) + docs/reports/ (write).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
