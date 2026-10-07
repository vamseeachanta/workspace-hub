# Plan for #3876: Harden shell test selectors against undefined-helper false greens

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-09-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3876
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-30-plan-3876-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/skills/tests/test_resync_skill_links.sh` — contains the canonical instance of this defect class. `snapshot_adapter()` defined at line 251 inside a code path skipped by `if [[ "${CODEX_ONLY_ONLY:-0}" != 1 ]]; then` (line 266). PR #3875 applied a partial fix: `declare -F snapshot_adapter >/dev/null || { fail ...; exit 1; }` guards at lines 329 and 349. The owner comment on issue #3876 extends scope to cross-shell exit-code propagation (sequential commands where a later success masks an earlier failure).
- EXISTS: `scripts/monitoring/tests/test_equivalence_fingerprint.sh` — another shell harness; uses `set -uo pipefail` (line 9); command substitutions in `field()` (lines 44–47) wrap python; no `declare -F` guards observed. Uses a conditional `if` branch structure (lines 103–131) that runs different paths depending on outputs.
- EXISTS: `scripts/review/tests/test_plan_review_fanout.sh` — shell harness in `scripts/review/tests/`.
- EXISTS: `scripts/monitoring/tests/test_cron_health_check.sh` — another shell test harness.
- EXISTS: `scripts/maintenance/tests/test_harness_install_doctor.sh` — maintenance harness.
- No prior plan exists for #3876 (checked `docs/plans/` — no match).

### Standards

Not applicable — this is a test harness defect.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- Issue body [#3876](https://github.com/vamseeachanta/workspace-hub/issues/3876) — two defect classes: (1) conditional helper definition (helper defined only when a selector branch runs, referenced outside it); (2) command substitution / pipeline exit-code suppression (failures in `$()`, `|`, or helper functions are not propagated when `set -e` alone guards them).
- Owner comment on [#3876](https://github.com/vamseeachanta/workspace-hub/issues/3876#issuecomment-5697562656) — extends to cross-shell orchestration: "capture and enforce each prerequisite's exit code before subsequent commands"; a successful final command does not evidence preceding steps passed.
- PR [#3875](https://github.com/vamseeachanta/workspace-hub/issues/3875) (MERGED) — applied `declare -F snapshot_adapter >/dev/null || ...` guards in `test_resync_skill_links.sh`. Provides the canonical fix pattern.
- `docs/plans/2026-09-16-issue-3762-harness-context-guards-miss-soul-runtime.md` — adjacent plan on harness guards; confirms the pattern of adding explicit guards at the point-of-use.
- Issue [#3062](https://github.com/vamseeachanta/workspace-hub/issues/3062) — parent initiative where the defect was first observed.

### Gaps identified

- No inventory of shell harnesses that use conditional helper definitions exists.
- No static check enforces that `declare -F <fn>` is present before each use of a conditionally-defined function.
- No cross-shell exit-code propagation rule exists in `.claude/rules/` for sequential invocations.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-09-30 via `gh issue view`):
- `#3876` — OPEN — Harden shell test selectors against undefined-helper false greens
- `#3062` — verified referenced in PR #3875 body as parent initiative

**File existence** (`ls` 2026-09-30):
- EXISTS: `scripts/skills/tests/test_resync_skill_links.sh`
- EXISTS: `scripts/monitoring/tests/test_equivalence_fingerprint.sh`
- EXISTS: `scripts/review/tests/test_plan_review_fanout.sh`
- EXISTS: `scripts/review/tests/test_codex_version_guard.sh`
- EXISTS: `scripts/review/tests/test_cross_review_path_guard.sh`
- EXISTS: `scripts/monitoring/tests/test_cron_health_check.sh`
- EXISTS: `scripts/maintenance/tests/test_harness_install_doctor.sh`
- EXISTS: `scripts/maintenance/tests/test_return_to_main_guard.sh`

**Line excerpts** (`scripts/skills/tests/test_resync_skill_links.sh`):
```
251: snapshot_adapter() {
...
266: if [[ "${CODEX_ONLY_ONLY:-0}" != 1 ]]; then
...
329:   declare -F snapshot_adapter >/dev/null || { fail dry_run_gemini_snapshot_before; exit 1; }
349:   declare -F snapshot_adapter >/dev/null && pass codex_only_snapshot_helper_defined \
350:     || { fail codex_only_snapshot_helper_defined; exit 1; }
```
The `declare -F` guards at lines 329/349 are the PR #3875 fix. The underlying risk is that `snapshot_adapter()` is defined on line 251 *outside* the `CODEX_ONLY_ONLY` branch, so in this specific case the function IS always defined — but the pattern is risky and other harnesses may not be so lucky.

