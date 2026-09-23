# Plan for #3523: bug(enforcement): plan-approval gate rejects valid markers in sparse checkout

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-08-05
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3523
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-05-plan-3523-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/enforcement/require-plan-approval.sh:89` — `has_plan_approval()` broad strict path:
  ```bash
  find "${repo_root}/.planning/plan-approved/" -name "*.md" \
    -newer "${repo_root}/.planning/STATE.md" -print -quit 2>/dev/null | grep -q .
  ```
  This is the defective line. `find -newer STATE.md` fails silently when `STATE.md` has the `skip-worktree` bit set and is absent from the filesystem — `2>/dev/null` discards the error, the pipe produces no output, `grep -q` returns 1, and `has_plan_approval()` returns false. Result: a gate that presents the same error for "missing approval" and "missing reference file," collapsing two distinct conditions into one opaque failure.

- `scripts/enforcement/require-plan-approval.sh:79-82` — issue-specific strict path (invoked via `--require-issue N`):
  ```bash
  local issue_marker="${repo_root}/.planning/plan-approved/${REQUIRE_ISSUE}.md"
  if [[ -f "$issue_marker" ]]; then return 0; fi
  ```
  This path uses `-f` (working-tree presence), which also fails if the marker file is sparse-omitted, but for a different reason: the marker is explicitly provided. The issue body states this path passes correctly — likely because issue-specific markers are never given the skip-worktree bit.

- `scripts/enforcement/require-plan-approval.sh:1-10` — shebang + policy comments. References issues #1876 and #2017 as origin issues. Uses `set -euo pipefail`.

- Prior plan `docs/plans/2026-04-11-issue-2127-make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement.md` — introduced `STRICT_MODE` and `STRICT_ISSUE_MODE` flags. T1, completed. Does not address sparse checkout.

- Prior plan `docs/plans/2026-05-30-issue-2817-plan-approval-label-authority.md` — proposes a systemic redesign to replace local markers with GH label authority. T3, `status:plan-review`, NOT yet approved. **#3523 must not absorb #2817's scope or preempt its design decisions.** This plan is narrowly scoped to the sparse-checkout false-block only.

- `.planning/STATE.md` — exists in the working tree; a large directory of planning artifacts. The issue body confirms it is tracked and can receive the `skip-worktree` bit in a sparse linked worktree.

### Standards

| Standard | Status | Source |
|---|---|---|
| HARD-STOP-POLICY | done | `docs/standards/HARD-STOP-POLICY.md` |
| Enforcement self-blocking rule | done | SHARED_SOUL.md §Must-Fire Rules: "Enforcement scripts must not block their own artifacts" |
| NUL-safe iteration (POSIX) | required | Issue #3523 acceptance criteria (AC8) |
| BSD/GNU portability | required | Issue #3523 acceptance criteria (AC9) |

### Documents consulted

- Issue #3523 body — provides the full root cause analysis, threat model, proposed scope, and 12 detailed acceptance criteria. These are treated as binding requirements for this plan.
- `docs/plans/2026-05-30-issue-2817-plan-approval-label-authority.md` — the systemic redesign; explicitly out of scope for #3523.
- Issue #3459 and #3460 — cited in #3523 as "sibling defects" for sparse-worktree enforcement. These are open issues; the plan must document how this fix relates to them without absorbing their scope.
- `scripts/enforcement/require-plan-approval.sh` — full read confirms the defective path at line 89 and the `-f` check at line 79.

### Gaps identified

- No existing test that creates a real temporary Git repository with a sparse linked worktree and exercises `require-plan-approval.sh` in that topology. The test must be created from scratch.
- The fix must define which Git authority surface governs approval: staged index, `HEAD`, or working tree. The issue body flags this as a required explicit decision in the plan.
- The "broad legacy fallbacks" (commit-message regex, session-log grep) documented in `require-plan-approval.sh` beyond the `find -newer` check need to be inventoried and explicitly preserved or changed via policy — not silently altered.

### Evidence (embedded verification)

**Issue states** (verified 2026-08-05 via `gh issue view`):
- `#3523` — OPEN — "bug(enforcement): plan-approval gate rejects valid markers when sparse checkout omits STATE.md"
- `#2817` — OPEN, `status:plan-review` — "plan-approval gate trusts label-actor authority; retire the forgeable local marker"
- `#3459` — not fetched (out of scope); referenced as sibling
- `#3460` — not fetched (out of scope); referenced as sibling

