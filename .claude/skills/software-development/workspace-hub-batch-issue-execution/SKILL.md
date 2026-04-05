---
name: workspace-hub-batch-issue-execution
description: Execute a batch of feasible GitHub issues in workspace-hub with plan gating, TDD-first edits, adversarial review, and commit-to-main discipline.
version: 1.1.0
author: Hermes Agent
license: MIT
---

# Workspace-hub Batch Issue Execution

Use when the user asks to identify multiple GitHub issues that can be done on the current machine and execute them one by one.

## When to use
- User wants a queue of feasible GitHub issues from `workspace-hub`
- You need to filter by current-machine feasibility before implementation
- Work spans shell scripts, Python scripts, docs, and tests
- Repo policy requires plan approval, TDD, review, and direct commits to `main`

## Hard constraints
1. Read `AGENTS.md` first
2. Get explicit user approval before implementation
3. Use TDD for code/script changes
4. Commit to `main` and push immediately after each completed issue or tightly related pair
5. Use `uv run` for Python and pytest commands

## Feasibility triage workflow
1. Confirm repo + auth
   - `gh auth status`
   - `git remote -v`
   - `git branch --show-current`
2. List open issues
   - `gh issue list --state open --limit 200`
3. Prefer issues that are clearly executable on the current machine because they:
   - touch files present in the repo
   - do not require another machine label such as dev-secondary / Windows-only
   - have acceptance criteria that can be tested locally
4. Inspect candidate issue bodies
   - `gh issue view <num> --json number,title,body,labels`
5. Build an ordered batch and ask for approval before coding

## Good issue types for this workflow
- shell script hardening
- schema alignment
- local cron/config parsing fixes
- local docs/policy reconciliation
- test additions around existing scripts
- review/log normalization
- retention/documentation policy in local scripts

## Pre-check: is the issue already done?

Before planning any work, check if the issue's deliverables already exist:
1. Check if the files mentioned in the issue body already exist (`ls -la`)
2. If tests exist, run them (`uv run pytest path/to/tests -v`)
3. If code + tests exist and pass, close immediately with verification comment

This saved significant time in practice — issues with implementation comments may already be complete but not closed. A 30-second verification check avoids a 30-minute planning cycle.

## Execution pattern per issue

### 1. Write or update the failing test first
For shell scripts, static tests are acceptable when they assert a specific safety/property requirement, e.g.:
- script no longer contains `python3 -c`
- script uses `uv run --no-project python -`
- script contains locking via `flock`
- docs contain required legacy/canonical wording

For Python logic, write targeted unit tests around the function or module.

### 2. Run the failing test
Examples:
- `uv run pytest tests/solver/test_batch_submission.py -q`
- `uv run pytest tests/monitoring/test_cron_health_script.py -q`
- `uv run pytest tests/docs/test_work_queue_policy_consistency.py -q`

### 3. Make the minimal fix
Typical patterns that worked well:
- Replace fragile `python3 -c` / interpolated shell snippets with `uv run --no-project python - "$arg" <<'PY'`
- Pass dynamic values as CLI args to Python, not by embedding shell variables in source
- For shell watchers, use `flock` and persistent state files for failure counts
- For schema migrations, align example files, parser, validator, and tests together
- For docs contradictions, update canonical policy docs and add consistency tests

### 4. Run targeted validation
Common validation set:
- `bash -n path/to/script.sh`
- `uv run pytest <targeted tests> -q`
- one dry-run/manual execution of the script when safe

### 5. Adversarial review
Use a reviewer subagent after non-trivial changes.
Ask it to check:
- correctness vs issue acceptance criteria
- hidden mismatches between validator/runtime behavior
- shell-safety and shared-state risks
- test adequacy

If review returns MAJOR, fix before commit.

### 6. Commit and push immediately
Use issue-linked commit messages, e.g.:
- `fix(solver): lock result watcher and surface pull failures (#1705 #1706)`
- `fix(ops): harden cron health parsing and document legacy work queue (#1713 #1717)`

## Useful batching heuristic
It is efficient to combine issues in one commit when they are the same code path and share tests, for example:
- schema alignment + validation preflight
- watcher locking + pull failure surfacing
- user profile + review policy reconciliation + retention policy if they are all small control-plane config/doc changes

Do not combine unrelated domains just to reduce commits.

When the user asks to exhaust everything feasible on the current machine, use a wave-based pattern:
1. finish the currently active issue cleanly
2. spawn up to 3 reconnaissance subagents for the next issue set
3. have subagents return exact files/tests/commands, not edits
4. implement centrally in the main session to avoid git contention
5. close false-positive issues directly when the repo evidence shows no code change is needed

