# Plan for #3368: Day-to-day friction guards — CI failure classifier + MEMORY.md compaction (items 2 + 5)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3368
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-08-plan-3368-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

**Item 3 (gh-auth preflight) — ALREADY IMPLEMENTED:**
- Found: `scripts/enforcement/check-gh-auth.sh` — fully implemented, references `wh#3368` in its header comment; confirmed present 2026-07-08. This item requires no further work.

**Item 2 (baseline-red CI classifier):**
- Gap: `scripts/ci/` directory does NOT exist (`ls scripts/ci/ 2>/dev/null` → exit 2). No `classify-pr-failures.sh` exists anywhere in the repo.
- Found: Pattern reference in `scripts/enforcement/check-gh-auth.sh` — uses `gh api user -q .login` for authenticated API calls; same `gh` invocation pattern will be used for `gh run list`.
- Found: `scripts/enforcement/tests/` directory exists with `test_check_no_abs_paths.sh`, `test_check_harness_file_size.sh`, `test_require_review_on_push.sh`. The test harness uses `pass()` / `fail()` / `run_test()` bash helpers + injectable fake binaries (e.g. `GH_BIN` override in `check-gh-auth.sh`). New script will follow this exact pattern.
- Found: `scripts/enforcement/tests/fixtures/ok/` and `fixtures/violating/` fixture layout — new script tests will use `fixtures/ci-classifier/` parallel layout.

**Item 5 (compact-memory.py MEMORY.md rewrite):**
- Found: `scripts/memory/compact-memory.py` — exists (470 lines). Key gaps confirmed:
  - Line 35: `MEMORY_MD_LIMIT = 180  # lines; trigger compaction` — trigger is LINE-COUNT only
  - Line 121-133 (`_triggers_met`): checks `MEMORY.md` line count; does NOT check byte size
  - Line 454: `lines_freed_memory=0,  # MEMORY.md rewrite not yet implemented` — literal "not yet implemented" debt marker
  - Phase A `audit()` function (line 138): audits topic files only; does NOT audit `MEMORY.md` bullets
  - Phase C `apply_evictions()` (line 310): rewrites topic files only; skips `MEMORY.md`
- Found: `scripts/enforcement/check-memory-index-size.sh` — byte-based guard: warn at 17 KiB, hard-fail at 24 KiB. Looks for `~/.claude/projects/*/memory/MEMORY.md`. The guard fires when compact-memory.py has NOT triggered (because MEMORY.md's line count is below 180 but byte size exceeds 17 KiB). This is the gap the issue describes as "triggers on lines not bytes."
- Gap: `compact-memory.py` has no byte-based trigger for MEMORY.md; adding one will close the gap between the guard script (bytes) and the compactor (lines).
- Note: In remote cloud session, the auto-memory index file is named `INDEX.md` not `MEMORY.md`. On ace-linux-1 (machine:dev-primary), the file is `MEMORY.md` per `check-memory-index-size.sh`'s glob. Implementer must confirm the filename on ace-linux-1 before wiring the byte trigger. Script should accept `--memory-index-name MEMORY.md` defaulting to `MEMORY.md` for forward-compatibility.

### Standards
Not applicable — tooling/infrastructure issue.

### LLM Wiki pages consulted
No relevant wiki pages.

### Documents consulted
- Issue #3368 body (2026-07-03) — specifies all 5 items; item 1 merged (#3366/PR#3367), item 3 already merged (check-gh-auth.sh confirms); items 2, 4, 5 remain
- `scripts/enforcement/check-gh-auth.sh` — implementation reference + `GH_BIN` injection pattern for testing
- `scripts/memory/compact-memory.py` — read in full (470 lines); gaps at lines 35, 121-133, 310-350, 454
- `scripts/enforcement/check-memory-index-size.sh` — read in full; byte threshold contract (17/24 KiB)
- `scripts/enforcement/tests/test_check_no_abs_paths.sh` — test harness pattern reference (pass/fail/run_test + fixture dirs)
- `.claude/rules/patterns.md` — enforcement gradient (Level-2 script → Level-3 hook promotion path)

### Gaps identified
- `scripts/ci/` directory does not exist; must be created with a README or the script itself
- `classify-pr-failures.sh` does not exist; must be created from scratch
- `compact-memory.py` MEMORY.md compaction is explicitly deferred ("not yet implemented")
- Byte trigger for MEMORY.md is missing from `compact-memory.py`
- Item 4 (digitalmodel worktree symlink `scripts/dev/ensure-worktree-deps.sh`) is OUT OF SCOPE for this plan — it lives in the `digitalmodel` repo, not workspace-hub, and requires a separate plan under the `digitalmodel` repo.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-08T13:xx via `mcp__github__issue_read`):
- `#3368` — OPEN — "Day-to-day friction guards (session-grounded suite) — reduce recurring time-sinks"
- `#3366` — (item 1 merged per issue body) — auto-memory index byte guard

