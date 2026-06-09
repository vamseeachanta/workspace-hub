# Adversarial plan review — #2986 (Claude, main-session inline)

Reviewed: `docs/plans/2026-06-09-issue-2986-cron-uv-resolution.md`
Date: 2026-06-09

## Verdict

MAJOR

## Retrieval

- Read the full plan `docs/plans/2026-06-09-issue-2986-cron-uv-resolution.md` (lines 1-232).
- Read `scripts/skills/validate-skills.sh` (lines 1-20) — confirmed `command -v uv` gate at 13-16, `UV_CACHE_DIR` default at 18, exec at 19.
- Read `scripts/cron/comprehensive-learning-nightly.sh` (lines 1-168) — confirmed line-8 PATH prepend and line 90 best-effort call; also found line 14 `source scripts/lib/python-resolver.sh`.
- Read `scripts/lib/uv-env.sh` (full) — pre-existing `uv_env_setup`/`uv_env_repo_root` helper that centralizes `UV_CACHE_DIR`.
- Read `scripts/lib/python-resolver.sh` (full) — established resolver idiom (`$PYTHON`), sourced by 6+ scripts incl. the cron wrapper being modified.
- Read `.github/workflows/skills-validation.yml` (full) — CI uses `astral-sh/setup-uv@v4`, hard-fail on validator + regression tests.
- Listed `tests/cron/` and `scripts/lib/`; confirmed `validate_skills_frontmatter.py` exists.
- Ran `gh issue view 2986` for the actual problem statement and acceptance criteria.
- Ran the plan's reproduction command, AND ran the wrapper's line-8 prepend in an isolated shell (`env -i HOME=$HOME PATH=/usr/bin:/bin ...`) to test whether the real cron path resolves `uv`.
- Grepped all callers of `validate-skills.sh`; read the cron schedule in `config/scheduled-tasks/schedule-tasks.yaml:131` and the active crontab line.
- Listed existing `scripts/review/results/*2986*` files to check the plan's cited review-artifact paths.

## Findings

1. **The reproduction does not reproduce the production failure path (Step 1.5 violation — root justification is unsound).** Plan §Evidence "Reproduction proofs" (lines 86-94) runs `PATH=/usr/bin:/bin bash scripts/skills/validate-skills.sh` directly. But the nightly cron never invokes `validate-skills.sh` directly — it invokes the wrapper `comprehensive-learning-nightly.sh` (confirmed: crontab `0 2 * * * ... bash scripts/cron/comprehensive-learning-nightly.sh`), whose line 8 does `export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"` *before* reaching line 90. I verified empirically: under `env -i HOME=$HOME PATH=/usr/bin:/bin`, after applying the line-8 prepend, `command -v uv` resolves `/home/vamsee/.local/bin/uv`. So in the real cron flow the existing `command -v uv` gate already succeeds. The plan's reproduction bypasses the wrapper and therefore demonstrates a failure mode that does not occur in production.

2. **The proposed resolver shares the exact failure mode of the existing line-8 fix and adds no reliability against the only genuine residual risk.** The resolver's candidates (plan §Pseudocode line 139) are `$HOME/.local/bin/uv`, `$HOME/.cargo/bin/uv`, `/usr/local/bin/uv` — identical to what line 8 already prepends. The only realistic way the production path fails is if `$HOME` is unset/wrong under cron (standard cron sets `HOME` from `/etc/passwd`, so even this is unlikely). When `$HOME` is unset, the resolver's `$HOME/.local/bin/uv` expands to `/.local/bin/uv` and fails identically to line 8. The plan never investigates `$HOME` behavior under cron, yet that is the sole failure mode that survives the existing fix. Net new reliability for the cron path ≈ zero; the only real gains are the `UV_BIN` override and better diagnostics — which the Deliverable (line 125) and Acceptance Criteria overstate as "resolve uv reliably under cron-like environments."