## Review findings worth remembering
During batch execution, these findings were important:
- A weaker duplicate validator in a shell script can appear “working” while still being inconsistent with the canonical Python validator. Use the canonical validator directly when possible.
- For concurrent watcher processes, initialize or reset shared state only after lock acquisition.
- Surfacing a failure counter is not enough if another invocation can erase it.
- Changing dedup keys for historical data requires migration logic for legacy IDs, or the next run will misclassify old items as new.
- A source allowlist based only on a symbolic source label is weaker than a domain allowlist; validate both when possible.
- Some repo/audit issues are false positives. If local inspection proves the issue claim is wrong, comment with evidence and close instead of forcing a code change.
- For skill collision fixes in workspace-hub, prefer canonicalizing identity to SKILL.md frontmatter `name:` and adding leaf-directory collision detection before attempting broad directory renames.
- When reconciling repo skills with Hermes skills, prefer updating the repo-side skill to absorb the stronger operational guidance while preserving repo-local frontmatter/category conventions; add regression tests for the merged sections instead of trying to rename everything at once.
- For cron issues, distinguish repo-source fixes from machine-state drift. If YAML is correct but `crontab -l` is stale, repair machine state with `bash scripts/cron/setup-cron.sh --replace` and close the issue as an operational fix.
- If scheduled task commands still inline `git pull/add/commit/push`, replace them with small wrapper scripts that source `scripts/cron/lib/git-safe.sh`; validate with `bash -n` plus `setup-cron.sh --dry-run`.
- For review-gate enforcement issues, use the existing pre-push script as the implementation surface, add latency logging JSONL, add path-based low-risk classification for docs/config-only commits, and document bypass policy explicitly.

## Git pitfalls
If `git push` fails with a remote rejected / expected-old-sha style error even after a local commit, run:
- `git pull --rebase origin main`
- `git push origin main`

If `pull --rebase` refuses because of unrelated local edits from the next issue, temporarily stash those local edits, finish the push for the already-committed issue, then pop the stash and continue.

## Artifact hygiene
Before commit, check for runtime artifacts accidentally created during validation, especially:
- `queue/.processed/`
- `queue/.watcher-state/`
- `data/solver-results-log.jsonl`

Do not stage these unless the issue explicitly requires them.

## Closeout discipline
For each completed issue, prefer this sequence:
1. targeted tests + one safe manual validation
2. adversarial review subagent for non-trivial changes
3. commit + push to `main`
4. `gh issue comment` with what changed and validation commands
5. `gh issue close` when the fix is fully landed or when you have confirmed the issue was invalid / already satisfied

## Large test coverage issues: research-then-parallel pattern

When an issue targets test coverage across many files (5+), use this 3-phase approach:

### Phase 1: Research subagent (single, read-only)
Dispatch ONE subagent with toolsets=["file"] to:
- Read all source files under test
- Read existing conftest.py for available fixtures/factories
- Read dependency schemas (dataclasses, enums, etc.)
- Produce a structured test plan (TEST_PLAN.md) with:
  - Per-file: public functions, signatures, return types
  - Mock data factories needed
  - Proposed test cases with names and assertions
  - Implementation order (leaf modules first)
  - Priority ratings

### Phase 2: Parallel implementation subagents (up to 3)
Split files into batches and dispatch 3 subagents simultaneously, each with:
- The test plan from Phase 1 as context
- Explicit conftest fixture names and signatures
- Source file locations and key imports
- toolsets=["terminal", "file"] so they can write files AND run pytest

Each subagent reads source files, writes tests, and runs them to verify. Wall-clock time: ~11 min for 266 tests vs ~30+ min serial.

### Phase 3: Unified verification
Run all new test files together from the main session to catch cross-file conflicts.
Only commit after the unified run passes.

### Key learnings from this pattern:
- Give each subagent EXACT fixture names from conftest.py — they can't discover them
- Tell subagents about non-obvious imports (e.g., dataclass locations in other modules)
- For Plotly-producing functions, assert HTML keywords/structure, not pixel output
- Mock lazy imports (e.g., MeshPipeline for OrcFxAPI) with unittest.mock.patch
- Use tmp_path for all file I/O tests
- Subagents should run pytest at the end and fix failures before returning

### When NOT to use this pattern:
- < 5 files to test (just do it directly)
- Files with heavy interdependencies (serial is safer)
- When conftest needs new fixtures (build conftest first, then parallelize)

## Library integration issues: rapid batch pattern

When multiple issues are "Integrate X library" with the same shape (install, evaluate, test), use this formula:

