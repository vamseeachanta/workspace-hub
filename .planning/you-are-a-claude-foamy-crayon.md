# Claude plan-review — security runbooks (#2550, #2552)

> Lane: provider-capacity-aware-20260501-1334 / Claude long-context plan-review
> Date: 2026-05-01
> Repo: vamseeachanta/workspace-hub

---

## ENV-MISMATCH BANNER (read first)

The lane prompt prescribed the result path:

```
/mnt/local-analysis/agent-logs/provider-capacity-aware-20260501-1334/results/claude-plan-review-security-runbooks.md
```

That path is **outside this session's read/write sandbox**, which is scoped to `/mnt/local-analysis/workspace-hub`. An `ls` of the prescribed directory was rejected by the harness with: *"For security, Claude Code may only list files in the allowed working directories for this session"*. Plan mode is also active, further restricting writes to one specified file inside the workspace.

Per the durable mitigation in `feedback_lane_result_path_outside_sandbox.md`, this report has been canonicalized at the only writable target (`/mnt/local-analysis/workspace-hub/.planning/you-are-a-claude-foamy-crayon.md`). The orchestrator should either:

1. Copy this file to the prescribed path, or
2. Rerun the lane with `/mnt/local-analysis/agent-logs` added to the read/write sandbox roots, or
3. Update the lane spec to land results under `docs/sessions/` inside the workspace.

No GitHub mutations were performed. No labels touched. No approval markers created. Only this single file was written.

---

## Executive verdict

| Issue | State | Net verdict | Approval-ready? | Blocking signature |
|---|---|---|---|---|
| #2550 — codify public repo interaction-limit renewal | OPEN, `status:plan-review` | **NOT approval-ready** | No | Codex MAJOR (2 substantive blockers) ∧ Gemini MINOR |
| #2552 — external contributor & paid-help runbook | OPEN, `status:plan-review` | **NOT approval-ready** | No | Codex MAJOR (1 substantive blocker) ∧ Gemini APPROVE |

Both issues have **valid current evidence** (no UNAVAILABLE, no zero-byte, no stale-workspace pollution in the latest round) but **each carries a substantive Codex MAJOR that is not yet patched**. Recommendation: tighten plan text on the named blockers, then run a single fresh Codex+Gemini fanout. No self-approval, no label flip until that fanout returns no MAJOR.

Provider-tooling health snapshot for this round:
- **Codex CLI:** v0.125.0 — clear of the 0.124.0 stdin-hang regression (`feedback_codex_cli_0_124_upstream_regression.md`). Codex evidence here is uncompromised. Sandbox bubblewrap warning visible (`bwrap: loopback: ... Operation not permitted`) but only affected an internal SKILL read; the verdict body parsed cleanly.
- **Gemini CLI:** ran with agent-loading warnings (`Unrecognized key(s) in object: 'permissionMode'` for `gsd-debugger` / `gsd-executor` agents) but the review body returned substantive verdicts. Worth a follow-up for `.gemini/agents/*.md` schema drift, but doesn't degrade the round.
- **Disagreement reports** (`scripts/review/results/2026-04-29-plan-2550-disagreement.md`, `…2552-disagreement.md`): both are **stale**. They captured an earlier round in which Claude/Codex were UNAVAILABLE/UNKNOWN and Gemini's MAJOR rested on **false-positive "missing file" claims** that were the *reason* the plans were patched. Do not use these as current evidence.

---

## #2550 — codify public repo interaction-limit renewal in scheduled tasks

### Live state

- **Labels:** `enhancement`, `priority:medium`, `cat:operations`, `domain:automation`, `domain:security`, `status:plan-review`
- **Plan artifact:** `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md` (21,078 bytes; 2026-05-01 02:16 mtime — patched after 2026-04-30 review feedback)
- **Approval marker:** `.planning/plan-approved/2550.md` absent (verified by Codex postpatch prompt)
- **Review artifacts (canonical slot, current round):**
  - Claude: `scripts/review/results/2026-04-29-plan-2550-claude.md` (12,985 B; single-author canonicalized) — MINOR_PATCH_NEEDED, patches landed
  - Codex postpatch: `scripts/review/results/2026-04-30-plan-2550-codex-postpatch.md` (30,820 B) — **MAJOR / not-approval-ready**
  - Gemini postpatch: `scripts/review/results/2026-04-30-plan-2550-gemini-postpatch.md` (3,094 B) — MINOR / approval-ready-with-minor-notes
