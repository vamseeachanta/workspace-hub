# Plan for #2322: Promote binary-checkable .claude/rules/*.md prose to Level 2 scripts per enforcement gradient

> **Status:** revised 2026-04-17 (scope reduced; third script deferred — see "Execution-time revisions")
> **Complexity:** T2
> **Date:** 2026-04-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2322
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2322-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/rules/patterns.md` — defines 4-level enforcement gradient (prose → micro-skill → script → hook) with explicit migration path.
- Found: `.claude/rules/coding-style.md` — contains the three prose rules targeted for promotion: no-hardcoded-absolute-paths, harness-file-size-≤20, queue-git-tracked.
- Found: `scripts/enforcement/` — 18 existing enforcement scripts (`check-config-protection.sh`, `require-plan-approval.sh`, `require-cross-review.sh`, etc.) plus a `tests/` subdir. Pattern: exit 0/1 shell semantics; many already wired to pre-commit or pre-push.
- Found: `.pre-commit-config.yaml` — has working pattern for local hooks (`validate-work-queue-state` calls `scripts/work-queue/validate-queue-state.sh`).
- Found: `scripts/enforcement/install-hooks.sh` — canonical install point for pre-commit/pre-push wiring.
- Gap: no script enforces absolute-path ban, harness-size cap, or queue-git-tracked.

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a — harness/enforcement work | n/a | — |

### LLM Wiki pages consulted
- Not applicable.

### Documents consulted
- Issue #2018 — agent bypass resistance — technical gates (parent umbrella; this plan is one concrete slice).
- Issue #2028 — review gate strict mode + GitHub Actions CI enforcement workflow (sibling).
- Issue #1876 — enforce engineering workflow via Hermes prefill + Claude Code hooks (sibling).
- Memory: `feedback_queue_git_tracked.md` — the source of the queue-git-tracked rule.
- `.claude/rules/README.md` — explicit statement: "Universal constraints only. Stage-specific rules live in micro-skills."
- `CLAUDE.md` at repo root — currently 9 lines (passes harness cap).

### Gaps identified
- Three Level-0 prose rules that are binary-checkable have no enforcement script.
- No regression test fixtures demonstrating pass/fail for these checks.
- The rules files themselves don't cite scripts (so rule readers don't know a check exists).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2322-rule-promotion.md` |
| Script 1 | `scripts/enforcement/check-no-abs-paths.sh` |
| Script 2 | `scripts/enforcement/check-harness-file-size.sh` |
| Tests (sh convention) | `scripts/enforcement/tests/test_check_no_abs_paths.sh` |
| Tests (sh convention) | `scripts/enforcement/tests/test_check_harness_file_size.sh` |
| Fixtures | `scripts/enforcement/tests/fixtures/` |
| Pre-commit wire | `.pre-commit-config.yaml` (modify) |
| Hook installer | `scripts/enforcement/install-hooks.sh` (modify if pre-push needed) |
| Rule pointers | `.claude/rules/coding-style.md`, `.claude/rules/patterns.md` (modify to cite scripts) |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2322-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-17-plan-2322-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-17-plan-2322-gemini.md` |

---

## Deliverable

Two `scripts/enforcement/check-*.sh` scripts with exit-0/1 semantics, each with a regression test fixture; harness-file-size check wired to pre-commit; rules files updated to reference the scripts. (The third script, `check-queue-git-tracked.sh`, is deferred to a follow-up issue — see "Execution-time revisions" — because its target surface was mis-identified in v1.)

---

## Pseudocode

```
# check-no-abs-paths.sh
# Scope: tracked .sh and .py files under scripts/, .claude/, and root.
# Bypass: ALLOW_ABS_PATHS=1 (logged to stderr) — follows existing
#         FORCE_PLAN_GATE / FORCE_REVIEW convention in sibling scripts.
# Allowlist: fixture files under scripts/enforcement/tests/fixtures/violating/,
#         and lines ending with a trailing " # abs-path-allowed" marker.
# Detection: regex for /home/|/mnt/|/Users/|/opt/|^[A-Z]:[/\\] — simple first,
#         per the "enforcement gradient" philosophy (Level-0 prose → Level-2
#         regex script → future Level-3 AST if false-positive rate proves high).
violations=[]
for file in $(git ls-files 'scripts/**/*.sh' 'scripts/**/*.py' '*.sh'):
    for line_no, line in enumerate(file):
        if match(line, r'/home/|/mnt/|/Users/|/opt/|^[A-Z]:[\\/]') and not in_allowlist(file, line_no):
            violations.append("$file:$line_no: $line")
