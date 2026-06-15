---
name: project-gtm-daily-reanalysis-routine
description: Remote daily routine (trig_01LHnPhwG7WZcsdNCMsKJFst) reanalyzes the 3 GTM threads at 11:00 UTC with full-execution-but-bounded-merge authority — parallel sessions must expect its writes
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b7b8f68-73fa-4802-bb93-a0f9051308b9
---

Created 2026-06-06: remote CCR routine **gtm-daily-reanalysis** (`trig_01LHnPhwG7WZcsdNCMsKJFst`, manage at https://claude.ai/code/routines/trig_01LHnPhwG7WZcsdNCMsKJFst), cron `0 11 * * *` UTC (6 AM Chicago CDT), model sonnet-4-6, no MCP connectors (Gmail deliberately stripped). Clones aceengineer-strategy, llm-wiki, deckhand, workspace-hub, digitalmodel.

**Prompt v2 deployed 2026-06-07** (effective from 06-08 run) after run-1/2 review: (a) FRESHNESS-FIRST — provisioned clones proved stale (journal merged 6 min before run #1 was invisible → Thread A skipped), v2 fetches origin/main per repo + gh-api file fallback; (b) one-time actions moved to a COMPLETED-LEDGER (verify-only, never recreate) instead of search-guarded re-execution; (c) digitalmodel added as 5th source (run #1's #632 comment failed — remote token only covers source repos); (d) issue #52 BODY = edit-in-place gate dashboard, comments = delta-first ≤40-line dailies; (e) minimal report even on fatal error. Run #1 published flywheel #51–#59, merged llm-wiki#402 + PR#49, opened PRs #60/#61/#62; run #2 (06-07, old prompt) = zero duplicates, all dedup held. Collide handoff doc published to workspace-hub main via gh-api PR #2961 (was local-only on fix/track-fleet-skills-2925-portable).

Daily it works three threads: (A) Open Deck exit-handoff pending actions ([[project_open_deck_outreach_exp003]]), (B) content→outreach flywheel ([[project_content_outreach_flywheel]]), (C) Collide→outreach mapping. Branches `gtm-daily/<date>-<slug>` from origin/main; reports as one comment/day on ace-strategy issue "GTM daily reanalysis log (Open Deck / flywheel / Collide)" incl. BLOCKED-ON-VAMSEE asks + gate table.

**Authority bounds:** never sends outreach; Intermoor #30 send-ready only on VA's explicit deck-grade comment; EXP-002 ≤3-canary gate honored; merge authority = llm-wiki #402 + strategy #49 + its own prior-day PRs VA approved; its same-day PRs stay open for review.

**VA's 4 flywheel answers (recorded 2026-06-06, baked into routine prompt):** merge slices 6+7 → 7 content issues; all in ace-strategy; labels as the PR #49 plan doc proposed; YES Hanwha tracking issue. First run publishes the set, merges PR #49, comments epic link on digitalmodel#632.

**Why:** VA wants the GTM threads advanced daily without manual prompting; sessions touching these repos/issues should check the daily-log issue for the routine's recent writes before acting.

**How to apply:** before working strategy #25/#30–#36/#42–#48, deckhand #2/#22/#81/#82, llm-wiki #402, or the flywheel issues, read the latest comment on the "GTM daily reanalysis log" issue — the routine may have already done or queued the action. To change its behavior, update the routine prompt via RemoteTrigger (deletes only via claude.ai/code/routines).

**2026-06-07 exit handoff** → workspace-hub `docs/session-handoffs/2026-06-07-gtm-routine-review-and-pat-rotation-prep.md` (published via gh-api PR #2966; local push blocked on this host per [[feedback_prepush_hooks_sigpipe_and_sibling_layout]]). digitalmodel#632 epic-link comment + Collide handoff (workspace-hub PR #2961) both done. **deckhand#2 PAT rotation pinned to ace-linux-2** (new `host:ace-linux-2` label convention started — none existed before; run sheet = deckhand#2 comment 4645330367). **Non-obvious gotcha:** rotation touches TWO env files — `~/.hermes/deckhand/secrets.env` (shims, written by `scripts/deckhand/add-scope-pat.sh acma|lng-a`) AND `~/.hermes/.env` (read by `protect-and-verify.sh verify-pat`); update both or split-brain; still `hermes gateway restart` despite add-scope-pat's "no restart" note (gateway caches env separately from the per-invocation shims). On deckhand#2 close, routine flips EXP-002 broad-send gate ⚠️→✅ next run.