- **Older / superseded:** `2026-04-29-plan-2550-disagreement.md` (stale, false-positive Gemini findings); `2026-04-30-plan-2550-{codex,gemini}-final.md` (round 2, both MAJOR; superseded by postpatch round)

### Codex postpatch MAJOR findings (must be patched before rerun)

**F1 — `logs/security/` directory creation may run too late for the scheduler.**
> Evidence: AC says *"Script creates `logs/security/` before writing reports/logs so failure redirection cannot fail due to a missing directory."* Schedule entry also requires a `log` field.
> Impact: If the scheduled-task runner opens the configured `log` path **before** invoking the script, the script's internal `mkdir -p "$REPO_ROOT/logs/security"` happens too late. Prior blocker re-fires.
> Required fix: name a scheduler-safe mechanism — either (a) tracked placeholder `logs/security/.gitkeep`, or (b) put `mkdir -p logs/security && bash scripts/security/renew-interaction-limits.sh ...` directly in the `command` field of `schedule-tasks.yaml`. Plan must commit to one explicitly.

**F2 — Hermes cron decommission AC depends on a future scheduled run.**
> Evidence: *"After the new `github-interaction-limit-renewal` task fires successfully on its first scheduled run AND a follow-up `--check` cycle confirms expected behavior, remove the Hermes cron `d9b2d1c2270d`…"*
> Impact: Issue completion now hinges on a calendar event possibly months out (next cron firing under the `0 2 1 1,6,11 *` cadence). Mixes implementation acceptance with post-deployment ops follow-up. Also leaves Hermes dependency live after implementation, contradicting the deliverable's *"without Hermes-local cron dependency"* claim.
> Required fix: pick one — either (a) make decommission executable in this tranche after a manual `--dry-run` + live + `--check` sequence (deliverable-consistent path), or (b) explicitly defer Hermes removal to a new follow-up issue and remove it from this AC list. The plan must not depend on a future scheduled firing for closure.

### Gemini postpatch MINOR finding

- Pytest wrapper tests + bats integration tests both stub `gh` on `$PATH`; redundant. Suggested consolidation to bats only. **Non-blocking** — leave as a notes-on-approval item, not a blocker.

### Blockers list for #2550

1. F1 (Codex MAJOR) — scheduler-safe `logs/security/` creation
2. F2 (Codex MAJOR) — Hermes decommission timing/scope ambiguity
3. (Optional) Gemini MINOR — bats-only test consolidation

### Independent rerun needed?

**Yes — single fresh fanout after F1+F2 patches land.** Codex's MAJOR is substantive and grounded. With Codex v0.125.0 stable and Gemini already at MINOR, a clean rerun with both providers no-MAJOR is achievable in one cycle.

### Exact next safe operator commands (no mutations)

```bash
# 1. Re-confirm live label and approval-marker state (read-only).
gh issue view 2550 --json state,labels --jq '.labels[].name'
ls .planning/plan-approved/2550.md 2>/dev/null || echo "absent"

# 2. Inspect current postpatch evidence (read-only).
sed -n '1,40p' scripts/review/results/2026-04-30-plan-2550-codex-postpatch.md
sed -n '1,40p' scripts/review/results/2026-04-30-plan-2550-gemini-postpatch.md

# 3. Inspect the two AC lines flagged by Codex (read-only).
grep -n 'logs/security' docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
grep -n 'first scheduled run' docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
```

The control plane should **NOT**: flip the label, write `.planning/plan-approved/2550.md`, or post an approval-ready comment. Per `feedback_never_offer_to_self_label_plan_approved.md`, the user-in-loop gate must hold across session boundaries.

### Comment text the control plane MAY post (read-only operator action, no label change)

