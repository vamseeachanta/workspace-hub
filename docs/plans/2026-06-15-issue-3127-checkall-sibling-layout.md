# Plan for #3127: check-all gate must resolve tier-1 repos in sibling OR nested layout

> **Status:** plan-review (awaiting user approval — NOT self-approved)
> **Complexity:** T2
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3127
> **Client:** N/A
> **Project:** N/A

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/quality/check-all.sh:8` — `REPO_ROOT="${QUALITY_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"`. `REPO_ROOT` is workspace-hub and is used both for the script's own internal paths (config, sibling helper scripts, baselines) **and** for tier-1 repo paths — so it cannot simply be repointed.
- `scripts/quality/check-all.sh:118` — `_rp="${REPO_ROOT}/${REPO_MAP[$_r]}"` (mypy-version probe loop). Construction site #1.
- `scripts/quality/check-all.sh:429` — `repo_path="${REPO_ROOT}/${REPO_MAP[$repo_name]}"` (main loop); line 432 emits `ERROR: directory not found: ${repo_path}` and bumps `FAIL_COUNT`. Construction site #2 — the gate-blocking one.
- `scripts/lib/tier1-repos.sh` — supplies the repo **slugs** (`TIER1_PYTHON_REPOS`); reads `config/tier1-python-repos.txt`, overridable via `TIER1_REPOS_FILE` (used by tests). Does not resolve paths.
- `.git/hooks/pre-push` — runs `check-all.sh --repo <repo>` per tier-1 repo on new-branch/tier-1 pushes; any FAIL blocks the push. `GIT_PRE_PUSH_SKIP=1` is the audited soft-bypass.

### Standards
| Standard | Status | Source |
|---|---|---|
| Workspace issue planning gate | applicable | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Enforcement gradient (script-level gate) | applicable | `.claude/rules/patterns.md` |
| Path handling (no hardcoded abs paths) | applicable | `.claude/rules/coding-style.md` |

### Existing tests
- `tests/quality/test_check_all.sh`, `tests/quality/test_check_all_static.sh` — check-all behavior/static tests.
- `tests/quality/test_tier1_excludes_relocated_repo.bats`, `test_tier1_repos_ssot.bats` — tier-1 list tests (bats harness available).
- `tests/hooks/test_pre_push.py` — pre-push hook test.

### Reproduce (Step 1.5 — confirmed)
On `ace-linux-1` the tier-1 repos are siblings at `/mnt/local-analysis/<repo>`, not nested under `workspace-hub`. A push of a clean branch produced:
```
[assetutilities] ERROR: directory not found: /mnt/local-analysis/workspace-hub/assetutilities
[pre-push] FAIL: check-all for assetutilities   (also digitalmodel, worldenergydata)
error: failed to push some refs
```
`repo_path` resolved to the **nested** path (`${REPO_ROOT}/assetutilities`) which does not exist; the sibling path (`/mnt/local-analysis/assetutilities`) does. PR #3122 (a clean 5-file cron fix) could only land via `GIT_PRE_PUSH_SKIP`.

### Gaps identified
- No path resolver that tolerates both nested and sibling layouts.
- No test asserting check-all finds repos under either layout.

---

## Deliverable

`check-all.sh` resolves each tier-1 repo by trying the nested path (`${REPO_ROOT}/<repo>`) first, then the sibling path (`$(dirname "${REPO_ROOT}")/<repo>`), using whichever exists; it only emits `directory not found` (and FAILs) when the repo exists at **neither**. `REPO_ROOT` continues to govern workspace-hub-internal paths unchanged. Behavior on nested-layout machines is identical (nested tried first).

---

## Pseudocode

```
# new helper, defined once near REPO_ROOT setup
resolve_repo_path(slug):
    nested="${REPO_ROOT}/${slug}"
    sibling="$(dirname "${REPO_ROOT}")/${slug}"
    if [[ -d "$nested"  ]]: print "$nested";  return 0
    if [[ -d "$sibling" ]]: print "$sibling"; return 0
    return 1            # neither — genuine absence

# site #1 (line ~118)
_rp="$(resolve_repo_path "${REPO_MAP[$_r]}")" || continue

# site #2 (line ~429)
if ! repo_path="$(resolve_repo_path "${REPO_MAP[$repo_name]}")"; then
    echo "${label} ERROR: directory not found (nested or sibling): ${REPO_MAP[$repo_name]}" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1)); continue
fi
```
- Nested-first preserves current behavior where repos ARE nested.
- `dirname "${REPO_ROOT}"` is derived, not hardcoded (satisfies `coding-style.md`).
- An optional `TIER1_REPOS_BASE` env override may be added for explicit control, defaulting to the nested-then-sibling probe; decide during review (keep minimal unless a reviewer wants it).

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/quality/check-all.sh` | Add `resolve_repo_path` helper; use at both construction sites (118, 429); update the not-found message. |
| Create | `tests/quality/test_check_all_repo_layout.bats` (or `.sh` to match harness) | Assert resolution under nested-only, sibling-only, and neither (FAIL) layouts. |
| Modify | `tests/quality/test_check_all.sh` | Only if needed to keep existing assertions valid under the resolver. |

---

## TDD Test List
| Test | Verifies | Input | Output |
|---|---|---|---|
| `test_resolves_nested_repo` | nested layout still works (no regression) | temp REPO_ROOT with `REPO_ROOT/<slug>` present | resolver prints nested path; check-all runs it |
| `test_resolves_sibling_repo` | sibling layout now works | temp REPO_ROOT with `$(dirname REPO_ROOT)/<slug>` present, nested absent | resolver prints sibling path; no "directory not found" |
| `test_prefers_nested_when_both` | deterministic precedence | both present | resolver prints the nested path |
| `test_fails_when_neither` | genuine absence still FAILs closed | neither present | resolver returns 1; check-all emits not-found + bumps FAIL_COUNT |
| `test_pre_push_passes_sibling_layout` (if feasible in `tests/hooks`) | end-to-end: gate no longer blocks a clean push under sibling layout | sibling layout + clean diff | check-all per-repo returns 0 |

---

## Acceptance Criteria
- [ ] New layout tests pass under nested-only, sibling-only, both, and neither.
- [ ] `tests/quality/test_check_all.sh` + `test_check_all_static.sh` still pass (no regression).
- [ ] On a sibling-layout machine, `bash scripts/quality/check-all.sh --repo assetutilities` no longer reports "directory not found" solely due to layout.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` passes; no hardcoded absolute paths (`coding-style.md`).
- [ ] Code/artifact adversarial review completes with no MAJOR blockers.

---

## Risks and Open Questions
- **Risk:** `check-all.sh` is the load-bearing pre-push gate; a resolver bug could either block valid pushes or (worse) let a genuinely-absent repo pass. Mitigation: fail-closed when neither path exists; nested-first precedence preserves current machines exactly.
- **Risk:** Other scripts may also assume nested layout (e.g., `run-tests`, api-audit). Scope this PR to `check-all.sh`; file follow-ups if review finds siblings of this bug.
- **Open:** Add explicit `TIER1_REPOS_BASE` override now, or keep the implicit nested-then-sibling probe only? Recommend probe-only for minimalism; decide at review.

---

## Complexity: T2
Small shared shell resolver, two call-site edits, focused layout tests, preservation of an existing gate's behavior on current machines.