3. **No caller exercises the path the resolver fixes.** Grep shows only two real callers of `validate-skills.sh`: the cron wrapper (PATH fixed at line 8) and CI `skills-validation.yml` (which installs `uv` on PATH via `setup-uv@v4`). Neither invokes the script with a minimal PATH + valid HOME where the resolver would change the outcome versus status quo. The plan does not enumerate callers to establish that the fix is reachable in any real invocation. The "fix" is defensive hardening of `validate-skills.sh` in isolation, not a fix to a demonstrated production defect — the plan should be reframed honestly as such.

4. **Plan ignores existing prior art it is sitting on top of.** `scripts/lib/uv-env.sh` already exists and centralizes `UV_CACHE_DIR` via `uv_env_setup`; `scripts/lib/python-resolver.sh` is the established resolver idiom and is `source`d on line 14 of the very cron wrapper this plan modifies. The Resource Intelligence Summary (lines 15-46) and "Gaps identified" claim "No reusable `uv` resolver exists for shell scripts" without acknowledging either file. The new `uv-resolver.sh` should mirror `python-resolver.sh`'s function/`export` idiom and reuse `uv_env_setup` for the cache default rather than re-hand-rolling `UV_CACHE_DIR` — otherwise the repo accrues a third parallel lib helper.

5. **Acceptance criterion #4 is a tautology that cannot fail.** Line 199: "Minimal-PATH probe either resolves a common installed `uv` or prints actionable guidance." Every possible outcome satisfies one branch of the OR, so the criterion verifies nothing about correctness — same defect class as the circular-AC example in the review rubric. It must assert the *specific* expected branch given a known HOME (e.g., "with HOME pointing at a tree containing `.local/bin/uv`, the probe resolves that exact binary and execs it; with empty HOME, it exits 2 with guidance naming all three searched paths and `UV_BIN`").

6. **Test `test_nightly_skill_validation_step_mentions_resolver_diagnostics` asserts behavior the plan does not commit to producing.** TDD list line 190 expects cron output to include "resolver diagnostic and then `WARNING: skill validation issues found`." But (a) resolver diagnostics only print on *failure* (to stderr) — in a normal nightly run `uv` resolves and there are zero diagnostics, so the assertion only holds in the failure case, not the success case it implies; and (b) the cron-wrapper change is described as optional — §Pseudocode lines 162-164 say "optionally source resolver ... only if needed for clearer log header" and "call validate-skills.sh as today." A test cannot assert output from a change the plan marks optional. Either commit to emitting the diagnostic header unconditionally (and test both success and failure output), or drop this test.

7. **Cited review-artifact paths do not exist; the dated files that exist are from a different date.** Plan lines 9, 118-119 reference `scripts/review/results/2026-06-09-plan-2986-{claude,codex}.md`. On disk only `2026-06-08-plan-2986-*` exist (the `2026-06-08-plan-2986-codex.md.err` is 2 MB — the Codex review appears to have errored/looped, leaving the `.md` empty). The plan's traceability pointers are dangling, and there is no evidence a Codex plan review actually completed. Reconcile the date and confirm whether a Codex verdict exists before filling the Adversarial Review Summary table.

## Blockers

- Finding 1 — reproduction is unfaithful to the production cron flow; the alleged failure is not demonstrated as it would occur. Must either (a) reproduce a real cron-context failure (e.g., `$HOME` unset under the wrapper) or (b) reframe the plan honestly as defensive hardening + `UV_BIN` override + better diagnostics, not a fix for a reproduced cron failure.
- Finding 2 — the resolver must address the residual `$HOME`-unset risk that survives line 8, or the plan must state explicitly that it does not and justify the change on diagnostics/override grounds alone.
- Finding 5 — acceptance criterion #4 must be made falsifiable (assert the specific branch).
- Finding 6 — the cron-wrapper test must align with a committed (non-optional) wrapper change and cover the success path.

Findings 3, 4, 7 are MINOR-to-MAJOR context that should be resolved in the rewrite but are not independent hard blockers.