> Plan-review status update (2026-05-01 lane): NOT approval-ready. Codex postpatch (`scripts/review/results/2026-04-30-plan-2550-codex-postpatch.md`) returned MAJOR with two substantive blockers — (F1) `logs/security/` creation must be scheduler-safe (place `mkdir -p` in the `schedule-tasks.yaml` `command` field, or commit a `logs/security/.gitkeep`), and (F2) Hermes cron decommission AC currently depends on a future scheduled firing months out, mixing implementation acceptance with post-deployment ops. Gemini postpatch (`…-2550-gemini-postpatch.md`) returned MINOR (bats/pytest test redundancy, non-blocking). Recommend: patch plan on F1+F2, then rerun a single Codex+Gemini fanout. No self-approval; label remains `status:plan-review`.

---

## #2552 — external contributor and unsolicited paid-help response runbook

### Live state

- **Labels:** `documentation`, `priority:medium`, `cat:documentation`, `domain:security`, `status:plan-review`
- **Plan artifact:** `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md` (18,958 bytes; 2026-05-01 02:16 mtime — patched after 2026-04-30 review feedback)
- **Approval marker:** `.planning/plan-approved/2552.md` absent (verified by Codex postpatch prompt)
- **Review artifacts (canonical slot, current round):**
  - Claude: `scripts/review/results/2026-04-29-plan-2552-claude.md` (12,961 B; single-author canonicalized) — MINOR_PATCH_NEEDED, patches landed
  - Codex postpatch: `scripts/review/results/2026-04-30-plan-2552-codex-postpatch.md` (25,827 B) — **MAJOR / not-approval-ready**
  - Gemini postpatch: `scripts/review/results/2026-04-30-plan-2552-gemini-postpatch.md` (2,265 B) — APPROVE / approval-ready (no findings)
- **Older / superseded:** `2026-04-29-plan-2552-disagreement.md` (stale, false-positive Gemini findings); `2026-04-30-plan-2552-{codex,gemini}-final.md` (round 2, both MAJOR; superseded by postpatch round)

### Codex postpatch MAJOR finding (must be patched before rerun)

**F3 — README contact-path AC is too soft to substantively close the prior blocker.**
> Evidence: plan AC says *"`README.md` has a concise public-facing pointer ... including the off-GitHub contact route or a link to the runbook"*. The structural test only asserts: `external-contributor-runbook` or `external contributor` plus a contact-path *phrase*.
> Impact: A worker can satisfy this with vague text or a repo-local link without publishing a real off-GitHub contact mechanism. Legitimate contributors still have no usable route while `collaborators_only` blocks GitHub interaction. The prior MAJOR blocker (missing public-facing off-GitHub contact path) is **only partially resolved**.
> Required fix: name the required contact route explicitly, or require a concrete placeholder format approved by the owner — e.g. `contact: <specific email | contact form URL | website path>`. The README AC and the `test_readme_external_contributor_pointer` test must assert that **concrete value** (or a regex matching `mailto:`/`https://` and the owner-provided string), not merely the presence of a "contact-path phrase."

### Gemini postpatch verdict

- APPROVE / approval-ready, no findings. Both prior MAJOR blockers (permanent CI test for historical plan-index row; missing README contact path) flagged as resolved.

### Blockers list for #2552

1. F3 (Codex MAJOR) — concrete README contact-route specification

### Independent rerun needed?

**Yes — single fresh fanout after F3 patch lands.** Gemini already approves; the only outstanding signal is the Codex MAJOR. The fix is a small, targeted plan-text edit (specify the exact contact route + tighten the test regex). One additional Codex+Gemini cycle should resolve it.

Note: Per the plan's own front-matter, an alternative path exists — *"T1 deferred-review approval candidate only if user explicitly accepts single-author Claude evidence"*. This path is on the table for a T1 documentation-only issue if the user explicitly waives cross-provider evidence; however, given Codex IS available and HAS substantively MAJOR'd this round, defaulting to the deferred-review path would mean knowingly approving a plan with an open Codex blocker. **Recommend: do NOT use the T1 deferred-review path here.** Patch F3 and rerun.

### Exact next safe operator commands (no mutations)

