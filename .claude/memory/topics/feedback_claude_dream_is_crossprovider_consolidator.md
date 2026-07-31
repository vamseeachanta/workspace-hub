> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-31
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_claude_dream_is_crossprovider_consolidator.md

---
name: feedback_claude_dream_is_crossprovider_consolidator
description: "User chose the Claude dream (not Hermes) as THE cross-provider memory consolidator; a bridge script distills Codex/Gemini/Hermes sessions into Claude's auto-memory dir"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e0c2082e-c5ec-4acf-bdbb-6163610bea88
---

2026-05-26 directive. The user wants Claude Code's **dreaming** (auto-memory consolidation) to take *all* providers' sessions into account — Codex, Gemini, Hermes — not just Claude's own.

**Why:** The native dream only ingests its own auto-memory store + its own `~/.claude/projects/*/*.jsonl` transcripts. `autoDreamEnabled` is a bare boolean — there is NO config knob for additional input paths. So cross-provider coverage requires a **bridge**: distill other-provider sessions into the Claude auto-memory dir (the one input the dream reads), and the dream then consolidates/dedupes/prunes them.

**How to apply:** Use `scripts/memory/distill-provider-sessions.py` (+ `bridge-providers-to-dream.sh`). It pre-filters sessions to conversational signal (Codex via `event_msg` stream; Gemini/Hermes via `messages[]`), batches them, distills durable learnings via **Claude itself — headless `claude -p --model haiku` on the subscription** (no API key; the .env `ANTHROPIC_API_KEY` is empty), and writes content-hashed `crossprovider_<provider>_*.md` files (idempotent). Daily cron at 04:00 for incremental; one-time `--backfill` for the ~10k-session history. Calls run from a neutral cwd to avoid reloading this repo's ~67K-token CLAUDE.md/MEMORY.md context each batch.

**Engine = Claude (NOT gpt-5.5/codex).** Initial choice was gpt-5.5/`codex exec` per [[feedback_hermes_no_openrouter_always_gpt55]], but (a) codex backfill was ~10-16 hr serialized + flaky ([[feedback_codex_cli_0_124_upstream_regression]]) and (b) the user said "let us get the claude to do the dreaming" (2026-05-26). So the engine is Claude on the subscription — dreaming is a Claude-native act, ONE consistent engine for all providers/sessions. The gpt-5.5 directive still governs *Hermes routing*, not this dream distiller.

**Tension to remember:** This PARTIALLY SUPERSEDES [[feedback_memory_aspire_to_hermes_level]] (everything-into-Hermes). The user's explicit 2026-05-26 choice: the **Claude dream is the cross-provider consolidator**, fed by the other three. Do not "correct" this back to Hermes-canonical — deliberate decision.

**STATE @ 2026-05-26 (for resume):** Built on branch `feat/2833-crossprovider-dream-bridge` (4 commits, pushed; commit `6f9557f`), issue [#2833](https://github.com/vamseeachanta/workspace-hub/issues/2833). Backfill COMPLETE all 3 providers (~3,059 `crossprovider_*.md` staged in auto-memory dir; Codex 696 / Gemini 413 / Hermes 1,950). Adversarial review done (REJECT→fixed→MINOR). Scorecard `docs/reports/2026-05-26-crossprovider-dream-bridge-completeness.html` (88%). Handoff doc `docs/sessions/2026-05-26-crossprovider-dream-bridge-handoff.html`. **Dreaming is AUTOMATIC — there is NO `/dream` command** (verified from binary: fires on minHours+minSessions+lock). PENDING (all automatic/time, nothing to invoke): background dream firing to consolidate the staged learnings; first live cron(04:00)+hook fire; then re-score→close #2833. NOT merged to main (review gate). Accepted residual: Codex/Hermes carry minor pre-fix CoT noise (user declined re-backfill).
