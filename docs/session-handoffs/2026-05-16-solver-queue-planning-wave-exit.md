# Session exit — solver-queue planning wave (#2708-#2711 + follow-ups)

**Span:** 2026-05-14 → 2026-05-16 (single Claude session, opus-4-7-1m, explanatory style)
**Triggering ask:** "review gh issue where we can set off a batch file on licensed-win-1 from any other machine" → broadened to "run AQWA and OrcaFlex analyses as needed from any machine with a prompt and submission of files" + "add data from service providers such as Helix"

---

## Outcome at a glance

| Plan | Issue | Final commit | Status label | Disposition |
|---|---|---|---|---|
| A — OrcaFlex live validation | [#2708](https://github.com/vamseeachanta/workspace-hub/issues/2708) | `9c675ad4a` | `status:plan-review` | Awaiting user approval (r3-inline-loop-break applied) |
| B — AQWA runner adapter | [#2709](https://github.com/vamseeachanta/workspace-hub/issues/2709) | `6f7a25c7d` | (none — at `draft`) | **HALTED** pending [#2717](https://github.com/vamseeachanta/workspace-hub/issues/2717) live AQWA baseline |
| C — Solver-submit UX (skill + CLI) | [#2710](https://github.com/vamseeachanta/workspace-hub/issues/2710) | `57524495f` | `status:plan-review` | Awaiting user approval (r3 inline rework — duplicate-validation defect ripped) |
| D — Helix 15k IRS provider-data pilot | [#2711](https://github.com/vamseeachanta/workspace-hub/issues/2711) | `6d97c7422` | `status:plan-review` | Awaiting user approval (r2 MINOR fold-in; cleanest plan of the wave) |

**Follow-up issues filed:**
- [#2713](https://github.com/vamseeachanta/workspace-hub/issues/2713) — `infra: gemini 0.42.0 headless mode reports run_shell_command not found — blocks cross-review`
- [#2717](https://github.com/vamseeachanta/workspace-hub/issues/2717) — `infra: live AQWA env access on licensed Windows host — prerequisite for #2709`

**Memory entries added:**
- `feedback_retry_loop_sweep_contamination` — retry-loop commits can sweep parallel-session staged files; pathspec form (`git commit -m "..." -- <file>`) prevents
- `feedback_r1_review_trust_hazard` — before applying an r1 fix asserting a gap, independently verify the asserted-missing surface; reviewers selectively quote

---

## Where to pick up

### User decisions outstanding

For each of A, C, D — when ready to approve:

```bash
gh issue edit <N> --remove-label "status:plan-review" --add-label "status:plan-approved"
mkdir -p .planning/plan-approved
echo "Approved by: <user>" > .planning/plan-approved/<N>.md
```

After both label + marker exist for any plan, the next agent can begin TDD execution per planning-mode Step 6.

**Per `feedback_never_offer_to_self_label_plan_approved`, no agent will self-apply `status:plan-approved`.**

### Plan B unblock path

Plan B stays at `draft` until [#2717](https://github.com/vamseeachanta/workspace-hub/issues/2717) produces:
1. AQWA executable path on Windows (NOT `Framework/bin/Win64`; the AQWA binary is at `v*/aqwa/bin/winx64/aqwa.exe` or `aqwa_le.exe`)
2. Exact CLI invocation shape that succeeds on a known-good `.dat`
3. Real `.lis` AND `.mes` content samples (success + deliberate failure)
4. `ANSYSLMD_LICENSE_FILE` requirement for headless invocation
5. `ANSYS_INSTALL_DIR` semantics that resolve correctly to AQWA

When that lands, re-ground `docs/plans/2026-05-14-issue-2709-aqwa-runner-adapter.md` §Resource Intelligence Summary against the empirical artifact and re-dispatch r3 review.

---

## Adversarial-review wave summary

| Round | A | B | C | D |
|---|---|---|---|---|
| r1 | MAJOR (Claude) — 3 blockers + 7 MINOR | MAJOR (Codex) — 7 blockers | MAJOR (Codex) — 5 blockers | MAJOR (Codex) — 7 blockers |
| r1 Gemini | n/a (T1) | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE |
| r2 | MAJOR (Claude) — 15 fresh, non-overlapping | MAJOR (Claude fallback) — 13 findings, 8 blockers | MAJOR (Claude fallback) — 12 findings, 4 blockers | **MINOR (Claude fallback)** — 12 findings, 0 blockers |
| r2 Codex | n/a (T1) | UNAVAILABLE (stdin-hang, #2713-class) | UNAVAILABLE | UNAVAILABLE |
| Final | r3 inline-loop-break | Halt pending [#2717](https://github.com/vamseeachanta/workspace-hub/issues/2717) | r3 inline rework | r2 MINOR fold-in |

**Total defects caught before any implementation:** 27 r1 blockers + 32 r2 findings (including 12 blockers across A/B/C). Cost: ~14 adversarial-review dispatches across 2 rounds. None of this work touched production code.

---

## Surprises and lessons that landed durably

1. **Codex CLAUDECODE-guard requires `env -u CLAUDECODE`** — per [#2684](https://github.com/vamseeachanta/workspace-hub/issues/2684) guard, `codex exec` returns UNAVAILABLE when `CLAUDECODE=1`. Workaround works for r1; r2 hit a *different* failure (stdin-hang on plans >~30 KB, per [#2713](https://github.com/vamseeachanta/workspace-hub/issues/2713)) which the workaround does not cover.

2. **Gemini 0.42.0 returns UNAVAILABLE in headless mode** — "Tool 'run_shell_command' not found" with hint listing a different tool registry. Tracked at [#2713](https://github.com/vamseeachanta/workspace-hub/issues/2713). Cross-review fanout falls back to single-author with transparent provenance per `feedback_permission_gate_blocks_cross_review`.

3. **Retry-loop commit swept in 75 parallel-session files** — commit `9d9c6e4c7` (Plan A r1 revision) is the contaminated bystander. Auto-sync pushed before recovery was possible. Subsequent commits used `git commit -m "..." -- <file>` pathspec form to prevent re-occurrence. Memory captured.

4. **r1 reviewer asserted a gap that didn't exist** — Plan C r1 Codex said `submit-job.sh` lacks input-file existence check. It has had one since the original commit `71a53898b`. r1 revision trusted the finding and added a duplicate-validation block — violating the issue's own AC 5. r2 Claude caught it. r3 inline rework ripped the duplicate. Memory captured.

5. **r1 + r2 surface DIFFERENT defects each round (Plan A)** — qualifies for `feedback_r3_inline_loop_break_pattern` (apply r3 inline patches without dispatching r3 review). 15 r2 findings absorbed into the plan via single Write.

6. **Empirical-grounding gap is structural, not documentation (Plan B)** — two rounds of revision caught increasingly sophisticated defects in the same area (AQWA invocation contract). Reviewer's closing diagnosis: "Until the live smoke validation actually runs once and is captured, the probe and scrape logic is speculation." Halt + prerequisite issue is the right move; another revision round would only produce polished speculation.

---

## Files of record (this session)

**Plans (all under `docs/plans/`):**
- `2026-05-14-issue-2708-orcaflex-live-validation.md` (r3-inline)
- `2026-05-14-issue-2709-aqwa-runner-adapter.md` (halted at draft)
- `2026-05-14-issue-2710-solver-submit-ux.md` (r3 inline rework)
- `2026-05-14-issue-2711-helix-provider-data-pilot.md` (r2 MINOR folded)

**Review artifacts (under `scripts/review/results/`):**
- `2026-05-14-plan-{2708,2709,2710,2711}-{claude,codex,gemini,disagreement}.md` (r1 round)
- `2026-05-15-plan-{2708,2709,2710,2711}-{claude,codex,disagreement}.md` (r2 round)

**Memory (under `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/`):**
- `feedback_retry_loop_sweep_contamination.md`
- `feedback_r1_review_trust_hazard.md`
- `MEMORY.md` updated with index entries for both

---

## What this session did NOT do

- No production code changes — every commit is to plans, docs, or review artifacts.
- No `status:plan-approved` self-labels — explicit user-in-loop gate per `feedback_never_offer_to_self_label_plan_approved`.
- No implementation of A/B/C/D — all four await user approval (or, for B, the [#2717](https://github.com/vamseeachanta/workspace-hub/issues/2717) prerequisite).
- No commits to files outside this session's scope (per `feedback_retry_loop_sweep_contamination`, pathspec form scoped each commit to its named plan file).

---

## Repo state at exit

`docs/plans/` revisions committed via pathspec form; nothing dirty in this session's scope. Other dirty files (`config/ai-tools/*`, `docs/reports/*`) belong to parallel sessions and were intentionally not staged or committed by this one.

Auto-sync has pushed all 9 of this session's commits to `origin/main` per `feedback_autosync_silent_pusher`. Verifiable via `git log origin/main..HEAD --oneline` → empty.