if violations and $ALLOW_ABS_PATHS != "1": print all; exit 1
exit 0

# check-harness-file-size.sh
# Caps: CLAUDE.md, MEMORY.md, AGENTS.md, GEMINI.md ≤ 20 lines each.
# Bypass: ALLOW_HARNESS_OVERSIZE=1 (logged to stderr).
# Scope: repo root and subdirectories, but NOT SKILL.md (skills have
#        different size expectations) and NOT tests/fixtures/**.
over_cap=[]
for file in find_harness_files():
    lines = wc -l
    if lines > 20: over_cap.append("$file: $lines lines (>20)")
if over_cap and $ALLOW_HARNESS_OVERSIZE != "1": print all; exit 1
exit 0
```

(Deferred — see "Execution-time revisions": `check-queue-git-tracked.sh` was based on a wrong target surface and is moved to a follow-up issue.)

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/check-no-abs-paths.sh` | implementation |
| Create | `scripts/enforcement/check-harness-file-size.sh` | implementation |
| Create | `scripts/enforcement/tests/test_check_no_abs_paths.sh` | tests (shell convention, not .bats) |
| Create | `scripts/enforcement/tests/test_check_harness_file_size.sh` | tests |
| Create | `scripts/enforcement/tests/fixtures/{ok,violating}/` | shell + python fixtures |
| Modify | `.pre-commit-config.yaml` | wire harness-file-size hook |
| Modify | `.claude/rules/coding-style.md` | cite new scripts at rule sites |
| Modify | `.claude/rules/patterns.md` | cite new scripts as Level-2 examples |
| Update | `docs/plans/README.md` | add row for this plan |

---

## TDD Test List

Shell convention (`test_*.sh`), matching the 30+ existing siblings under `scripts/**/tests/`. Harness is `pass/fail/run_test` helpers plus final counters (pattern: `scripts/enforcement/tests/test_require_review_on_push.sh`).

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_abs_paths_fail_on_home | detects `/home/...` in a script | fixture .sh containing `/home/vamsee/x` | exit 1, message cites file:line |
| test_abs_paths_fail_on_mnt | detects `/mnt/...` | fixture with `/mnt/local-analysis/...` | exit 1 |
| test_abs_paths_fail_on_python | detects `/home/...` in a `.py` file | fixture .py with `Path("/home/.../x")` | exit 1 |
| test_abs_paths_pass_on_relative | no violation for relative paths | fixture using `$(git rev-parse --show-toplevel)` | exit 0 |
| test_abs_paths_allowlist_fixtures | files under fixtures/violating/ are ignored | fixture | exit 0 |
| test_abs_paths_allowlist_marker | line ending `# abs-path-allowed` ignored | fixture | exit 0 |
| test_abs_paths_bypass_env | `ALLOW_ABS_PATHS=1` overrides a violation | fixture w/ violation | exit 0, stderr logs bypass |
| test_harness_pass_under_20 | 10-line CLAUDE.md passes | fixture | exit 0 |
| test_harness_fail_over_20 | 25-line MEMORY.md fails | fixture | exit 1 |
| test_harness_ignores_skill_md | SKILL.md (different size contract) not checked | SKILL.md in fixture | exit 0 |
| test_harness_ignores_fixtures | harness files under tests/fixtures/ not checked | fixture | exit 0 |
| test_harness_bypass_env | `ALLOW_HARNESS_OVERSIZE=1` overrides | fixture | exit 0, stderr logs bypass |
| regression_precommit_harness_blocks_over_cap | pre-commit hook blocks commit that inflates MEMORY.md >20 | `pre-commit run` | non-zero exit |

---

## Acceptance Criteria

- [ ] Both scripts created under `scripts/enforcement/` with `exit 0`/`exit 1` semantics and a documented bypass env var each.
- [ ] Each script has ≥3 regression tests covering pass + fail + edge case, written in `test_*.sh` convention.
- [ ] `pre-commit run check-harness-file-size --all-files` works.
- [ ] An intentionally-inflated MEMORY.md (>20 lines) is blocked by the hook.
- [ ] `.claude/rules/coding-style.md` and `patterns.md` cite each new script at the relevant prose rule.
- [ ] No false positives when run against current clean repo (`bash scripts/enforcement/check-no-abs-paths.sh` exits 0).
- [ ] `scripts/enforcement/install-hooks.sh` wires any additional hooks if added.
- [ ] A follow-up issue is filed for the deferred solver-queue git-tracked check, linked to `feedback_queue_git_tracked.md` and `scripts/solver/submit-job.sh`.

