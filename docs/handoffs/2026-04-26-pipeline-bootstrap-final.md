# Pipeline Bootstrap — Final State 2026-04-26

> **What this is:** end-of-session reference doc capturing the 10-routine self-sustaining issue-pipeline that was bootstrapped 2026-04-26.
> **Audience:** future sessions (and me when I return) that need to understand what's running and how to interact with it.
> **Replaces:** standalone session-close handoffs from 2026-04-25/26 (those remain in `docs/handoffs/` for history but this is the operating-state doc).

---

## TL;DR

```
            ┌──────────────────────────────────────────────────────────┐
            │   intake     →    plan-review    →    plan-approved      │
            │   (M items)       (N items)            (P items)         │
            └─────────┬────────────────┬──────────────────┬────────────┘
                      │                │                  │
                  Wed drafter      Sat-Sun user        Mon drainer
                  picks 2          approves            executes 1
                                                         │
                                                         ▼
                                                       PR open
                                                         │
                                                       Sat-Sun user
                                                         merges
                                                         │
                                                         ▼
                                                       status:done
```

Plus: Friday triage surfaces fresh intake candidates → Sunday digest summarizes the whole week's movement on `#2424`.

---

## Routine inventory (10 total)

| # | Name | Schedule | Type | Read/write |
|---|---|---|---|---|
| 1 | Execute #2443 achantas-data CI | one-shot 2026-04-26 14:00 UTC | one-time | r/w (target repo + workspace-hub closeout comment) |
| 2 | Execute #2444 aceengineer-admin CI | one-shot 2026-04-26 16:00 UTC | one-time | r/w |
| 3 | Execute #504 OrcaFlex buoys refactor (slices 2-8) | one-shot 2026-04-26 18:00 UTC | one-time | r/w |
| 4 | Plan-write #2479 Codex stdin-hang | one-shot 2026-04-27 14:00 UTC | one-time | w plan + comment + label transition |
| 5 | Plan-write #2490 coverage-gate | one-shot 2026-04-27 17:00 UTC | one-time | w plan + comment + label transition |
| 6 | Plan-write #534-#537 batch | one-shot 2026-04-28 14:00 UTC | one-time | w 1 unified plan + 4 comments + 4 label transitions |
| 7 | Weekly plan-drainer | Mondays 13:00 UTC (8 AM CT) | recurring | r/w (executes 1 status:plan-approved/week, opens PR or commits to main per plan) |
| 8 | Weekly plan-drafter | Wednesdays 13:00 UTC (8 AM CT) | recurring | r/w (drafts 2 plans/week → status:plan-review) |
| 9 | Weekly intake triage | Fridays 14:00 UTC (9 AM CT) | recurring | r/o + 1 comment on #2424 |
| 10 | Sunday queue-status digest | Sundays 14:00 UTC (9 AM CT) | recurring | r/o + 1 comment on #2424 |

Manage all routines: https://claude.ai/code/routines

---

## User-gate boundaries (preserved across all 10 routines)

Per `feedback_never_offer_to_self_label_plan_approved`, every routine respects these gates — none can be bypassed:

| Transition | Gate | Why |
|---|---|---|
| `status:plan-review → status:plan-approved` | **USER ONLY** — drafter sets plan-review, drainer never approves | adversarial-review + user judgment required |
| PR merge | **USER ONLY** — drainer opens PR, stops at `status:working` | reviewing changes is the user's job |
| `status:working → status:done` | **AUTO via `Closes` trailer** on user-merged PR | derived from merge event, not from agent action |
| Routine deletion | **USER ONLY** via https://claude.ai/code/routines | explicit cleanup |

Agents in this pipeline can:
- ✅ draft plans → set `status:plan-review`
- ✅ execute plan-approved → commit + open PR + set `status:working`
- ✅ post comments, file follow-up issues, close issues with `Closes` trailer

Agents cannot:
- ❌ self-approve a plan (set `status:plan-approved`)
- ❌ merge a PR
- ❌ self-label `status:done` independent of a PR merge
- ❌ skip adversarial review by routing directly to plan-approved

---

## Weekly cadence

**Routine schedule (Chicago time):**

