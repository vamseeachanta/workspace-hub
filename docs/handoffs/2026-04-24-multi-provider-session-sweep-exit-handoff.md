# 2026-04-24 Multi-Provider Session Sweep Exit Handoff

## Session objective
Assess recent/unassessed AI provider sessions (Hermes, Claude, Codex) and transfer durable learnings into the repo ecosystem.

## Current state
- No open GitHub issue; this was an unblocked maintenance sweep.
- Anchor commit for prior transfer: `2a9a5ef4c` (2026-04-11 — previous `docs(memory): transfer durable session-log learnings`).
- Sweep-commit this session: `8e2236d7d` — `docs(memory): transfer multi-provider session learnings (Claude + Codex + Hermes)`.

## What is complete

### 1. Provider session inventory
Counted sessions since `2a9a5ef4c`:
- Claude: ~161 JSONLs under `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/`
- Codex: ~364 rollout JSONLs under `~/.codex/sessions/2026/04/`
- Hermes: ~250 session JSONs under `~/.hermes/sessions/` plus `interrupt_debug.log`

Scan used signal extraction (correction/surprise/failure keywords + first-user-prompt topic map), not full ingestion.

### 2. Dominant workload identified
Issue #2460 (tier-1 indexing and code-placement contract, CLOSED 2026-04-23) dominated the window: **r1 → r16 adversarial-review loop**, Codex verdict sequence today = `MAJOR×8 → MINOR → REQUEST_CHANGES×2 → MINOR → APPROVE`.

### 3. Three net-new learnings captured

**Auto-memory only (`/home/vamsee/.claude/projects/.../memory/`):**
- `feedback_codex_sandbox_fallback_paths.md` — Codex shell-blocked fallbacks: `js_repl` (dominant ~70%), GitHub connector, non-login shell retry. Weakly-grounded verdict rule added.
- `feedback_codex_sustained_major_loop.md` — UPDATED with #2460 as third instance (alongside #2045, #2289); added meta-lesson flagging Level-2 promotion need.
- `project_issue_2460_approval_binding.md` — NEW: approval markers must bind to four immutable anchors (plan SHA, review-artifact paths + verdicts, storage surface, revision cleanup protocol).
- `MEMORY.md` index updated (69 lines, under 200-line auto-truncation cap).

**Git-tracked (`.claude/memory/topics/`, shipped in `8e2236d7d`):**
- `feedback_codex_sandbox_fallback_paths.md` — mirrored from auto-memory (cross-machine relevance).
- `feedback_codex_sustained_major_loop.md` — PROMOTED from auto-memory-only to git-tracked.
- `improve-log.md` — chronological sweep entry appended.

The project-specific `project_issue_2460_approval_binding.md` intentionally stayed in auto-memory only per the topics/ promotion convention (no `project_*` files in git-tracked topics).

### 4. Follow-up agent scheduled
One-shot routine created to verify whether the sustained-MAJOR anti-pattern recurs in the next 14 days:
- Routine ID: `trig_01JLExxhtAtsmBxmNE8oK112`
- Fires: **2026-05-07 10:00 AM CDT (2026-05-07T15:00:00Z)**
- Model: `claude-sonnet-4-6`
- Manage: https://claude.ai/code/routines/trig_01JLExxhtAtsmBxmNE8oK112

The agent branches:
- **Recurrence found** → drafts `scripts/enforcement/check-review-major-streak.sh` (modeled on `check-harness-file-size.sh`) + updates `.claude/rules/README.md`, opens a DRAFT PR.
- **No recurrence** → comments on the most recent open issue that Level-2 promotion can be deferred.

## What is NOT done (intentional, low-risk)
- The approval-binding pattern (project memory #3) was NOT promoted into `docs/standards/` because that's authoritative-governance scope; memory placement is sufficient until repeated cross-phase application justifies a standard.
- Hermes model switch observation (`gpt-5.5` on most recent session vs prior `gpt-5.4` default) was NOT captured as memory — treated as operational observation rather than durable learning.
- ~16 background/exit-hook Claude sessions with empty bodies were not inspected further.
- Pre-2026-04-22 sessions (Claude sessions 2026-04-11 through 2026-04-21) were not full-scanned; the existing 40+ auto-memory feedback files cover that window based on memory file mtimes.

## Follow-up work queue
- Monitor the 2026-05-07 routine firing; review the draft PR or deferral comment it produces.
- If the recurrence-guard script lands, consider Level-3 promotion (pre-push hook) once the script has fired on ≥2 real PRs without false positives, per `.claude/rules/patterns.md` enforcement gradient.
- Outstanding worldenergydata CI lanes (from #2460 scope cleanup): **#2467** (flake8 pathological blocker — marine_safety/_cross_database_data.py quarantine/normalize), **#2468** (safe-rule first-wave cleanup — F401/E501/E402 outside the blocker), **#2469** (final green-gate verification).

## Exit conditions
- `git status` clean on my authored changes — commit `8e2236d7d` pushed (confirmed via prior commit log).
- No in-flight subagents; no pending user-in-loop gates from this session's work.
- Other modified/untracked files observed during the sweep (auto-sync artifacts, parallel-session plan drafts, review results for #2441/#2475/#2476) are from parallel work lanes, NOT this session — left untouched.

## Resume instructions
If the 2026-05-07 routine produces a draft PR, review it like any enforcement script: confirm the streak-counting logic handles edge cases (missing provider files, non-numeric `r` suffixes, tie-case verdicts), run the script against `scripts/review/results/` as-is to confirm it doesn't false-positive on current data, and merge if clean. If the routine posts a deferral comment, no action needed — the prose rule continues to do its job.