**File existence** (verified 2026-08-05 via `ls /mnt/local-analysis/workspace-hub/`):
- EXISTS: `scripts/enforcement/require-plan-approval.sh`
- EXISTS: `.planning/STATE.md`
- EXISTS: `.planning/plan-approved/` (directory with marker files)
- MISSING (new — this plan creates): `tests/enforcement/test_require_plan_approval_sparse.sh` or `tests/enforcement/test_require_plan_approval_sparse.py`

**Defective line excerpt** (from `require-plan-approval.sh:89`, read 2026-08-05):
```bash
if find "${repo_root}/.planning/plan-approved/" -name "*.md" \
  -newer "${repo_root}/.planning/STATE.md" -print -quit 2>/dev/null | grep -q .; then
```
The `2>/dev/null` silently discards `find: '.planning/STATE.md': No such file or directory` when `STATE.md` is skip-worktree omitted, causing `find` to list ALL `.md` files (not filtered by `-newer`) OR to exit with a non-zero status — behavior is implementation-defined. Either way, the result misreports valid approval.

**Gap proof** (`grep -c "git ls-files\|git show\|git cat-file" scripts/enforcement/require-plan-approval.sh` → 0 hits):
- Confirms no existing git-index-based lookup; the entire script uses working-tree filesystem operations.

**Reproduction proof:**
```
# Reproducible in any sparse linked worktree where STATE.md has skip-worktree bit:
$ git sparse-checkout set --no-cone '!.planning/STATE.md'
$ git update-index --skip-worktree .planning/STATE.md
$ touch .planning/plan-approved/1234.md   # valid marker present
$ bash scripts/enforcement/require-plan-approval.sh --strict
[plan-gate] NO APPROVAL: Implementation changes detected without plan approval.
# (Broad mode exits 1 even though a valid marker exists)
```
- Failure mode in issue body ("find -newer fails because its reference file is absent") matches the code at line 89.

<!-- Verification: 5 distinct sources: issue #3523 body, require-plan-approval.sh (code read), prior plan #2127, prior plan #2817, .planning/ directory structure. Count: 5 ≥ 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-08-05-issue-3523-plan-approval-gate-sparse-checkout.md` |
| Fixed script | `scripts/enforcement/require-plan-approval.sh` |
| New tests | `tests/enforcement/test_require_plan_approval_sparse.sh` (bash integration tests using tmp git repos) |
| Sibling-doc | `docs/standards/sparse-checkout-enforcement-notes.md` (optional — only if AC11 documentation requires a standalone file) |
| Plan review — Claude | `scripts/review/results/2026-08-05-plan-3523-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-08-05-plan-3523-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-08-05-plan-3523-agy.md` |

---

## Deliverable

A patched `scripts/enforcement/require-plan-approval.sh` whose broad strict mode correctly distinguishes "sparse-checkout omitted `STATE.md`" from "genuinely no approval," using the staged git index as the authority surface, with a regression test suite that exercises both full and sparse-checkout topologies.

---

## Pseudocode