```bash
# 1. Re-confirm live label and approval-marker state (read-only).
gh issue view 2552 --json state,labels --jq '.labels[].name'
ls .planning/plan-approved/2552.md 2>/dev/null || echo "absent"

# 2. Inspect current postpatch evidence (read-only).
sed -n '1,40p' scripts/review/results/2026-04-30-plan-2552-codex-postpatch.md
sed -n '1,40p' scripts/review/results/2026-04-30-plan-2552-gemini-postpatch.md

# 3. Inspect the AC line flagged by Codex (read-only).
grep -n 'README.md has a concise public-facing pointer' docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md
grep -n 'test_readme_external_contributor_pointer' docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md
```

The control plane should **NOT**: flip the label, write `.planning/plan-approved/2552.md`, post an approval-ready comment, or invoke the T1 deferred-review path while a Codex MAJOR is open.

### Comment text the control plane MAY post (read-only operator action, no label change)

> Plan-review status update (2026-05-01 lane): NOT approval-ready. Codex postpatch (`scripts/review/results/2026-04-30-plan-2552-codex-postpatch.md`) returned MAJOR with one substantive blocker — F3, the README contact-path AC and `test_readme_external_contributor_pointer` test allow a worker to satisfy them with a vague phrase rather than a real off-GitHub contact route, leaving the prior blocker only partially resolved. Gemini postpatch (`…-2552-gemini-postpatch.md`) returned APPROVE with no findings. Recommend: tighten the README AC + test to assert a concrete owner-provided contact route (email/contact form/website URL), then rerun a single Codex+Gemini fanout. T1 deferred-review path is **not** recommended here because a substantive Codex MAJOR is open. No self-approval; label remains `status:plan-review`.

---

## Cross-cutting observations

1. **Plan vs review chronology is clean.** Both plans show 2026-05-01 02:16 mtimes (likely a sync touch) but their text body embeds the post-patch state — empty-list guards, archived-repo filters, 404-as-unset handling, single-machine cadence, decommission cutover steps for #2550; tightened README/test ACs for #2552. The 2026-04-30 postpatch reviews quote the patched plan text verbatim in their `## Current plan text under review` blocks, confirming the reviews are current. This passes `feedback_plan_past_tense_artifact_claims.md`.

2. **No `feedback_codex_sustained_major_loop.md` trigger.** That memory only fires at v3+ rounds of Codex MAJOR while Claude+Gemini are MINOR by v3. Round count for both issues is 2 (final + postpatch). Patch-and-rerun is the right move; consensus-vs-minority surfacing is premature.

3. **The 2026-04-29 disagreement files are misleading and should be ignored.** Both name "Hallucinated Evidence Document" / "false assertion: file is missing" findings against `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`. That handoff **does** exist (the plans' Resource Intelligence sections quote from it; the postpatch reviews cite it without contradiction). The 2026-04-29 round was Gemini reading a stale workspace, exactly per `feedback_gemini_sandbox_overlay_blindness.md`. The 2026-04-30 postpatch reviews correctly inspect the current checkout.

4. **Gemini agent-loading errors deserve a separate follow-up.** Both Gemini postpatch artifacts open with: *"Failed to load agent from `.gemini/agents/gsd-debugger.md`: Validation failed: Unrecognized key(s) in object: 'permissionMode'"*. The reviews still produced verdicts, but agent-loading drift in the `.gemini/agents/*.md` schema is a latent quality risk for future Gemini lanes. Worth a small standalone issue.

5. **No secrets observed.** None of the read artifacts contained credentials, tokens, or PII. Nothing to redact.

---

## Summary recommendation for the orchestrator

| Action | Issue | Authorization needed |
|---|---|---|
| **Read-only operator comment** posting the per-issue blocker summary above | #2550, #2552 | Yes (user-approved); read-only-style update without label change |
| **Plan text patch** on F1 + F2 | #2550 | User authorization to edit plan |
| **Plan text patch** on F3 | #2552 | User authorization to edit plan |
| **Fresh Codex+Gemini fanout** against patched plans | both | After patches land |
| **Label flip to `status:plan-approved`** | both | Hard NO until fanout returns no MAJOR; user must do this, not an agent |
| **`.planning/plan-approved/{2550,2552}.md` markers** | both | Hard NO until same gate passes |
| **T1 deferred-review path for #2552** | #2552 | Not recommended while Codex MAJOR is open |

**Round 3 should resolve both.** F1/F2/F3 are scoped, well-defined, and all three are plan-text-only edits — no implementation needed before rerun.
