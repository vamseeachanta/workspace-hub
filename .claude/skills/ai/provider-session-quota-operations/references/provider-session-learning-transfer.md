# Archived Skill: `provider-session-learning-transfer`

Original path: `/home/vamsee/.hermes/skills/coordination/provider-session-learning-transfer`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/provider-session-learning-transfer`
Consolidation date: 2026-04-29

---

---
name: provider-session-learning-transfer
description: Refresh provider session audit, identify post-audit/unassessed sessions, extract actionable learnings, and transfer them into repo notes and GitHub issues before a follow-up implementation session.
version: 1.0.0
tags: [providers, sessions, audit, learnings, github, handoff, transfer]
---

# Provider Session Learning Transfer

Use when the user asks to assess recent AI-provider sessions and push the learnings into repo artifacts, issue trackers, or handoff notes.

## When to use
- "Assess recent/unassessed sessions"
- "Transfer learnings to the repo ecosystem"
- "Update issue notes before a dedicated Claude/Codex/Gemini session"
- "Review provider activity since the last audit/report"

## Core idea
Do not just read the existing provider audit and summarize it. First refresh the audit, then identify what happened after the prior audit timestamp, then transfer only the actionable findings into the target repo artifacts.

## Workflow

### 0. Prefer the tracked delta section when available
If the refreshed audit already includes a `recent_activity_since_previous_audit` executive-summary section, use it as the first-pass filter for which providers actually need deeper inspection.

Treat this as the canonical answer to:
- which providers had post-audit work
- how many post-hook records they produced
- how many runtime sessions they opened
- which recent Bash families / missing repo reads matter first

This avoids re-deriving the same cutoff analysis ad hoc each time.

### 1. Load existing provider audit artifacts
Read:
- `analysis/provider-session-ecosystem-audit.json`
- `docs/reports/provider-session-ecosystem-audit.md`

Capture the prior `generated_at` timestamp. This is the boundary for "unassessed" work.

### 2. Inventory provider log coverage
Check for `session_*.jsonl` under:
- `logs/orchestrator/claude/`
- `logs/orchestrator/codex/`
- `logs/orchestrator/hermes/`
- `logs/orchestrator/gemini/`

Do not assume every provider has recent work just because logs exist historically.

### 3. Refresh the audit before drawing conclusions
Run:
- `bash scripts/cron/provider-session-ecosystem-audit.sh`

Then reread the JSON/Markdown outputs and note the new timestamp plus changed metrics.

### 4. Identify truly unassessed work
Use the prior audit timestamp as cutoff and count records/sessions after that point for each provider.

Recommended output:
- provider
- records_after_prior_audit
- sessions_after_prior_audit

Important: this is the best quick test for whether Codex/Gemini/Claude/Hermes actually contributed anything new since the last audit.

Implementation note:
- Prefer the audit JSON if it actually exposes top-level delta blocks such as `recent_activity_since_previous_audit`.
- But do not assume those keys exist on every refresh. In live use, the refreshed JSON sometimes only contains `generated_at`, `repo_root`, `logs_root`, `providers`, and `executive_summary`, while the Markdown report still renders the recent-activity and corpus-change sections.
- Therefore, probe the JSON shape first. If those top-level delta blocks are absent, treat `docs/reports/provider-session-ecosystem-audit.md` as the authoritative recent-activity source and extract provider deltas from the Markdown headings/sections instead of concluding the data is unavailable.
- The per-provider objects under `providers.<provider>` may also omit the same delta structure even when the Markdown renders it, so keep Markdown and raw logs as the fallback truth for deeper drill-down.

### 5. Inspect only relevant recent sessions
Filter recent post-audit logs for the user’s target domain (for example tax, filing, issue planning, docs, etc.).

For domain filtering, inspect fields such as:
- `tool`
- `repo`
- `cmd`
- `file`
- `search_query`
- `skill_name`

Do not overfit to all provider activity. Extract the pattern that is actually reusable for the next session.

### 6. Derive the transferable learning
Prefer operational learnings, such as:
- packet-first workflow before live browser/tool session
- material blockers vs low-impact uncertainties
- explicit pre-submit checkpoints
- dedicated handoff prompt instead of restarting from memory
- binary go/no-go decision early in the next session

For provider-audit work specifically, separate two different stories:
1. true recent event-time activity since the prior audit
2. snapshot/corpus growth beyond recent activity (often export backfill or improved classification)

If a provider has little or zero recent event-time work but still shows large corpus growth or missing-read deltas, transfer that as a classification/export interpretation, not as a claim that the provider recently "did" that work.

Avoid dumping raw metrics into business notes unless the metrics themselves matter.

### 7. Transfer learnings into the repo ecosystem
Update both:
1. durable repo notes/docs in the target repos
2. the active GitHub issue(s) or tracker items that the next session will use

Good transfer targets:
- tax/session summary note
- strategy/decision note
- issue comment on the active filing/execution issue
- handoff prompt source file

### 8. Verify the transfer
Before finishing, verify:
- refreshed audit files are updated
- target repo files are modified in the intended locations
- GitHub comment/edit succeeded
- transferred learnings are framed as next-session execution guidance, not just retrospective commentary

### 9. Convert the top actionable transfer into the next planning gate when asked
If the user asks for the next logical step after a provider-learning transfer, do not automatically rerun the audit. Prefer converting the highest-priority concrete remediation issue into the next gate:
1. Pick the most actionable child issue, not the broad parent, using the refreshed report and issue state. Example: a concrete stale-reference cleanup child beats the parent migration-debt backlog.
2. Read the canonical plan and latest transfer bundle.
3. Reconcile the transfer into the plan only if it changes evidence, scope framing, or approval readiness. Avoid broadening the implementation branch when the transfer is only standing-risk/negative evidence.
4. Update the local plan status and planning index to `plan-review`.
5. Post a GitHub approval-gate comment via `--body-file`, add `status:plan-review`, and remove stale conflicting status labels.
6. Commit/push the exact plan-status changes, then verify both live GitHub labels/comments and remote `origin/main`.

Pitfall: workspace-hub often has concurrent writers and background git/status processes. If `.git/index.lock` appears, inspect live git processes first, remove only stale locks, and re-run `git status`. If `git push` reports a remote ref-lock rejection but `git ls-remote origin refs/heads/main` already equals local `HEAD`, treat the push as effectively landed after verification instead of retrying blindly.

## Heuristics that worked well

If you rerun `bash scripts/cron/provider-session-ecosystem-audit.sh` after drafting or posting transfer notes, immediately re-read `analysis/provider-session-ecosystem-audit.json` / `docs/reports/provider-session-ecosystem-audit.md` and patch the transfer report plus posted issue comments to the final `generated_at` value. Timestamp drift between the audit, durable report, and issue comments makes future "unassessed since boundary" work ambiguous.

When committing/pushing the transfer, verify remote state after any odd push error. A push can report a remote ref-lock rejection like `cannot lock ref ... is at <new> but expected <old>` even when the remote has advanced to the just-created commit. Before retrying or rebasing, run `git rev-parse HEAD` and `git ls-remote origin refs/heads/main`; if both match, treat the push as successful and avoid unnecessary conflict recovery.

## Heuristics that worked well
- If recent Codex/Gemini counts are zero after the prior audit, say so explicitly and focus on the providers with real post-audit work.
- The most useful learnings may come from one provider’s recent workflow even when the task asked for “all providers”.
- For filing work, the reusable pattern is usually about session structure and evidence gating, not tax law interpretation.

## Recommended transfer format for tax/session work
Add a short section like:
- Cross-provider learnings transfer — <date>

Include:
1. packet-first filing workflow
2. material blockers list
3. explicit reconciliation/pre-submit checkpoints
4. dedicated handoff prompt requirement
5. first-decision binary: finish now vs extension/triage

## Pitfalls
- Do not rely on stale audit outputs without rerunning the audit.
- Do not assume “recent provider activity” means all providers contributed recently.
- Do not bury the actual next-session guidance inside audit statistics.
- Do not update only docs and forget the active GitHub issue the operator will actually open next.