**File existence** (`ls` 2026-07-08T13:xx):
- EXISTS: `scripts/enforcement/check-gh-auth.sh` — item 3 DONE
- EXISTS: `scripts/enforcement/tests/` — test harness directory
- EXISTS: `scripts/memory/compact-memory.py` — item 5 partial (needs MEMORY.md rewrite)
- MISSING: `scripts/ci/` — confirmed `exit 2` on `ls scripts/ci/`
- MISSING: `scripts/enforcement/tests/fixtures/ci-classifier/` — to be created

**Key line excerpts** from `compact-memory.py`:
```
Line 35:  MEMORY_MD_LIMIT = 180       # lines; trigger compaction
Line 454: lines_freed_memory=0,  # MEMORY.md rewrite not yet implemented
```

**Gap proofs**:
- `ls scripts/ci/ 2>/dev/null` → exit 2 → confirms directory does not exist
- `grep -n "lines_freed_memory" scripts/memory/compact-memory.py` → line 454: `lines_freed_memory=0,  # MEMORY.md rewrite not yet implemented`

**Reproduction proofs:**
N/A — this plan adds new capabilities, not fixing a reported runtime failure. Item 3 reproduction (gh-auth preflight): confirmed script exists and functions as described. Item 5 reproduction (MEMORY.md rewrite missing): confirmed at line 454 of compact-memory.py.

<!-- Distinct sources: (1) issue #3368 body, (2) check-gh-auth.sh (item-3 done evidence), (3) compact-memory.py code reading, (4) check-memory-index-size.sh contract, (5) test harness pattern. Count: 5 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-08-issue-3368-ci-classifier-memory-compaction.md |
| New CI script | `scripts/ci/classify-pr-failures.sh` |
| CI script tests | `scripts/enforcement/tests/test_classify_pr_failures.sh` |
| CI test fixtures | `scripts/enforcement/tests/fixtures/ci-classifier/ok/` and `violating/` |
| Compact-memory extension | `scripts/memory/compact-memory.py` (extend `_triggers_met` + `apply_evictions`) |
| Compact-memory tests | `scripts/memory/tests/test_compact_memory_index.py` (create) |
| Plan review — Claude | scripts/review/results/2026-07-08-plan-3368-claude.md |
| Plan review — Codex | scripts/review/results/2026-07-08-plan-3368-codex.md |
| Plan review — Gemini | scripts/review/results/2026-07-08-plan-3368-gemini.md |

---

## Deliverable

Two enforcement capabilities will exist that do not exist now:
1. `scripts/ci/classify-pr-failures.sh <repo> <pr-number>` — prints each failing CI check as `BASELINE` (also failing on main) or `REGRESSION` (green on main, red on PR), turning a 10-minute manual investigation into one command.
2. `compact-memory.py` will compact MEMORY.md alongside topic files, with a byte-based trigger for MEMORY.md that aligns with `check-memory-index-size.sh`'s 17 KiB warn threshold.

---

## Pseudocode

### Item 2 — classify-pr-failures.sh