| Day | Time | Routine | Output |
|---|---|---|---|
| Sun | 9 AM | queue-status digest | 1 comment on #2424 |
| Mon | 8 AM | plan-drainer | 1 PR or 1 direct-to-main commit |
| Wed | 8 AM | plan-drafter | 2 new status:plan-review issues |
| Fri | 9 AM | intake triage | 1 comment on #2424 |

**User cadence (interaction points):**

| When | Action |
|---|---|
| Sat or Sun morning | Read Friday triage + Sunday digest on #2424 |
| Sat or Sun morning | Review status:plan-review issues + approve the good ones |
| Sat or Sun afternoon | Merge any PRs the Monday drainer left open |
| Mid-week (optional) | If the digest shows YELLOW/RED pipeline health, investigate why |

If the user is fully AFK for a week:
- Plan-drainer skips its run if no `status:plan-approved` items exist (drained out)
- Plan-drafter still drafts 2 → backlog refills
- Triage + digest still post observability comments
- Pipeline self-throttles; resumes at full throughput when user returns

---

## Pipeline health signals (from the Sunday digest)

| Signal | Meaning | Action |
|---|---|---|
| 🟢 GREEN | drainer + drafter both moved this week | nothing to do |
| 🟡 YELLOW | one side stalled (e.g. drainer skipped due to parallel work, or drafter ran out of viable intake candidates) | check the digest's "Next Week Recommendations" section |
| 🔴 RED | nothing closed, nothing drafted | investigate routine errors at https://claude.ai/code/routines/{id} |

---

## What's NOT in the pipeline (and why)

- **Adversarial cross-review** — `scripts/review/plan-review-fanout.sh` requires local Codex CLI + interactive user judgment per finding. Manual workflow, not a fit for unattended routines.
- **PR review** — code review of the drainer's PR is the user's role. The drainer DOES spawn `pr-review-toolkit:code-reviewer` against its own diff before push (per `superpowers:requesting-code-review`), so user gets pre-reviewed PRs.
- **Roadmap planning / strategy** — the drafter picks tactical implementation issues, not strategic direction-setting.
- **Releases** — no release-cutting routine. Add one if release cadence becomes regular.
- **Dependency updates** — Dependabot handles dependency PRs; user merges manually. Could add a "weekly Dependabot sweep" routine if backlog grows.

---

## Routine prompts — content snapshot

For audit/review, the prompt for each recurring routine is reproduced here. Edit at https://claude.ai/code/routines/{id} if behavior needs to change.

### Plan-drainer (routine 7)
- Selection: parallel-work check first, then T1/T2 plan-approved, scored by priority + age
- Verifies plan currency before executing (spot-check 2-3 cited file paths)
- Spawns `pr-review-toolkit:code-reviewer` against diff before push
- T1 → direct-to-main with `Closes` trailer; T2 → PR + comment + leave at `status:working`
- HARD GUARDRAILS: never self-approve, never `status:done` without PR merge

### Plan-drafter (routine 8)
- Reads latest Friday triage report's "HIGH-PRIORITY PLAN-NEXT" section as input pool
- Picks 2 candidates covering DIFFERENT domains
- Drafts plans per `docs/plans/_template-issue-plan.md` structure with full Resource Intelligence pass
- Posts plan body as issue comment + sets `status:plan-review`
- HARD STOP at plan-review (never plan-approved)

### Intake triage (routine 9)
- Read-only survey of unstatus'd open issues
- Body-verified dup detection (NOT title-similarity)
- Conservative closure-candidate criteria (>21d stale + named obsolescence rationale)
- Output: single comment on #2424 with 5 sections + numeric summary

### Sunday digest (routine 10)
- Read-only weekly summary
- Week-over-week table parsed from prior Sunday's digest
- Pipeline-health verdict (GREEN/YELLOW/RED)
- Output: single comment on #2424

---

## Operational protocols (validated on #511 + #2441 this session, carry-forward)