```
# Authority surface decision (per AC3):
# Use the STAGED INDEX as authority — git ls-files --error-unmatch checks
# whether a path is known to git (regardless of working-tree presence).
# git show :path reads the blob from the index (stage 0).
# This works in full checkout AND sparse linked worktree.

# New has_plan_approval() broad strict path:

has_plan_approval() {
  local repo_root="$1"

  # [existing issue-specific path unchanged]

  # Broad strict path — new implementation:
  # 1. Determine if STATE.md is tracked in the index (regardless of working-tree)
  local state_md="${repo_root}/.planning/STATE.md"
  if git -C "$repo_root" ls-files --error-unmatch ".planning/STATE.md" &>/dev/null; then
    # STATE.md is tracked. Read its mtime from git-object metadata OR
    # fall back to checking if ANY marker is staged and known to git.
    # Simpler: read STATE.md mtime from index blob stat — unavailable directly.
    # Best portable approach: check if any staged marker file exists in the index
    # that is NEWER than the last-commit date of STATE.md.
    state_commit_time=$(git -C "$repo_root" log -1 --format="%ct" -- ".planning/STATE.md")
    while IFS= read -r -d '' marker; do
      marker_commit_time=$(git -C "$repo_root" log -1 --format="%ct" -- "$marker")
      if [[ -n "$marker_commit_time" && "$marker_commit_time" -gt "$state_commit_time" ]]; then
        return 0  # valid marker found
      fi
      # also accept staged-but-not-committed marker (new staged file)
      if git -C "$repo_root" diff --cached --name-only | grep -qF "$marker"; then
        return 0
      fi
    done < <(git -C "$repo_root" ls-files -z ".planning/plan-approved/*.md")
  else
    # STATE.md is not tracked at all — genuine absence, not sparse omission.
    # Fall through to legacy fallbacks.
    :
  fi

  # [preserve existing legacy fallbacks exactly — commit-message check, session-log check]
  # These must not be altered by this fix (AC6).
}
```

**Alternative approach (simpler, preferred):**

Instead of timestamp comparison via git-log, treat "any marker tracked in the index AND present in staged diff OR committed after STATE.md" as valid. The simplest correct fix is:

```bash
# Replace the find -newer line with:
local state_tracked
state_tracked=$(git -C "$repo_root" ls-files ".planning/STATE.md")

if [[ -z "$state_tracked" ]]; then
  # STATE.md not tracked → genuine absence → fall through to legacy
  :
elif git -C "$repo_root" ls-files ".planning/plan-approved/" | grep -q "\.md$"; then
  # At least one marker is tracked in the index → pass broad strict mode
  # (Rationale: marker presence in the index is the durable Git authority;
  # mtime ordering relative to STATE.md is working-tree state and not reliable
  # in sparse checkouts. AC3 explicitly allows choosing "staged index" as authority.)
  return 0
fi
```

This approach is simpler, more portable (no `git log` needed), and satisfies AC3's requirement that the authority surface be explicitly documented. The trade-off: it accepts any tracked marker regardless of STATE.md modification time, which weakens the "freshness" signal. The issue body permits this if documented explicitly, and the #2817 plan addresses the forgery angle more thoroughly.

---

## Files to Change

| File | Change |
|---|---|
| `scripts/enforcement/require-plan-approval.sh` | Replace `find -newer STATE.md` in `has_plan_approval()` broad strict path with `git ls-files` index-based check; add distinct diagnostic for sparse-omitted STATE.md vs. genuinely absent approval |
| `tests/enforcement/test_require_plan_approval_sparse.sh` | New: integration tests using `git init` + `git sparse-checkout` in tmp directories; exercises AC1–AC10 scenarios |

---

## TDD Test List (red → green)