```
classify-pr-failures.sh <repo> <pr-number>

USAGE_CHECK: require 2 args; print usage on failure; exit 2

# Fetch PR's failing check names
pr_failing = gh pr checks <pr-number> --repo <repo> --json name,state \
    | jq -r '.[] | select(.state=="FAILURE") | .name'

# If no failures, print "No failing checks on PR #N" and exit 0

# Fetch main's latest check run results for the same workflow names
main_run_id = gh run list --repo <repo> --branch main --limit 1 --json databaseId \
    | jq -r '.[0].databaseId'
main_results = gh run view <main_run_id> --repo <repo> --json jobs \
    | jq -r '.jobs[] | {name: .name, conclusion: .conclusion}'

# Classify each PR failing check:
for each check in pr_failing:
    main_conclusion = lookup main_results by check name
    if main_conclusion == "failure":
        print "BASELINE  <check>  (also failing on main — pre-existing)"
    else:
        print "REGRESSION  <check>  (green on main, red on PR — likely caused by this PR)"

exit 0 if at least one result printed; exit 1 if gh API calls fail
```

**Key design decision:** Join by CHECK NAME (job name string), not run ID. main's latest run and the PR's run share workflow-defined check names even across different commits. This is the correct join key — run IDs are not comparable across branches.

### Item 5 — compact-memory.py MEMORY.md compaction

```
# New function: compact_memory_index(memory_root, byte_budget=17*1024)
#   - Read MEMORY.md (or INDEX.md — accept --memory-index-name arg)
#   - Count bytes; if <= byte_budget, return 0 (nothing to do)
#   - Identify "Archive" section lines below the active entries
#   - Remove oldest archived bullets until byte count <= byte_budget
#   - Write atomically (tmp → replace); return lines_freed

# Extend _triggers_met():
#   - AFTER existing line-count check, add byte-count check for MEMORY.md:
#     memory_md = memory_root / "MEMORY.md"
#     if memory_md.exists() and memory_md.stat().st_size >= MEMORY_MD_WARN_BYTES:
#         return "memory-index-byte-oversize"
#   - New constant: MEMORY_MD_WARN_BYTES = 17 * 1024  (matches check-memory-index-size warn)

# Extend main():
#   - After apply_evictions(), call compact_memory_index(memory_root)
#   - Pass result to _write_log() as lines_freed_memory (replacing hardcoded 0)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create dir + file | `scripts/ci/classify-pr-failures.sh` | item 2: CI failure classifier |
| Create | `scripts/enforcement/tests/test_classify_pr_failures.sh` | TDD for item 2 |
| Create dir | `scripts/enforcement/tests/fixtures/ci-classifier/ok/` | test fixtures (no failures case) |
| Create dir | `scripts/enforcement/tests/fixtures/ci-classifier/regression/` | test fixtures (REGRESSION case) |
| Create dir | `scripts/enforcement/tests/fixtures/ci-classifier/baseline/` | test fixtures (BASELINE case) |
| Modify | `scripts/memory/compact-memory.py` | item 5: MEMORY.md compaction + byte trigger |
| Create | `scripts/memory/tests/test_compact_memory_index.py` | TDD for item 5 |
| Update | docs/plans/README.md | add this plan to index |

---

## TDD Test List

### Item 2 — classify-pr-failures.sh

The script uses `gh` CLI; inject a fake `GH_BIN` (matching `check-gh-auth.sh` pattern) that returns fixture JSON.

| Test name | What it verifies | Fixture | Expected output |
|---|---|---|---|
| `test_no_args_prints_usage` | usage guard fires | — | exit 2, stderr contains "Usage:" |
| `test_no_pr_failures_exits_clean` | PR with no failing checks | fake gh: `pr checks` returns all success | "No failing checks on PR #N", exit 0 |
| `test_baseline_failure_labeled_correctly` | check failing on both PR and main | fake gh: same check name fails on both | output line starts with "BASELINE" |
| `test_regression_failure_labeled_correctly` | check failing on PR only | fake gh: check passes on main, fails on PR | output line starts with "REGRESSION" |
| `test_mixed_failures_both_labeled` | PR has one BASELINE + one REGRESSION | fake gh: two checks, one each | both labels present in output |
| `test_gh_api_failure_exits_nonzero` | gh CLI fails | fake gh: returns exit 1 | script exits non-zero |

### Item 5 — compact-memory.py MEMORY.md compaction

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_memory_index_not_compacted_when_under_budget` | no-op when MEMORY.md small | MEMORY.md 5 KiB | `lines_freed_memory=0` in log |
| `test_memory_index_triggers_on_byte_oversize` | byte trigger fires | MEMORY.md 18 KiB (> 17 KiB warn) | `_triggers_met()` returns "memory-index-byte-oversize" |
| `test_memory_index_compacted_to_under_budget` | compact reduces bytes | MEMORY.md 20 KiB | after compact, MEMORY.md < 17 KiB |
| `test_memory_index_active_entries_preserved` | active bullets not evicted | MEMORY.md with 5 active + 10 archive bullets | 5 active bullets still present after compact |
| `test_memory_index_atomic_write` | no partial writes | MEMORY.md 20 KiB | no `.tmp` file left on disk after compact |
| `test_log_records_lines_freed_memory` | log entry updated | compact run that frees memory index lines | `compact-log.jsonl` has `lines_freed_memory > 0` |
| `test_byte_trigger_does_not_fire_below_threshold` | no false positives | MEMORY.md 16 KiB (< 17 KiB) | trigger returns None (no compaction) |

