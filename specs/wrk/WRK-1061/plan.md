# WRK-1061 Plan: generate-review-input.sh

## Mission
Auto-generate a structured cross-review input file from the WRK item and its git
diff, so agents stop hand-writing review bundles and the review is always complete.

## Step 1 — `scripts/review/generate-review-input.sh WRK-NNN [--phase N]`
Single bash script, no external deps beyond standard git + coreutils.

**Logic:**
1. Parse args: `WRK-NNN` (required), `--phase N` (default: 1)
2. Find WRK item: check `pending/`, then `working/`; error if not found
3. Extract frontmatter fields via `awk` (between `---` markers):
   - title, mission text, ACs, complexity, route, subcategory, target_repos
4. Build git diff:
   - If `target_repos` non-empty: `git diff HEAD -- <repo1> <repo2> ...`
   - Else: `git diff HEAD` (full workspace diff)
   - Count lines; if >300 truncate and append: `## Diff truncated at 300/N lines`
5. Read checkpoint summary: `assets/WRK-NNN/checkpoint.yaml` → `context_summary`
6. Read test snapshot: sniff most-recent markdown from `scripts/testing/results/` (best-effort)
7. Generate focus prompts based on `subcategory` + `complexity`
8. Write to: `scripts/review/results/wrk-NNN-phase-N-review-input.md`

**Output sections:**
```
# WRK-NNN Phase N Review Input
## WRK Context       (title, mission, ACs, route, complexity)
## Changed Files + Diff  (scoped, ≤300 lines)
## Test Snapshot     (last run-all-tests.sh output or "not available")
## Checkpoint Summary
## Review Focus      (3–5 tailored prompts)
## Verdict Request
```

## Step 2 — Tests: `tests/testing/test-generate-review-input.sh`
6 test cases:
1. Basic invocation produces `wrk-NNN-phase-1-review-input.md`
2. Output contains all required section headings
3. `--phase 2` produces `wrk-NNN-phase-2-review-input.md`
4. Diff truncation notice present for >300 line diffs
5. Missing WRK item exits non-zero with clear error
6. Empty `target_repos` falls back to full diff gracefully

## Acceptance Criteria
- `generate-review-input.sh WRK-NNN` produces a valid input file
- Output includes: mission, ACs, diff (scoped), test snapshot, focus prompts
- Diff truncation works correctly for large diffs (>300 lines)
- `--phase N` flag included in output filename
- Integrates with `cross-review.sh` without modification
- Cross-review (Codex) passes