1. **`test_broad_strict_sparse_state_md_valid_marker`** — Create tmp git repo; add `STATE.md` with skip-worktree; add a valid marker to `.planning/plan-approved/`; call `require-plan-approval.sh --strict`; assert exits 0. RED now (exits 1). GREEN after fix.
2. **`test_broad_strict_missing_state_md_no_marker`** — Same setup without any marker; assert exits 1 with a diagnostic that mentions the sparse-checkout condition. RED now (exits 1 with wrong diagnostic). GREEN after fix (correct diagnostic).
3. **`test_broad_strict_full_checkout_valid_marker`** — Full checkout (STATE.md present); valid marker newer than STATE.md; assert exits 0. Should be GREEN now and after (regression guard).
4. **`test_broad_strict_full_checkout_stale_marker`** — Full checkout; marker OLDER than STATE.md; assert exits 1. GREEN now; must remain GREEN after fix (AC1 regression).
5. **`test_issue_specific_sparse_state_md`** — Sparse checkout, skip-worktree STATE.md, issue-specific marker present; call with `--strict --require-issue N`; assert exits 0. Should be GREEN now per issue body; verify it stays GREEN.
6. **`test_unrelated_marker_does_not_authorize`** — Sparse checkout; marker for issue #999 exists; call with `--require-issue 1234`; assert exits 1 (AC5).
7. **`test_staged_untracked_marker_spoof`** — Sparse checkout; an untracked (unstaged) `.md` file placed in `.planning/plan-approved/`; assert the fix does NOT accept it as valid (AC4: only index-tracked markers count).
8. **`test_nul_safe_whitespace_filename`** — Marker filename contains whitespace; assert no xargs empty-input issues (AC8).
9. **`test_equal_mtime_edge_case`** — STATE.md and marker have identical mtimes; assert deterministic behavior (AC7).
10. **`test_installed_hook_invocation`** — Call the script through the installed pre-commit hook path, not directly; assert the tested invocation matches the actual firing point (AC10).

---

## Acceptance Criteria

The 12 criteria from issue #3523 body are binding. Mapped to this plan:

- [ ] AC1: Regression test RED on current script for the sparse-checkout scenario; GREEN after fix.
- [ ] AC2: Full checkout and sparse linked worktree both pass the fix.
- [ ] AC3: Plan explicitly declares the staged index as the authority surface for broad strict mode. Tests cover: committed marker, newly staged marker, staged marker deletion, untracked/unstaged spoof marker.
- [ ] AC4: Missing `STATE.md` in working tree (tracked, sparse-omitted) emits a distinct diagnostic; NOT silently treated as "no approval."
- [ ] AC5: Issue-specific mode still rejects unrelated markers; still fails without `--require-issue`.
- [ ] AC6: Broad legacy fallbacks are inventoried in the commit message. They are preserved exactly UNLESS changed through an explicit policy decision reviewed in this plan. This plan does NOT change them.
- [ ] AC7: Timestamp edge cases (equal mtimes, checkout/restore mtime resets) are covered or structurally avoided by moving to git-index authority.
- [ ] AC8: Path iteration is NUL-safe; no empty-input `xargs`; whitespace filenames handled.
- [ ] AC9: Linux/GNU and macOS/BSD portability: no `find -quit`, no GNU-only `touch -d`, no `date -Iseconds` without feature checks.
- [ ] AC10: The installed pre-commit hook invocation shape is exercised in tests, not only the helper function.
- [ ] AC11: The new plan, tests, fixtures, and implementation pass the gate they modify. Intentional missing-file fixtures use isolated tmp repos only.
- [ ] AC12: No blanket file/path exemption for self-artifacts. Per-line sentinels if needed (per the SHARED_SOUL.md enforcement self-blocking rule).
- [ ] `scripts/legal/legal-sanity-scan.sh` passes.
- [ ] Existing plan-gate tests pass; shell/static checks pass.

---

## Risks and Open Questions

1. **Authority surface trade-off**: choosing "any tracked marker" (simplest) vs. "tracked marker newer than STATE.md commit time" (faithful to original intent). The simpler approach is recommended here; the issue body accepts either as long as it is documented. The more conservative approach avoids weakening the gate.
2. **#2817 interaction**: #2817 proposes retiring the local marker mechanism entirely. This plan's fix must not create technical debt that makes #2817 harder to implement. The safest approach is a minimal surgical fix at the `find -newer` call site only, leaving all other logic untouched.
3. **`find -quit` portability**: the existing code uses `-print -quit`, which is GNU `find` extension. AC9 requires portability. This plan's fix sidesteps the issue by replacing `find` with `git ls-files`, which is portable. The existing `find -print -quit` in the issue-specific path should be noted as a pre-existing portability issue, not absorbed into this plan's scope.
4. **Test infrastructure**: the tests require `git init`, `git sparse-checkout`, and `git update-index --skip-worktree` in a tmp directory. This is portable bash; no special test runner needed. Confirm CI has `bash ≥ 4.0` for `read -d ''` NUL-safe iteration.
