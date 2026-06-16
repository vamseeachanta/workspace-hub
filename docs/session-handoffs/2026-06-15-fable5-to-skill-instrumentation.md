# Session Handoff — 2026-06-15: Fable-5 parity → skill-invocation instrumentation

## Origin
Started from: *"identify the gh issue used to assess Fable 5 sessions; can we get further enhancement to the repo ecosystem using the sessions"* + a video (*Make ANY Model Think Like Fable*). Evolved into building the skill-usage measurement foundation that unblocks skill cleanup.

## The Fable-5 assessment issue (the original question)
- **[#3056](https://github.com/vamseeachanta/workspace-hub/issues/3056)** — "analyze the Fable-5 session corpus" (CLOSED), under epic **[#3043](https://github.com/vamseeachanta/workspace-hub/issues/3043)** (model parity Opus⇄Fable). Report: `analysis/2026-06-13-fable5-opus-parity-learning.md`.

## What shipped (MERGED to main)
| Issue | PR | What |
|---|---|---|
| [#3109](https://github.com/vamseeachanta/workspace-hub/issues/3109) | #3115 | External HF Fable-5 corpus (~65 sessions) validates #3056 deltas out-of-sample |
| [#3112](https://github.com/vamseeachanta/workspace-hub/issues/3112) | #3134 | Skill-invocation chain: emit + short_name join + dashboard wiring (3 bugs) |
| [#3139](https://github.com/vamseeachanta/workspace-hub/issues/3139) | #3147 | Shared `_skill_identity.py` (one universe + key; `_archived` collision fix) |
| [#3137](https://github.com/vamseeachanta/workspace-hub/issues/3137) | #3150 | Skill-tool capture (id→short_name; live-firing runtime-unverified) |
| [#3138](https://github.com/vamseeachanta/workspace-hub/issues/3138) | #3151 | Transcript backfill (661 events / 90d coverage) |

All under harden-ecosystem epic **[#3058](https://github.com/vamseeachanta/workspace-hub/issues/3058)**. ~70 tests, zero regressions (19 pre-existing skill-content failures are unrelated — verified).

## Signal is LIVE
Backfill activated into gitignored `.claude/state/sessions/` → demotion-aware report **demoted 214 skills by one tier on real 90-day usage**. Live tiers: HOT 41 / WARM 99 / COLD 106 / DEAD 580. "DEAD ≠ unused" is now measurable (133 skills have proven usage).

## CLOSED / parked
- [#3106](https://github.com/vamseeachanta/workspace-hub/issues/3106) — de-prescription sweep: CLOSED (premise empirically invalidated).
- [#3107](https://github.com/vamseeachanta/workspace-hub/issues/3107) — fable-mode adapter: parked blocked-draft (mechanism mis-specified for v2.1.177; build as a Skill / `keep-coding-instructions:true`; gate efficacy on #3061).
- [#3062](https://github.com/vamseeachanta/workspace-hub/issues/3062) — **skill retirement: re-planned on the live signal, adversarial review MAJOR → BLOCKED.** Even with the signal, it's blind to non-Read usage (`@`-include / path / prose refs) → could archive a load-bearing skill. Plan: `docs/plans/2026-06-15-issue-3062-retirement-on-live-signal.md` (blocked-draft) on local branch `plan/3062-retirement-replan` (4e6e06bc4, UNPUSHED).

## Repo state at exit
- On branch `plan/3062-retirement-replan` (local-only, unpushed; holds the parked #3062 re-plan).
- **Dirty exception (expected):** `.claude/state/skill-scores.yaml` modified = the live signal-activation result (214 demoted). Regenerable; gitignored backfill events in `.claude/state/sessions/*.backfill.jsonl` (not committable by design).
- feat/3137/3138/3139 local branches deleted post-merge (work on main).
- No external actions taken (no emails/posts beyond GitHub issue comments + PRs on this repo).

## NEXT STEPS (priority order)
1. **#3062 reference-scanning gate** (the one blocker before safe retirement): scan `@`-includes + path/prose refs in CLAUDE.md/SOUL/`.claude/rules/`/skill-bodies, **rel-path-keyed** (survives the 11 basename collisions); reconcile the 3 retirement signals (tier vs session_count vs check_retirement_candidates); fix the plan's pseudocode schema (`rows` list + `session_count_available_days`). Then re-review → approve → TDD archive-not-delete.
2. **Runtime-verify #3137's hook**: invoke any skill in a live session, check `.claude/state/sessions/session_*.jsonl` for a `tool:"Skill"` entry with `skill_name` (only confirmable live).
3. Decide commit-vs-regenerate for `skill-scores.yaml` + whether the backfill runs on a cadence (dashboard already wires scanner→report per #3112 BUG-3).
4. Optionally push `plan/3062-retirement-replan` (code-free; needs the audited `GIT_PRE_PUSH_SKIP` for unrelated assetutilities lint debt).

## Memories saved this session
- `feedback_verify_generated_state_against_origin_not_working_copy`
- `project_skill_retirement_blocked_on_invocation_signal`

## Operational notes
- An aggressive auto-committer/auto-sync runs on this checkout (commits/pushes working-tree changes, holds git locks). Work atomically; expect it to bundle/preserve changes (it created `preserved/2026-06-15-skill-invocation-wip`).
- Pushes blocked by pre-existing `assetutilities` ruff debt (473 errors) need operator-run `GIT_PRE_PUSH_SKIP=1` (agent cannot self-grant).
