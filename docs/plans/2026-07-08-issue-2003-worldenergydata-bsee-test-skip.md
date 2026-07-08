# Plan for #2003: Fix 5 failing tests in worldenergydata — BSEE data skip markers

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2003
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-08-plan-2003-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- **Gap:** worldenergydata is not checked out in the planning environment (this is a remote session; repo lives on ace-linux-1 at `/mnt/local-analysis/worldenergydata`). Exact test file paths and function names must be identified by the implementer using the commands in the Reproduction Proofs section.
- **Found (via issue comment 2026-04-07):** After an overnight batch fix (commit `22e0f32`) that excluded 14 broken test directories and fixed `norecursedirs`, the suite reached 222 passed / 13 skipped / 0 collection errors. The 5 remaining failures all require BSEE data from `/mnt/ace/worldenergydata/data/modules/bsee` which is not committed to the repo to avoid bloat.
- **Found (issue body):** The command to run the suite is `cd assetutilities && uv run python -m pytest ../worldenergydata/tests/ --noconftest` or from the worldenergydata root.
- **Gap:** No existing `@pytest.mark.skipif` pattern for machine-specific data paths has been verified in worldenergydata; must check for a conftest.py fixture to reuse.

### Standards
Not applicable — test infrastructure issue.

### LLM Wiki pages consulted
No relevant wiki pages.

### Documents consulted
- Issue #2003 body — specifies "5 errors detected during collection"; acceptance criteria: all 431 tests pass with 0 errors
- Issue #2003 comment 1 (2026-04-07T19:58:51Z) — overnight batch fix reached "222 passed, 13 skipped, 0 collection errors; 5 remaining failures need BSEE data from /mnt/ace/worldenergydata/data/modules/bsee (not in repo to avoid bloat)"
- worldenergydata#2433 close-out context in issue #2424 — established pattern for worldenergydata CI fixes; `pytest.ini` with `norecursedirs` is in use
- Prior plan: no plan file found for issue #2003 (`ls docs/plans/ | grep 2003` → empty)
- Issue #2005 (same issue family, lane:codex) — addresses test collection timeout; separate scope, separate lane

### Gaps identified
- Exact names of the 5 failing test functions are unknown from the planning environment; implementer must run `uv run python -m pytest tests/ -v --tb=short 2>&1 | grep FAILED` on ace-linux-1 to enumerate them.
- It is unknown whether worldenergydata has an existing conftest.py pytest fixture or skip mark for external data paths; implementer must check before creating a new pattern.
- The acceptance criterion "All 431 tests pass with 0 errors" may be overly strict: if 222 pass and 13 skip after the overnight fix, the 5 BSEE-failing tests + the 13 already-skipped = 196 tests are unaccounted for. Implementer must reconcile the count (likely the overnight fix changed which tests are collected) and target 0 errors / 0 failures with skips allowed for absent-data tests.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-08T13:15Z via `mcp__github__issue_read`):
- `#2003` — OPEN — "Fix 5 failing tests in worldenergydata — test suite cleanup (#1962 Phase 3)"

**File existence** (planning env, worldenergydata not checked out):
- MISSING (not in this env): `/mnt/local-analysis/worldenergydata` — worldenergydata repo lives on ace-linux-1
- EXISTS (workspace-hub): `docs/plans/` — confirmed no `2003`-prefixed plan file

**Issue comment evidence** (`mcp__github__issue_read get_comments page=1`):
```
Comment 2026-04-07T19:58:51Z:
  "Result: 222 passed, 13 skipped, 0 collection errors
   5 remaining failures need BSEE data from /mnt/ace/worldenergydata/data/modules/bsee
   (not in repo to avoid bloat)"
```

**Reproduction proofs:**
N/A — worldenergydata not checked out in planning environment (remote cloud session; repo on ace-linux-1). Implementer must reproduce on ace-linux-1:
```
cd /mnt/local-analysis/worldenergydata
uv run python -m pytest tests/ -v --tb=short 2>&1 | grep -E 'FAILED|ERROR|passed|failed'
```
Expected: 5 failures referencing `/mnt/ace/worldenergydata/data/modules/bsee` paths.
Failure mode to confirm matches issue claim: YES (per issue comment evidence above).

<!-- Distinct sources: (1) issue body, (2) issue comment 2026-04-07, (3) issue #2424 triage context, (4) prior plan absence check. Count: 4 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-08-issue-2003-worldenergydata-bsee-test-skip.md |
| Conftest or skip fixture | `worldenergydata/tests/conftest.py` (extend or create) |
| Test files modified (×5) | `worldenergydata/tests/<path>/<test_file>.py` — 5 files, identified at implementation time |
| Plan review — Claude | scripts/review/results/2026-07-08-plan-2003-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-08-plan-2003-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-08-plan-2003-gemini.md |

---

## Deliverable

