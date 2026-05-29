# Plan Review — #2841 core (gaps 1-6) — Claude (fresh-context subagent)
- Date: 2026-05-28 · Stage: plan (adversarial) · Verdict: MAJOR → revised (PASS)
- Reviewer: fresh-context subagent; Codex/Gemini UNAVAILABLE (CLAUDECODE, #2721/#2715) — T3 degraded to single-author+fresh-context per feedback_permission_gate_blocks_cross_review.

## Findings (all incorporated)
- F1 [CRITICAL] slice from per-machine untracked auto-memory → cross-machine churn → source from git-tracked .claude/memory/ + single-machine commit.
- F2 [MAJOR] stale resource-intel → verified cron ids on origin/main, pinned.
- F3 [MAJOR] codex AGENTS/SOUL runtime emitted identically → post-emit append to AGENTS.runtime.md only + test.
- F4 denylist→allowlist by category + negative test. F5 single-oversize→drop-and-warn. F6 weekly on dev-primary only + label-first. F7 concrete Hermes verify + probe §3. F8 freshness via cron-log not mtime.

## Confirmed sound: A→B→C sequencing; harness-file-size check doesn't match AGENTS.runtime.md.
Re-review recommended at code stage when cross-provider dispatch available.
