# Plan for #3198: pre-push new-branch push path-filters via merge-base instead of running all tier-1 repos

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-01
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3198
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-01-plan-3198-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `tests/hooks/test_pre_push.py` — 10-test TDD suite already written for
  `scripts/hooks/pre-push.sh`. 9 of 10 tests currently fail (exit 127: hook file missing); the
  one passing test (`test_skip_does_not_run_checks`) passes accidentally because an absent hook
  never invokes `check-all.sh`, leaving the calls log empty.
- Found: `.git/hooks/pre-push` — does NOT exist in this clone (fresh checkout). The live hook on
  dev-primary is untracked; its logic at lines 94-103 is reconstructed from plan
  `docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md` (see Evidence below).
- MISSING: `scripts/hooks/pre-push.sh` — canonical tracked implementation referenced by all tests;
  never created despite being the intent since at least issue #2128 (April 2026).
- Found: `scripts/testing/run-all-tests.sh` — accepts `--repo <name>` flag; tier-1 repo list from
  `scripts/lib/tier1-repos.sh`.
- Found: `scripts/quality/check-all.sh` — accepts `--repo <name>` flag; same tier-1 source.
- Found: `scripts/enforcement/install-hooks.sh` — appends enforcement layers
  (review-gate, stage-prompt-drift, state-file-size, cadence-sync) to an existing pre-push hook;
  does NOT create the base hook. The base hook (`scripts/hooks/pre-push.sh`) is the missing piece.
- Found: Issue #2203 (OPEN) — broader worktree-awareness epic (absent sibling repos); its April 2026
  draft plan documents the existing live hook lines 94-103 (RUN_ALL on new-branch).

### Standards

| Standard | Status | Source |
|---|---|---|
| `.claude/rules/coding-style.md` — "use relative paths or `$(git rev-parse --show-toplevel)`" | relevant | repo rule |
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | relevant (GIT_PRE_PUSH_SKIP) | repo standard |

### LLM Wiki pages consulted

- No relevant wiki pages — this is a git-hooks / harness infrastructure issue.

### Documents consulted

- Issue #3198 body (2026-06-17) — root cause, proposed fix (merge-base diff), and explicit scope
  constraints ("preserve genuine-disconnected-history fallback and harness-file config-drift check").
- `docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md` — documents the live
  hook's exact line numbers (94-103) and the `RUN_ALL=true` pattern; confirms `scripts/hooks/pre-push.sh`
  was always the intended tracked home for this logic.
- Issue #3179 (closed 2026-06-17) — fixed `REPO_ROOT-under-hook` using git-free structural root
  pattern; that same `REPO_ROOT="$(cd SCRIPT_DIR/../.. && pwd)"` idiom applies here.
- Issue #2203 (OPEN) — sibling issue for worktree-awareness; distinct from #3198's new-branch
  merge-base fix. Plans do not conflict: #2203 covers absent-sibling-repo discovery; #3198 covers
  over-gating on docs-only new branches.

### Gaps identified

- `scripts/hooks/pre-push.sh` does not exist — must be created from scratch.
- No test covers new-branch + merge-base path-filter (happy path); only the fallback
  (no merge-base → RUN_ALL) is tested via `test_new_branch_runs_all_repos`.
- The hook will need a `PRE_PUSH_CHANGED_FILES` env override so tests can inject the git-diff
  output for both existing-branch AND new-branch paths without needing real commits.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-01):
- `#3198` — OPEN — `bug(pre-push): new-branch push runs ALL tier-1 test suites even for docs-only / non-tier-1 changes`
- `#2203` — OPEN — `fix(harness): make pre-push tier-1 repo checks worktree-aware for integration branches`
- `#3179` — CLOSED/completed — `fix(pre-push): REPO_ROOT-under-hook broken`
- `#2128` — existence of `scripts/hooks/pre-push.sh` intent confirmed in plan history

**File existence** (`ls` 2026-07-01):
- EXISTS: `tests/hooks/test_pre_push.py`
- EXISTS: `scripts/testing/run-all-tests.sh`
- EXISTS: `scripts/quality/check-all.sh`
- EXISTS: `scripts/enforcement/install-hooks.sh`
- MISSING (this plan creates): `scripts/hooks/pre-push.sh`

