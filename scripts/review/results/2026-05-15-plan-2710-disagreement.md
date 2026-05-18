# Disagreement report — plan #2710 (2026-05-15)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=0: Reading additional input from stdin... ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **Architecture Decision contains a false factual claim about `submit-job.sh`'s current behavior, on which the r1 revision's central design choice rests.** Plan §Architecture Decision, line 141 states: *"the current `submit-job.sh` writes the YAML and commits without ever checking if the input file exists; the issue acceptance demands this gap be closed at the wrapper layer until `submit-job.sh` itself is extended."* This is empirically false. `scripts/solver/submit-job.sh` lines 18-23 contain an explicit existence check that fires BEFORE the git commit at line 40:
-    ```
-    if [[ ! -f "${REPO_ROOT}/${INPUT_FILE}" ]]; then
-        echo "ERROR: input file not found: ${INPUT_FILE}" >&2
-        echo "Path must be relative to repo root: ${REPO_ROOT}" >&2
-        exit 1
-    fi
-    ```
-    `git log -S "input file not found" -- scripts/solver/submit-job.sh` shows this check has been present since the original commit `71a53898b feat(07-02): create git-based solver job queue infrastructure`. The issue's acceptance criterion *"Both wrappers reject missing input files with a clear error before any git operations"* is ALREADY SATISFIED by `submit-job.sh` for any caller (wrapper, batch, or direct CLI). The premise of r1 Blocker 1 fix is wrong.
- **The r1 wrapper-layer existence check duplicates `submit-job.sh:18-23`, violating the issue's "No duplicate validation logic" acceptance criterion (AC 5).** Plan §Pseudocode lines 211-215 add `[[ ! -f "${REPO_ROOT}/${INPUT_FILE}" ]]` to the wrapper. This is the exact duplicate-validation pattern AC 5 forbids. The plan's own Architecture Decision (line 137) states the wrapper has no "string-level enum validation" — but an `-f` test IS validation, just gated on existence rather than enum. The plan rationalises this as "UX guard mirrors a precondition submit-job.sh is silent about" (line 141) — but submit-job.sh is NOT silent about it.
- **Resource Intelligence "Line excerpts" selectively truncate `submit-job.sh` at line 16 to hide the existing check.** Plan lines 88-99 quote `scripts/solver/submit-job.sh:8-16`, ending precisely one line before the existence-check block at 18-23. The selective citation creates the false impression that solver-enum validation is the only gate in `submit-job.sh`. The "Found:" entries at plan lines 15-16 also reference only `submit-job.sh:13-16`, not the full validation block. The retrieval is misleading by omission.
- **The wrapper's `case` statement at Pseudocode lines 196-201 IS a hardcoded second solver list, despite the plan claiming none exists.** The r1 revision claims (line 314): *"the new architecture has no second solver list in the wrapper — `submit-job.sh:13-16` is the single gate; nothing to cross-check."* But the menu options and `case CHOICE in 1) SOLVER="orcawave" ;; 2) SOLVER="orcaflex" ;; 3) SOLVER="aqwa" ;;` are by construction a hardcoded enumeration of solvers. If `submit-job.sh:13-16` adds `iwave`, the wrapper menu is silently stale until manually edited. Calling it "UX-only" does not eliminate drift risk — it just removes the failure mode of duplicate *rejection*. The removed `test_solver_list_consistency` was the only artifact protecting against menu drift; its removal is an unforced regression.
- **AQWA stale-hint mitigation in §Risks contradicts the Pseudocode implementation.** §Risks line 362 states: *"the hint code path checks for `${DELEGATE_EXIT} -ne 0` AND specifically grep for the canonical enum-rejection message in stderr; once #2709 lands and AQWA is accepted, the hint will not fire."* But Pseudocode lines 241-245 implement only `if [[ "${SOLVER}" == "aqwa" && "${DELEGATE_EXIT}" -ne 0 ]]; then print HINT`. There is no stderr grep. The mitigation as written in Risks is not in the implementation plan. After #2709 lands, ANY non-zero exit from a `submit-job.sh aqwa ...` call (validation failure, push failure, etc.) will spuriously emit a stale #2709 hint. Either the Pseudocode or the Risks claim must change before implementation.
- **Divergent error messages for the same condition once the wrapper-layer check is removed (or once submit-job.sh is bypassed).** Plan Pseudocode line 212 produces stderr `ERROR: input file does not exist: ...`. `submit-job.sh:20` produces `ERROR: input file not found: ...`. Acceptance criterion at plan line 328 hard-codes the wrapper's wording (`stderr contains "input file does not exist"`), but anyone calling `submit-job.sh` directly or via `submit-batch.sh` will see "not found". Two strings for one condition is a documented user-experience defect that the issue's acceptance criteria do not address.
- **r1 review status table is inconsistent with the on-disk r2 artifacts the user can observe.** Plan §Adversarial Review Summary table (lines 342-346) shows `Codex (r2) | PENDING`, but `scripts/review/results/2026-05-15-plan-2710-codex.md` already exists with verdict `UNAVAILABLE (codex CLI failed, rc=0: Reading additional input from stdin... )`. The matching r2 Claude artifact at `scripts/review/results/2026-05-15-plan-2710-claude.md` is 1 line long (empty review body). If these are the r2 outputs, the table is stale; if they are not, the plan needs to name what they are. Either way the plan's claim that r2 is "PENDING" misrepresents the artifact state.
- **Test name lies about realism — `test_aqwa_delegates_and_shows_hint` uses an OrcaFlex `.dat` file as the AQWA input.** Plan line 306 input: `output/orcaflex_validation/pipeline_test_model.dat`. AQWA uses `.dat`-extension files but with an entirely different binary/text format; calling this an AQWA fixture is misleading. The mock doesn't care, so the test passes, but the fixture choice undermines the "real-file fixture" claim from §Evidence (lines 80-81).
- **Dead trailing input in `test_missing_file_rejected_before_git` stdin.** Plan line 304 sends `1\ndoes/not/exist.owd\nx\ny\n` — 5 lines. The wrapper exits after the existence check, having read only the first two lines (menu choice + input path). The trailing `x\ny\n` are wasted bytes. Either the test is asserting behavior that never reaches the description prompt (in which case truncate the stdin), or the test author confused the order of pseudocode steps. Minor but indicates the test list was hand-written without dry-running the flow.
- **§Risks line 361 mitigation is missing from the §TDD Test List.** Risks states: *"the harness will additionally check `git status --short queue/pending/` before/after each test to fail loudly if any pending file appeared."* No test row in §TDD Test List (plan lines 300-313) implements this guard; no test name like `test_no_queue_file_leakage` exists. The mitigation is unenforced documentation.
- **§Evidence "Source count: 13 distinct sources" is off-by-one.** Counting the parenthetical at plan line 129: issue body + #2709 + #2708 + submit-job.sh + submit-batch.sh + job-schema.yaml + 3× SKILL.md frontmatter + README.md + CONTROL_PLANE_CONTRACT.md + behavior-contract.yaml + coding-style.md + patterns.md + SKILLS_INDEX.md = 14, not 13. Trivial, but the plan asserts the number explicitly.
- **Acceptance Criteria still cite 2026-05-14 review-artifact paths after r1 (line 334).** The criterion reads: *"Review artifacts will be posted to `scripts/review/results/2026-05-14-plan-2710-{claude,codex,gemini}.md`"*. After r1 revision dated 2026-05-15, the natural artifact dates would be 2026-05-15 (which already exist as untracked files per `git status`). The criterion is satisfiable as-stated but the convention is unclear, and the gemini r2 artifact may never appear.

### codex

- (none)