The 5 worldenergydata tests that currently fail with missing-BSEE-data errors will be marked with `pytest.mark.skipif` conditions so the suite reaches 0 failures / 0 errors on any machine where `/mnt/ace/worldenergydata/data/modules/bsee` is absent, while still executing (and expected to pass) on ace-linux-1 where that path exists.

---

## Pseudocode

```
# Step 1: Enumerate failures on ace-linux-1
cd /mnt/local-analysis/worldenergydata
uv run python -m pytest tests/ -v --tb=short 2>&1 | grep FAILED
# → produces list of test::function names

# Step 2: For each failing test, identify the data-path dependency
grep -n "/mnt/ace" tests/<failing_test_file>.py

# Step 3a: Check for existing conftest.py skip fixture
cat tests/conftest.py 2>/dev/null | grep -E "skipif|skip_no_data|bsee"

# Step 3b: If no fixture exists, add to conftest.py:
#   BSEE_DATA = Path("/mnt/ace/worldenergydata/data/modules/bsee")
#   skip_no_bsee = pytest.mark.skipif(
#       not BSEE_DATA.exists(),
#       reason=f"BSEE data not available at {BSEE_DATA}"
#   )

# Step 4: Apply to each failing test:
#   @skip_no_bsee
#   def test_bsee_xxx(): ...

# Step 5: Verify
uv run python -m pytest tests/ -v 2>&1 | grep -E 'passed|failed|error|skip'
# Expected: 0 failures, 0 errors; ≥5 skips on machines without BSEE data
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create or extend | `worldenergydata/tests/conftest.py` | add `skip_no_bsee` mark definition |
| Modify (×5) | `worldenergydata/tests/<path>/<test_file>.py` | apply `@skip_no_bsee` to each of the 5 failing tests |
| Update | docs/plans/README.md | add plan to index |

---

## TDD Test List

TDD here means: write the skip-logic test first (confirm the skip fires on a machine without BSEE data), then apply the marker to the 5 failing tests.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_bsee_skip_fires_when_data_absent` | conftest skip mark exits correctly when path absent | `BSEE_DATA` mocked to non-existent path | test marked `xfail` or `skip` — NOT error |
| `test_suite_zero_failures_without_bsee` | full suite on machine without `/mnt/ace/…/bsee` | run `pytest tests/` on CI or machine lacking path | `0 failures, 0 errors, ≥5 skipped` |
| `test_suite_zero_failures_with_bsee` | all 5 tests PASS on machine with BSEE data | run on ace-linux-1 with data present | `0 failures, 0 errors, ≥227 passed` |
| `test_skip_mark_not_applied_to_non_bsee_tests` | regression — no accidental broad skip | count of skipped tests same as before on CI | skip count ≤ (pre-existing skips + 5) |

The first two tests can be written and confirmed on ANY machine. The third requires ace-linux-1 with BSEE data; document expected result and note as machine-gated.

---

## Acceptance Criteria

- [ ] Running `uv run python -m pytest tests/ -v` on ace-linux-1 (BSEE data present) produces 0 failures, 0 errors
- [ ] Running the same command on any machine WITHOUT `/mnt/ace/worldenergydata/data/modules/bsee` produces 0 failures, 0 errors, with exactly 5 (or more) tests skipped and a human-readable reason printed
- [ ] No test regressions: tests that currently pass on CI continue to pass
- [ ] `conftest.py` skip fixture is documented with a comment explaining the `/mnt/ace` path policy
- [ ] Commits follow TDD convention: conftest.py + skip test first, then marker application

---

## Adversarial Review Summary

<!-- To be filled after adversarial review. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (pending) | |
| Codex | (pending) | |
| Gemini | (pending) | |

**Overall result:** (pending)

---

## Risks and Open Questions

- **Risk:** The 431-test count from the issue body may not match current state after the overnight fix applied 14 directory exclusions. Implementer must reconcile the actual count before claiming "all 431 pass".
- **Risk:** `/mnt/ace/` is a machine-specific mount point. If tests also run on ace-linux-2 (where `/mnt/local-analysis/worldenergydata` was absent per agents.md), the skip condition must account for that machine's path layout.
- **Open:** Should BSEE data path be overridable via a `WORLDENERGYDATA_BSEE_PATH` environment variable for CI? (Flag for user — adds flexibility but adds complexity. Default to hardcoded skip unless user prefers env-var pattern.)
- **Open:** The test count discrepancy (431 claimed, 222 passing after overnight fix) suggests some tests were excluded entirely from collection. Verify whether those exclusions are in `pytest.ini norecursedirs` and whether they should be reinstated or permanently retired.

---

## Complexity: T2

Multi-file (conftest.py + 5 test files) across a sibling repo (worldenergydata). Requires execution on machine:dev-primary (ace-linux-1) for full verification since BSEE data is only present there. Cannot be fully reproduced in a cloud/remote session.