**Test run confirming 9 failing** (2026-07-01):
```
$ uv run python -m pytest tests/hooks/test_pre_push.py -q
FAILED tests/hooks/test_pre_push.py::TestChangedOnly::test_changed_repo_subset_is_run
FAILED tests/hooks/test_pre_push.py::TestAllMode::test_all_flag_runs_every_repo
FAILED tests/hooks/test_pre_push.py::TestFailureBlocks::test_failing_check_all_blocks_push
FAILED tests/hooks/test_pre_push.py::TestFailureBlocks::test_failing_run_tests_blocks_push
FAILED tests/hooks/test_pre_push.py::TestSkipBypass::test_skip_exits_zero
FAILED tests/hooks/test_pre_push.py::TestSkipBypass::test_skip_writes_jsonl_record
FAILED tests/hooks/test_pre_push.py::TestNewBranchFallback::test_new_branch_runs_all_repos
FAILED tests/hooks/test_pre_push.py::TestNewBranchFallback::test_delete_branch_skipped
FAILED tests/hooks/test_pre_push.py::TestSmokeHelp::test_help_exits_zero
9 failed, 1 passed in 0.15s
```

Failure reason: `bash: .../scripts/hooks/pre-push.sh: No such file or directory`

**Live hook excerpt** (from `docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md:86`):
```bash
# .git/hooks/pre-push (live on dev-primary, untracked)
94|if [[ "$FIRST_REMOTE_OID" == "$ZERO_OID" ]]; then
95|    echo "[pre-push] New branch — running all tier-1 repo checks." >&2
96|    RUN_ALL=true
97|fi
102|if [[ "$RUN_ALL" == "true" ]]; then
103|    REPOS_TO_CHECK=("${TIER1_REPOS[@]}")
```

- Reproduced at: 2026-07-01 (missing hook confirmed; live RUN_ALL behavior from plan evidence)
- Failure mode matches issue claim: YES

<!-- Source count: issue body (1) + tests/hooks/test_pre_push.py (2) + plan 2203 (3) + install-hooks.sh (4) + run-all-tests.sh (5) = 5 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-01-issue-3198-pre-push-new-branch-merge-base-diff.md |
| Implementation (new) | `scripts/hooks/pre-push.sh` |
| Tests (modify) | `tests/hooks/test_pre_push.py` |
| Plan review — Claude | scripts/review/results/2026-07-01-plan-3198-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-01-plan-3198-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-01-plan-3198-gemini.md |

---

## Deliverable

`scripts/hooks/pre-push.sh` will exist as the canonical tracked implementation of the workspace-hub
pre-push tier-1 gate; on new-branch pushes it will diff against `git merge-base origin/main HEAD`
(path-filter to affected repos only) rather than unconditionally running all tier-1 suites; all
10 existing tests will pass plus a new test for the merge-base path-filter happy path.

---

## Pseudocode

```
pre-push.sh:
  if --help: print usage, exit 0

  read stdin: local_ref local_oid remote_ref remote_oid

  if GIT_PRE_PUSH_SKIP=1:
    write JSONL record to PRE_PUSH_BYPASS_LOG (timestamp, refs, operator, exit_code=0)
    exit 0

  if local_oid == ZERO_OID:
    exit 0  # branch deletion — nothing to check

  if PRE_PUSH_CHANGED_FILES set:
    CHANGED = $PRE_PUSH_CHANGED_FILES   # test override for both paths
  elif remote_oid == ZERO_OID:          # new branch
    BASE=$(git merge-base origin/main "$local_oid" 2>/dev/null)
    if BASE is non-empty:
      CHANGED=$(git diff --name-only "$BASE..$local_oid")
    else:
      RUN_ALL=true                      # genuinely disconnected history
  else:                                 # existing branch
    CHANGED=$(git diff --name-only "$remote_oid..$local_oid")

  if RUN_ALL:
    REPOS_TO_CHECK = all TIER1_REPOS
  else:
    REPOS_TO_CHECK = [r for r in TIER1_REPOS if CHANGED matches "^r/"]

  for repo in REPOS_TO_CHECK:
    run CHECK_ALL_SCRIPT --repo repo   || FAIL=1
    run RUN_TESTS_SCRIPT --repo repo   || FAIL=1

  exit FAIL

env overrides (test seams):
  PRE_PUSH_CHECK_ALL_SCRIPT   → replaces scripts/quality/check-all.sh
  PRE_PUSH_RUN_TESTS_SCRIPT   → replaces scripts/testing/run-all-tests.sh
  PRE_PUSH_CHANGED_FILES      → replaces git diff output (both paths)
  PRE_PUSH_BYPASS_LOG         → replaces default bypass log path
  PRE_PUSH_DRY_RUN=1          → exits 0 after printing plan (no real checks)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/hooks/pre-push.sh` | Canonical tracked hook implementation (previously untracked in `.git/hooks/pre-push`) |