### Per-library checklist (15-20 min each)
1. **Check if already installed:** `uv run python -c "import X; print(X.__version__)"`
2. **Install if needed:** `uv add X` (updates pyproject.toml + uv.lock)
3. **Smoke test in terminal:** Run 3-5 key API calls inline to verify working
4. **Delegate to subagent:** Create evaluation script + integration tests in one call
   - Evaluation script: `scripts/integrations/X_evaluation.py` (5-7 engineering demos)
   - Integration tests: `tests/test_X_integration.py` (15-40 tests)
   - Subagent runs pytest to verify before returning
5. **Verify in main session:** `uv run pytest tests/test_X_integration.py -q`
6. **Commit all 4 files:** pyproject.toml, uv.lock, evaluation script, test file
7. **Close issue with specifics:** version, test count, capabilities verified

### Key learnings:
- Always check if already integrated FIRST — Pint was fully done (module + 22 tests) but issue was still open
- The smoke test in step 3 catches API changes (ht 1.2.0 moved `nearest_pipe`, GeoPandas deprecated `unary_union`)
- Pass API change findings to the subagent so it doesn't hit the same errors
- Engineering-domain evaluation scripts (offshore platform locations, subsea pipeline U-value, Morison equation) are much more valuable than generic demos — they serve as reference code for future work
- One subagent per library is fastest; batching 2 libraries into one subagent wastes context on the second

### Libraries that follow this pattern well:
- PyVista (3D mesh viz), Pint (units), ht (heat transfer), GeoPandas (spatial)
- sectionproperties, fluids, chemicals, wavespectra, meshio
- Any library where: pip install + smoke test + tests = done

## Maturity promotion: verify-and-close pattern

When parent issues track maturity promotion (e.g., DEVELOPMENT→TESTED), check if child issues have collectively met the threshold rather than doing more work:

1. Count source files and test files: `find src/... -name '*.py' | wc -l` vs `find tests/... -name 'test_*.py' | wc -l`
2. If test/source ratio exceeds threshold (e.g., 80%), close the parent
3. Comment with exact numbers and child issue references that contributed
4. This saved a full planning+execution cycle on #1639 which was closable after #1784 completed

## Already-done issue sweep: aggressive verification-first approach

This session closed 18 issues — but 7 of them required ZERO code changes because the work was already done. The verification-first sweep is the highest-ROI activity in batch execution:

### Pattern: scan for closable issues before writing code
1. Pull full issue list with `gh issue list --state open --label "machine:dev-primary" --limit 50`
2. For EACH issue, before planning any work:
   a. Check if deliverable files exist (`ls -la path/to/expected/file`)
   b. If code exists, run its tests (`uv run pytest path/to/tests -v`)
   c. If implementation comments exist on the issue, read them for commit hashes
   d. If everything passes, close immediately with verification evidence
3. Typical yield: 30-40% of issues on a mature repo are already done but not closed

### Issues that are commonly already done:
- Issues with implementation comments (someone committed but forgot to close)
- Child issues whose parent was implemented in a single sweep
- Bug fixes from retroactive reviews (reviewer filed issues, fixer resolved multiple in one commit)
- Schema/convention issues that were fixed as part of a larger refactor

### Shell injection / security review issues
When Codex adversarial review files security issues, check each reported vulnerability:
- The SPECIFIC files/patterns cited may already be fixed
- Search for the vulnerable pattern (`grep 'python3 -c' scripts/`)
- If the pattern is gone or already uses safe heredocs, close with verification
- But ALSO search broadly — the pattern may exist in unreported files (this session found 8 additional vulnerable scripts beyond the 2 reported)

## Pytest collection error triage shortcut

When an issue reports N collection errors from missing dependencies:
1. Check which deps are already installed: `uv run python -c "import X"`
2. Library integration work in the same session may have already fixed most errors
3. Run `uv run pytest --collect-only -q 2>&1 | tail -3` to get current count
4. If the count is below the acceptance threshold, close immediately
5. This session: 149 errors → 1 error just from installing PyVista + ht + GeoPandas as part of other issues

## digitalmodel nested repo: commit + push requires working from within digitalmodel/

The digitalmodel repo is gitignored inside workspace-hub. Commits must be made from within `digitalmodel/` directory. When pushing fails with "Everything up-to-date" from workspace-hub root, verify with `git log origin/main --oneline -1` — it may already be pushed. The sparse overlay can cause confusing `git push` messages.

## Recommended output back to user
After each wave or checkpoint, report:
- issues completed (with breakdown: new work vs verified-already-done)
- commit hashes pushed
- what remains feasible next
- whether anything is only local vs already pushed
- running totals (tests written, issues closed)