## Execution-time revisions (2026-04-17)

Pre-execution contradiction scan against the approval-with-debt marker
(`.planning/plan-approved/2322.md`) and live repo state surfaced five deltas:

1. **Test harness convention.** v1 used `.bats`. Repo has 30+ `test_*.sh` and
   zero `.bats` files (verified via find). Approval marker flagged this as
   known debt. **Resolution:** use `test_*.sh`.

2. **Absolute-path detection.** v1 pseudocode was pure regex. Approval marker
   noted AST parsing "likely" needed. **Resolution:** ship regex + allowlist
   (fixture dir + inline marker) as v1; document the false-positive risk as
   known debt; file a follow-up if the false-positive rate is material.
   Per the enforcement-gradient philosophy, "Level-2 script (exit 0/1,
   auditable, testable)" is the intended target; AST parsing is a
   potential Level-2+ upgrade.

3. **Queue-git-tracked scope — LOAD-BEARING.** v1 pseudocode iterated
   `.claude/work-queue/*.yaml`. Reality: no such files exist. The actual
   source of the rule (`feedback_queue_git_tracked.md` in auto-memory) is
   about **solver queue jobs** submitted via `scripts/solver/submit-job.sh`
   on `licensed-win-1` — the reported incident was a `.owr` file that
   wasn't git-tracked. **Resolution:** DROP the third script from #2322.
   File a separate, correctly-scoped follow-up issue for a
   `check-solver-job-inputs-git-tracked.sh` tied to the real surface.
   (The `.claude/work-queue/` directory is legacy per its own `INDEX.md`;
   the canonical agent queue now lives at `notes/agent-work-queue.md`
   and is GitHub-label-sourced, so it doesn't need the rule.)

4. **No bypass env var.** Wave v2 flagged this. Sibling scripts
   (`require-plan-approval.sh`, `require-cross-review.sh`) use `FORCE_*=1`
   env vars. **Resolution:** each script gets an `ALLOW_*=1` bypass, logged
   to stderr on use.

5. **No Python fixtures for abs-paths.** v1 TDD only covered shell
   fixtures, but the check applies to `.py` files too. **Resolution:**
   add a `.py` fixture in both `fixtures/ok/` and `fixtures/violating/`.

Resolutions #1, #2, #4, #5 applied unilaterally per standing preferences.
Resolution #3 (scope cut) confirmed by user before code was written.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
**Wave v2 (2026-04-17, stance-contract applied):**

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | `.bats` tests violate repo precedent (confirmed: existing tests are `test_*.sh`); `check-no-abs-paths.sh` allowlist as described requires AST parsing not expressible in shell; `.claude/work-queue/` has no top-level yamls so schema assumption is invented; no bypass env var documented; no Python TDD fixtures |
| Codex | MAJOR | (see scripts/review/results/2026-04-17-plan-2322-codex.md) |
| Gemini | MAJOR | (see scripts/review/results/2026-04-17-plan-2322-gemini.md) |

**Overall result:** FAIL — MAJOR from all three. Plan requires revision before user approval.

**Blockers to resolve before approval:** see per-provider review artifacts under `scripts/review/results/2026-04-17-plan-2322-*.md`.

---

## Risks and Open Questions

- **Risk:** False-positive on absolute-path check blocks legitimate file_path parameters in tool calls. Mitigation: allowlist file patterns (e.g., `tests/**/fixtures/**`).
- **Risk:** Harness-size check flags the temporary addition of a line during editing. Mitigation: hook runs on commit only, not on save.
- **Risk:** Queue-git-tracked check's schema assumption may not match all queue formats. Mitigation: start narrow (one schema), widen incrementally.
- **Open:** Should `check-no-abs-paths.sh` also apply to `.md` files? Recommend no for v1 — docs routinely cite paths.
- **Open:** Pre-push vs pre-commit for absolute-path check? Recommend pre-commit (faster feedback).

---

## Complexity: T2

**T2** — three scripts, tests, pre-commit wiring, rule-doc updates. Bounded scope; no external dependencies.