1. **TDD MANDATORY** — failing tests first per slice, watch fail, write minimum impl, watch pass
2. **Atomic commits per slice** — one commit per logical change, message references the issue
3. **Stage + commit in same turn** — closes auto-sync history-split window
4. **Code review before push** — `pr-review-toolkit:code-reviewer` against diff
5. **Verify code review findings** — `superpowers:receiving-code-review` discipline (don't blindly fix)
6. **Plan-defect escalation** — if implementation reveals plan is wrong, STOP + post comment + don't silently re-plan
7. **NEVER `status:done` without user merge** — `feedback_never_offer_to_self_label_plan_approved`
8. **Verify branch state after commits** — `git rev-parse HEAD origin/<branch>` (auto-sync hazard)
9. **Check parallel work before heavy pytest** — `ps aux | grep "uv run"` (multi-session uv lock contention)
10. **Stash → fast-forward → pop on stale main** — pattern for committing to a repo where local main is behind origin

---

## Environmental hazards (validated this session)

- **Auto-sync silent push + history split** — `feedback_autosync_silent_pusher`. Mitigation: stage + commit in same turn, verify with `git rev-parse` post-commit.
- **Multi-session uv lock contention** — single-session work is the safe default. Scan for parallel `uv run` processes before heavy pytest.
- **Workspace-hub branch drift** — branch can switch from `main` to a feature branch silently mid-session. Always check `git branch --show-current` before workspace-hub commits.
- **First `uv run pytest` per session** recompiles bytecode (~1:40s — 4 min if env perturbed). Subsequent ~5s for schema/, ~14-17 min for full orcaflex/.
- **`tests/solver/` is OrcFxAPI-gated** via `conftest.py` auto-mark; new tests belong under `tests/solvers/orcaflex/modular_generator/...` (note plural `solvers`).
- **Title-similarity dup heuristics over-trigger** — agent flagged 10 cluster groups, ~6 were adjacent-not-dup at body level. Always verify dup pairs by reading bodies before closing.
- **Auto-close on commit-trailer** — `Closes vamseeachanta/<repo>#<n>` in commit body fires the auto-closer on push. Subsequent `gh issue close` calls hit no-op "already closed" — not an error, but label edits should happen BEFORE push.

---

## Recent session SHA reference card

| Where | SHA | What |
|---|---|---|
| digitalmodel main tip (post-session) | `85875f36` | `fix(#2441): add pylife>=2.2,<3.0 dependency + smoke import test` |
| digitalmodel main pre-#2441 | `481f17af` | Merge of #533 (#511 OrcaFlex campaign spec generation) |
| digitalmodel main pre-#511 | `b24857e9` | Merge of #532 (#510 test-drift repair) |
| digitalmodel `issue-504-buoys-builder-refactor` | (Slice 1 commit) | `_buoy_geometry.py` extracted; routine 3 fires today to ship slices 2-8 |
| workspace-hub main (this handoff) | (latest) | session-close handoffs + plan-approved markers + pipeline-bootstrap doc |

---

## What shipped this session (2026-04-24/25/26)

- ✅ #510 — OrcaFlex test-drift repair (PR #532 merged earlier)
- ✅ #511 — OrcaFlex campaign spec generation (PR #533 merged 2026-04-25; +31 tests, 0 regressions)
- ✅ #2441 — digitalmodel Quality Gates pylife dep (commit `85875f36` direct-to-main)
- ✅ 13 plan-review issues approved + markers committed
- ✅ #2251, #2477, #2358 closed (intake triage)
- ✅ #2490 filed (coverage-gate follow-up split from #2441)
- ✅ #534-#537 filed (4 #511 deferred minor follow-ups)
- ✅ 10 routines bootstrapped on https://claude.ai/code/routines

**Wave A status:** #510 done, #511 done, #504 mid-flight (Slice 1/8 done; routine 3 fires today to ship slices 2-8).

---

## When this doc becomes stale

Update or supersede when:
- Routine count changes (add/remove/disable)
- A routine's prompt changes materially
- A new user-gate boundary is added
- Pipeline-health signals consistently show YELLOW/RED (means the model is broken)
- Repo set changes (e.g., new repo joins the ecosystem)

For minor weekly state changes, the Sunday digest comment on #2424 is the authoritative weekly snapshot — no need to update this doc.
