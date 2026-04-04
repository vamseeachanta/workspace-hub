---
name: Cross-review policy — multi-layer enforcement live
description: "Adversarial AI review gates: gate scripts (#1537), pre-push hook (#1668), daily audit cron, retroactive Codex reviews all operational"
type: project
---

Cross-AI adversarial review policy established by #1515, with enforcement progressively strengthened through 2026-04-02.

**Policy:** Claude=orchestrator, Codex=default adversarial reviewer, Gemini=optional third. Two-provider minimum.

**Enforcement layers (newest first):**
1. **Pre-push review gate + daily audit cron** (#1668, commit `541c74c6`, 2026-04-02) — blocks pushes without review evidence, daily cron audits compliance
2. **Retroactive Codex adversarial review** (commit `fdfddd4a`, 2026-04-02) — MAJOR review across 3 streams retroactively
3. **Gate scripts** (#1537, `scripts/enforcement/`) — blocks `gh pr create`, `gsd-execute-phase`, `gsd-ship` without adversarial REVIEWS.md
4. **Claude hook** (`.claude/hooks/cross-review-gate.sh`) — PreToolUse on Bash

**Why:** Prevents single-AI blind spots. Documentation-only policy was not being followed, so enforcement was progressively automated.

**How to apply:** Gates fire automatically. If blocked, run `/gsd:review --phase <N> --codex`. The system now has 3 layers (hook, git pre-push, daily audit) making bypass unlikely.