---

## Acceptance Criteria

- [ ] `scripts/ci/classify-pr-failures.sh <repo> <pr> ` prints BASELINE/REGRESSION for every failing check with 0 manual investigation needed
- [ ] All 6 CI classifier tests pass: `bash scripts/enforcement/tests/test_classify_pr_failures.sh`
- [ ] `compact-memory.py --memory-root <path>` with a 20 KiB MEMORY.md triggers compaction and reduces the file below 17 KiB
- [ ] All 7 MEMORY.md compaction tests pass: `uv run --no-project python -m pytest scripts/memory/tests/test_compact_memory_index.py -v`
- [ ] `compact-log.jsonl` records a non-zero `lines_freed_memory` value after a compaction run that processes MEMORY.md
- [ ] No regression in existing compact-memory.py behavior: topic-file compaction tests still pass
- [ ] `classify-pr-failures.sh` passes the existing `check-no-abs-paths.sh` enforcement check (no hardcoded absolute paths)
- [ ] Item 3 (check-gh-auth.sh) noted as DONE in a comment on issue #3368 — no implementation work needed

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

- **Risk:** `gh pr checks` output format may vary by GitHub CLI version. The script must handle both `jq` parse failures (non-JSON output) and empty results gracefully.
- **Risk:** When the PR is first opened and CI hasn't run yet, `gh pr checks` returns an empty list. Script should print "No check results yet for PR #N" and exit 0 rather than failing.
- **Risk:** `compact-memory.py` uses `MEMORY.md` as the hardcoded index filename. In cloud/remote sessions, the auto-memory index may be named `INDEX.md`. The implementation should accept a `--memory-index-name` argument (default: `MEMORY.md`) to support both. Verify actual filename on ace-linux-1 before finalizing.
- **Risk:** MEMORY.md compaction evicts old "Archive section" bullets — but the MEMORY.md format is not guaranteed to have a well-defined archive section. Implementer must read the actual MEMORY.md on ace-linux-1 before coding the eviction logic. If MEMORY.md has no archive section, the compaction approach must be: trim the oldest non-`# keep`-marked bullets, same as topic-file compaction.
- **Open:** Should `classify-pr-failures.sh` also support listing REGRESSION checks across ALL open PRs in a repo (not just one PR)? (Flag for user — useful but out of scope for this plan; defer to a follow-on.)
- **Open:** Item 4 (digitalmodel worktree symlink) is deliberately excluded from this plan. If user wants it planned, file a separate issue or reuse #3368 with a separate plan file for the digitalmodel portion.
- **Note:** Item 1 (#3366) and Item 3 (check-gh-auth.sh) are already implemented. This plan covers Items 2 and 5 only.

---

## Complexity: T2

Two files in different scripts sub-directories, new directory creation (`scripts/ci/`), modification of an existing 470-line Python script, and tests for both. All work is in workspace-hub — single repo. Estimated: one focused session (~3h).