**Gap proofs**:
```
grep -rn "declare -F" scripts/*/tests/*.sh → only test_resync_skill_links.sh shows results
```
Confirms the guard pattern is not yet applied in other harnesses.

**Reproduction proofs**:
The specific false-green in #3876 was fixed by PR #3875. The plan targets the remaining class (audit + generalize). No live reproducer to run; verification is by harness inspection.

---

## Artifact Map

```
scripts/
  skills/tests/test_resync_skill_links.sh    AUDIT ONLY (already has declare -F guards from PR #3875)
  monitoring/tests/test_equivalence_fingerprint.sh  AUDIT + potential fix
  review/tests/test_plan_review_fanout.sh           AUDIT + potential fix
  review/tests/test_codex_version_guard.sh          AUDIT + potential fix
  review/tests/test_cross_review_path_guard.sh      AUDIT + potential fix
  monitoring/tests/test_cron_health_check.sh        AUDIT + potential fix
  maintenance/tests/test_harness_install_doctor.sh  AUDIT + potential fix
  maintenance/tests/test_return_to_main_guard.sh    AUDIT + potential fix
  maintenance/tests/test_git_lock_reaper.sh         AUDIT + potential fix
  maintenance/tests/test_never_clean_globs.sh       AUDIT + potential fix
  maintenance/tests/test_review_audit.sh            AUDIT + potential fix
  ai/tests/test_gh_quirk_dry_run.sh                 AUDIT + potential fix
  knowledge/tests/test-knowledge-scripts.sh         AUDIT + potential fix
  scaffolding/tests/test_new_module.sh              AUDIT + potential fix
  test/
    test-session.sh                                 AUDIT + potential fix
    test-test-health-check.sh                       AUDIT + potential fix
.claude/rules/
  shell-test-helper-guards.md               NEW — rule encoding the two defect classes
tests/
  test_shell_helper_guards.sh               NEW — regression fixture (neutral paths)
```

---

## Deliverable

1. Audit report (inline in commit message / plan comment) listing every shell harness checked, which defect class applies (conditional helper / exit-code suppression / neither), and what fix was applied.
2. Patches to each affected harness: add `declare -F <fn> >/dev/null || { fail "<test>: helper undefined"; exit 1; }` before first use of any conditionally-defined function; make exit codes from command substitutions explicit where they are load-bearing.
3. A new regression fixture `tests/test_shell_helper_guards.sh` that uses a synthetic harness to prove each defect class is caught.
4. A new rule file `.claude/rules/shell-test-helper-guards.md` encoding the two invariants for future plan adversarial review.

---

## Pseudocode

```bash
# Audit pass (to run before writing any fixes):
for harness in $(find scripts -name "*.sh" -path "*/test*"); do
  # Defect Class 1: conditional helper
  # Find: function definitions inside `if` blocks
  # Check: are those functions referenced outside the if block?
  grep -n "^[a-z_]*() {" "$harness" |   # functions defined
  while read funcdef; do
    fn=$(echo "$funcdef" | cut -d: -f2 | cut -d'(' -f1)
    # Check if defined inside a conditional
    # Check if used outside that conditional without declare -F guard
    grep -n "$fn\b" "$harness" | grep -v "^${lineno}:" | grep -v "declare -F $fn"
  done

  # Defect Class 2: exit-code suppression
  # Find: result="$( subcommand )" where subcommand failure matters
  # Check: is there explicit || { fail ...; exit 1; } after the substitution?
done

# Fix pattern for Defect Class 1:
# BEFORE: result="$(snapshot_adapter "$path")"
# AFTER:  declare -F snapshot_adapter >/dev/null || { fail "test_name: snapshot_adapter undefined"; exit 1; }
#         result="$(snapshot_adapter "$path")" || { fail "test_name: snapshot failed"; exit 1; }

# Fix pattern for Defect Class 2:
# BEFORE: out=$(run_thing) ; [[ "$out" == "expected" ]] && pass || fail
# AFTER:  out=$(run_thing) || { fail "test_name: run_thing failed (exit $?)"; exit 1; }
#         [[ "$out" == "expected" ]] && pass || fail
```

---

## Files to Change