| Modify | `tests/hooks/test_pre_push.py` | Add `test_new_branch_path_filters_via_merge_base` to `TestNewBranchFallback` |

---

## TDD Test List

**Existing tests (9 failing → must pass after implementation):**

| Test | What it verifies |
|---|---|
| `test_changed_repo_subset_is_run` | changed-only path: only touched repo runs |
| `test_all_flag_runs_every_repo` | `--all` flag forces all repos |
| `test_failing_check_all_blocks_push` | failing check-all exits 1 |
| `test_failing_run_tests_blocks_push` | failing run-tests exits 1 |
| `test_skip_exits_zero` | `GIT_PRE_PUSH_SKIP=1` exits 0 |
| `test_skip_writes_jsonl_record` | bypass log contains required keys |
| `test_new_branch_runs_all_repos` | new branch with no merge-base (fake OIDs → merge-base fails) → RUN_ALL fallback |
| `test_delete_branch_skipped` | local_oid=ZERO_OID → exit 0, no checks |
| `test_help_exits_zero` | `--help` exits 0 and prints "pre-push" or "usage" |

**New test (write RED before implementation):**

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_new_branch_path_filters_via_merge_base` | `remote_oid=ZERO_OID` + `PRE_PUSH_CHANGED_FILES=assetutilities/src/foo.py` → only assetutilities runs | `remote_oid=ZERO_OID`, `PRE_PUSH_CHANGED_FILES="assetutilities/src/foo.py"` | calls log contains "assetutilities"; does NOT contain "digitalmodel", "worldenergydata", "assethold", "OGManufacturing" |

**Implementation order (TDD):**
1. Write `test_new_branch_path_filters_via_merge_base` — RED (hook missing)
2. Create `scripts/hooks/pre-push.sh` with full logic
3. All 10 existing + 1 new = 11 tests GREEN

---

## Acceptance Criteria

- [ ] All 11 tests pass: `uv run pytest tests/hooks/test_pre_push.py -v`
- [ ] `scripts/hooks/pre-push.sh` is executable (`chmod +x`)
- [ ] `bash scripts/hooks/pre-push.sh --help` exits 0 and prints usage
- [ ] Manual verify: on a docs-only new branch with `PRE_PUSH_CHANGED_FILES=""`, hook exits 0 and runs 0 repos (no tier-1 path touched)
- [ ] Existing pre-push chain: `install-hooks.sh` can append its enforcement layers after `scripts/hooks/pre-push.sh` is installed into `.git/hooks/pre-push` (idempotency preserved)
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

<!-- To be filled after Step 4 completes. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

---

## Risks and Open Questions

- **Risk (medium):** `test_new_branch_runs_all_repos` currently expects RUN_ALL behavior when
  `remote_oid=ZERO_OID` and NO `PRE_PUSH_CHANGED_FILES`. With the fix, this path calls
  `git merge-base origin/main FAKE_OID` — which will fail in a test environment (FAKE_OID doesn't
  exist in git history), triggering the RUN_ALL fallback. The test expectation is unchanged; the
  mechanism is different (fail-safe fallback instead of unconditional RUN_ALL). This is intentional
  and correct — do NOT change the test.
- **Risk (low):** `git merge-base origin/main HEAD` requires `origin/main` to be fetched. In the
  pre-push hook, `origin/main` is always present (we just authenticated to push). No additional
  fetch is needed. In offline or detached-HEAD environments, merge-base fails → falls back to
  RUN_ALL (correct conservative behavior per issue body).
- **Risk (low):** The hook installs via `install-hooks.sh` (appends to `.git/hooks/pre-push`).
  The base hook at `scripts/hooks/pre-push.sh` must be copied/symlinked to `.git/hooks/pre-push`
  first. Add a note to `install-hooks.sh` or its README that the base hook must be installed before
  the enforcement chain is appended. Out of scope for this plan (scope: create + test the file).
- **Open:** Should this plan update `install-hooks.sh` to auto-install `scripts/hooks/pre-push.sh`?
  Deferred — `install-hooks.sh` is guarded by `if [[ -f "$PRE_PUSH" ]]` and only appends;
  bootstrapping the base hook is a separate installation step. Flag for user during approval.

---

## Complexity: T2

New file created (`scripts/hooks/pre-push.sh`, ~80 lines of bash); one new test added to an
existing test file; no existing code modified. Complexity is T2 because the hook integrates
multiple code paths (new-branch, existing-branch, delete, skip-bypass, `--help`, env overrides)
and must not regress any of the 10 existing test cases.