| File | Action | Scope |
|------|--------|-------|
| `scripts/skills/tests/test_resync_skill_links.sh` | AUDIT (no change — already fixed by PR #3875) | verify |
| `scripts/monitoring/tests/test_equivalence_fingerprint.sh` | AUDIT + conditional fix | 1–3 lines if affected |
| `scripts/review/tests/test_plan_review_fanout.sh` | AUDIT + conditional fix | 1–3 lines if affected |
| `scripts/review/tests/test_codex_version_guard.sh` | AUDIT + conditional fix | 1–3 lines if affected |
| `scripts/review/tests/test_cross_review_path_guard.sh` | AUDIT + conditional fix | 1–3 lines if affected |
| `scripts/monitoring/tests/test_cron_health_check.sh` | AUDIT + conditional fix | 1–3 lines if affected |
| `scripts/maintenance/tests/test_*.sh` (5 files) | AUDIT + conditional fix | 1–3 lines each |
| `scripts/ai/tests/test_gh_quirk_dry_run.sh` | AUDIT + conditional fix | 1–3 lines if affected |
| `scripts/knowledge/tests/test-knowledge-scripts.sh` | AUDIT + conditional fix | 1–3 lines if affected |
| `scripts/scaffolding/tests/test_new_module.sh` | AUDIT + conditional fix | 1–3 lines if affected |
| `scripts/test/test-*.sh` (3 files) | AUDIT + conditional fix | 1–3 lines each |
| `tests/test_shell_helper_guards.sh` | CREATE — regression fixture | ~60 lines |
| `.claude/rules/shell-test-helper-guards.md` | CREATE — invariant rule | ~30 lines |

---

## TDD Test List (red → green)

All tests in `tests/test_shell_helper_guards.sh`:

1. `test_undefined_helper_caught` — synthetic harness where `fn()` is defined only inside `if [[ $FLAG ]]; then ... fi` and used outside; confirm that the test framework exits non-zero and prints "undefined" before PR #3876 fix is applied.
2. `test_declare_f_guard_catches_missing_fn` — `declare -F nonexistent_fn >/dev/null || exit 1` returns non-zero when function is absent.
3. `test_declare_f_guard_passes_present_fn` — `declare -F snapshot_adapter >/dev/null` returns 0 when function is defined.
4. `test_command_substitution_exit_propagated` — synthetic: `result=$(failing_cmd) || exit 1` makes the harness exit non-zero; without the `|| exit 1`, `set -uo pipefail` alone would not catch it inside a conditional assignment.
5. `test_existing_harnesses_pass_their_own_tests` — runs each audited harness's self-test suite; confirms the patches do not break existing pass/fail counts.

---

## Acceptance Criteria

- Every shell harness in `scripts/*/tests/*.sh` and `tests/` has been audited; the commit message lists each file and whether it was clean or patched.
- No harness calls a conditionally-defined function without a preceding `declare -F <fn> >/dev/null || { fail ...; exit 1; }` guard.
- Load-bearing command substitutions (`result=$(cmd)` where test logic depends on both exit code AND output) use explicit `|| { fail ...; exit 1; }` after the substitution.
- `tests/test_shell_helper_guards.sh` has all 5 named tests passing.
- `.claude/rules/shell-test-helper-guards.md` documents the two invariants with the canonical fix patterns.
- Running all audited harnesses' tests shows the same or improved pass counts compared to baseline (no regressions).

---

## Risks and Open Questions

- **Audit scope**: the harness list above is derived from `find scripts -name "*.sh" -path "*/test*"`. Run this enumeration live before implementing to catch any recently added harnesses not in the list.
- **`set -uo pipefail` vs `set -e`**: harnesses using `set -uo pipefail` (e.g., `test_equivalence_fingerprint.sh`) already catch more errors than plain `set -e`. The audit should distinguish: only harnesses that lack `pipefail` OR use command substitutions inside function bodies (where pipefail does not propagate to caller) need the explicit `|| exit` guard.
- **Cross-shell orchestration** (owner comment on #3876): PowerShell sequential command failure masking is out of scope for this shell-harness plan. Track as a separate issue or extend scope explicitly before implementing.
- **Worktree paths**: harnesses that reference `$REPO_ROOT` or equivalent may behave differently in worktree context. The regression fixture must use a disposable `git init` repo (pattern from `test_equivalence_fingerprint.sh:24–33`), not live paths.
- **Out of scope**: rewriting harnesses that are correct but verbose; adding new test coverage beyond the two defect classes; Python test harnesses (`pytest`).
