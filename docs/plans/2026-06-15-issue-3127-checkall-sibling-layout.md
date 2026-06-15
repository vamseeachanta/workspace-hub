# Plan for #3127: pre-push gate must resolve tier-1 repos in sibling OR nested layout

> **Status:** plan-review (REVISED after r1+r2 adversarial review — NOT self-approved)
> **Complexity:** T3 (was T2 — review proved the fix spans the whole pre-push gate surface + Python ratchets)
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3127
> **Client:** N/A | **Project:** N/A
> **Review artifacts:** scripts/review/results/2026-06-15-plan-3127-gemini.md (MAJOR), -codex.md (UNAVAILABLE — CLAUDECODE stdin-hang), -disagreement.md; + 3 Claude adversarial subagents (correctness / test-coverage / scope), all NON-APPROVE.

---

## Why this was revised (r1 Claude inline + 3 subagents, r2 Gemini)

The original T2 "fix check-all.sh only" plan was **NON-APPROVE on three independent axes**. The decisive finding: **check-all.sh alone does not unblock pushes** — the pre-push hook runs several layout-dependent gates, and the coverage ratchet would still hard-fail. Fixing one script would land, the next clean push would still need `GIT_PRE_PUSH_SKIP`, and the issue's goal would be unmet. Scope is therefore expanded to the gate surface, with one shared resolver (shell + Python).

---

## Resource Intelligence Summary

### The pre-push gate surface (all layout-dependent; `.git/hooks/pre-push`)
| Gate | Site | Layout assumption | Failure mode on sibling layout |
|---|---|---|---|
| check-all.sh | `:118` (mypy-ver probe), `:429` (`repo_path="${REPO_ROOT}/${REPO_MAP[$repo_name]}"`, FAIL+msg at `:432-433`) | nested | hard FAIL "directory not found" |
| run-all-tests.sh | `:60` (`repo_dir="${REPO_ROOT}/${rel_dir}"`), `:131-132`,`:138` (coverage.json) | nested | per-repo `:62-65` returns **skip/exit 0 → silently runs 0 tests**; `--coverage` produces empty results |
| check_coverage_ratchet.py | `check_repos` `:88-93` (`actual=results.get(repo)` → None → `status:"missing"`) | nested (via run-all-tests) | **hard FAIL for all repos** (pre-push `:215`, unconditional) → push blocked |
| secrets-scan.sh | `:78` (`repo_path="${REPO_ROOT}/${repo_name}"`, return 1 at `:82-85`) | nested | hard FAIL if `gitleaks` installed (pre-push `:195-196`) |
| check_mypy_ratchet.py | `repo_path = repo_root / rel_path` | nested | hard FAIL (fail-closed on missing) when `--mypy-ratchet` used |

`scripts/lib/tier1-repos.sh` supplies repo **slugs** (SSoT, `TIER1_REPOS_FILE` test override); it is already `source`d by check-all.sh (`:14`), run-all-tests.sh, and is the right home for a shared resolver. `check-all.sh:5` = `set -uo pipefail` (no `-e`).

### Non-gate scripts with the same nested assumption (OUT of scope → follow-up issue)
`dep-health.sh:71`, `review/generate-review-input.sh:131`, `search/find-symbol.sh:46`, `learnings/cross-agent-bridge.sh:119+`, `operations/validate-file-placement.sh:31,33` (hardcoded slugs), `testing/run-cross-repo-integration.sh:105`, `test/config/digitalmodel.conf:5` (hardcoded abs path — also violates coding-style). These do not run in the push gate.

### Existing tests
`tests/quality/test_check_all.sh` + `test_check_all_static.sh` (`.sh`, bespoke `assert_contains`, mock-`uv` on PATH, `QUALITY_REPO_ROOT=$FIXTURE_ROOT=$(mktemp -d)`); `tests/quality/test_tier1_*.bats` (list SSoT); `tests/hooks/test_pre_push.py` (hook with injected fake check-all/run-tests).

### Reproduce (Step 1.5 — confirmed)
Clean 5-file push (PR #3122) on `ace-linux-1` (repos at `/mnt/local-analysis/<repo>`, not nested) failed: `check-all` "directory not found" FAIL for assetutilities/digitalmodel/worldenergydata; the coverage ratchet also reported "no coverage result". Only `GIT_PRE_PUSH_SKIP=1` landed it.

---

## Design decisions (resolved — no deferral)

1. **`TIER1_REPOS_BASE` = YES.** Add an explicit env override, resolved ONCE in `tier1-repos.sh`. Default = probe order: `$TIER1_REPOS_BASE` if set, else nested (`$REPO_ROOT/<slug>`), else sibling (`$(realpath "$REPO_ROOT")/../<slug>`). This (a) decouples "where my helper scripts live" (`REPO_ROOT`) from "where tier-1 repos live", fixing the test-hermeticity conflation, and (b) gives overlay/symlink machines a deterministic escape.
2. **Selection requires a real repo marker**, not bare `-d`: a candidate counts only if it contains `.git` OR `pyproject.toml`. Prevents empty-dir / mountpoint false-positives.
3. **Both-present → loud stderr WARNING** naming both candidate paths; nested still chosen for back-compat, but never silently (closes the false-negative). 
4. **Fail-closed when no candidate has a marker** (genuine absence) — preserves gate integrity. Distinguish from run-all-tests' current silent skip (fix that too).
5. **One shared resolver, two languages:** `resolve_tier1_repo_path` (shell, in `tier1-repos.sh`) + `resolve_tier1_repo_path()` (Python, in a small `scripts/lib/tier1_repos.py` or extend an existing module) so the ratchets share identical semantics.

---

## Pseudocode (shell resolver — Python mirrors it)
```
resolve_tier1_repo_path(slug):
    local base nested sibling             # MUST be local (Gemini #5)
    root="$(realpath "$REPO_ROOT")"       # symlink/overlay safe (MINOR-1)
    candidates=()
    [[ -n "${TIER1_REPOS_BASE:-}" ]] && candidates+=("$TIER1_REPOS_BASE/$slug")
    candidates+=("$root/$slug" "$(dirname "$root")/$slug")
    found=()
    for c in candidates: if [[ -d "$c/.git" || -f "$c/pyproject.toml" ]]: found+=("$c")
    if (( ${#found[@]} == 0 )): return 1                      # fail-closed
    if (( ${#found[@]} > 1 )): echo "WARN: $slug resolves at multiple layouts: ${found[*]}; using ${found[0]}" >&2
    printf '%s' "${found[0]}"; return 0
```
- check-all.sh `:118` keeps its `[[ -f pyproject.toml ]] … break` block, fed the resolved path (MAJOR-1).
- check-all.sh `:429`: `if ! repo_path="$(resolve_tier1_repo_path "$slug")"; then echo "${label} ERROR: tier-1 repo not found (tried nested/sibling/TIER1_REPOS_BASE): $slug" >&2; FAIL_COUNT++; continue; fi` (keeps diagnosability — MINOR-3).
- run-all-tests.sh `:60`/`:131`: same resolver; **a repo resolvable-but-absent-everywhere must FAIL, not skip** (fixes the silent-skip latent bug).

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/lib/tier1-repos.sh` | add shell `resolve_tier1_repo_path` (the SSoT resolver) |
| Create | `scripts/lib/tier1_repos.py` | Python mirror for the ratchets |
| Modify | `scripts/quality/check-all.sh` | use resolver at `:118`,`:429`; preserve break; keep path-rich error |
| Modify | `scripts/testing/run-all-tests.sh` | resolver at `:60`,`:131`; fail (not skip) on absent-everywhere |
| Modify | `scripts/testing/check_coverage_ratchet.py` | resolve repo path via Python mirror |
| Modify | `scripts/quality/check_mypy_ratchet.py` | resolve repo path via Python mirror |
| Modify | `scripts/security/secrets-scan.sh` | resolver at `:78` |
| Create | `tests/quality/test_check_all_repo_layout.sh` | hermetic two-level layout tests (`.sh`, mock-uv) |
| Create | `tests/testing/test_coverage_ratchet_layout.py` | coverage gate passes under sibling layout |
| Modify | `tests/quality/test_check_all.sh` | assert new not-found message + FAIL behavior |
| Update | `docs/plans/README.md` | index |

---

## TDD Test List (all hermetic — two-level fixture: `MB=$(mktemp -d); REPO_ROOT=$MB/hub`, siblings at `$MB/<slug>`, so `dirname` stays in-sandbox; inherit the mock-`uv` PATH; stub `scripts/lib` or set `TIER1_REPOS_FILE`)
| Test | Verifies |
|---|---|
| resolves_nested / resolves_sibling / resolves_via_TIER1_REPOS_BASE | each layout resolves |
| prefers_nested_when_both + warns | precedence + the multi-layout WARNING fires |
| fails_when_neither (no marker) | fail-closed; exact error message; FAIL/exit-1 observable |
| ignores_marker_less_dir | empty dir is NOT accepted (marker required) |
| symlinked_repo_dir | symlinked candidate resolves |
| mixed_layout (repo A sibling, B nested) | per-repo independence |
| site1_mypy_probe_sibling | mypy version header populated under sibling (not `(unavailable)`) |
| coverage_ratchet_passes_sibling | the ratchet gate (Python) passes under sibling layout — the gate that actually blocks |
| run_all_tests_fails_on_absent_everywhere | silent-skip latent bug fixed |

E2E pre-push: per the Gemini/subagent disagreement, the hook test injects a FAKE check-all, so an in-hook test can't exercise the resolver. Resolution: add a **focused integration test** that runs the REAL check-all + REAL coverage ratchet against a sibling fixture (not via the hook's mock boundary). Do NOT modify the hook-mock contract.

---

## Acceptance Criteria
- [ ] All layout tests pass (nested / sibling / TIER1_REPOS_BASE / both+warn / neither-fail / empty / symlink / mixed).
- [ ] **End-to-end: the full pre-push gate surface (check-all + run-all-tests + coverage ratchet + secrets-scan + mypy-ratchet) passes under a sibling fixture** — i.e. a clean push would NOT need `GIT_PRE_PUSH_SKIP`. (This is the issue's actual goal.)
- [ ] Nested-layout behavior byte-identical (nested tried first).
- [ ] Existing `test_check_all*.sh` + `test_pre_push.py` still pass.
- [ ] `legal-sanity-scan.sh --diff-only` passes; no hardcoded abs paths; resolver uses `local` + `realpath`.
- [ ] Follow-up issue filed for the out-of-scope non-gate scripts.
- [ ] T3 cross-provider review (Claude+Codex+Gemini) clean; Codex run from a plain terminal (CLAUDECODE unset) so it's not UNAVAILABLE.

---

## Risks and Open Questions
- **Risk:** load-bearing gate; a resolver bug could block valid pushes (fail-closed bias mitigates) or pass a wrong repo (marker-check + warn mitigates).
- **Risk:** shell/Python resolver drift → shared tests assert identical semantics on the same fixtures.
- **Risk:** larger blast radius (6 files). Mitigate: one resolver, mechanical call-site swaps, per-gate tests.
- **Open:** none blocking — `TIER1_REPOS_BASE` decided (yes).

---

## Adversarial Review Summary
| Provider | Verdict | Headline |
|---|---|---|
| Claude r1 (correctness) | NON-APPROVE | nested-precedence false-negative; site-1 break; `-d` empty-dir; symlink REPO_ROOT; ratchet `--repo-root` |
| Claude r1 (test-coverage) | NON-APPROVE | `/tmp` non-hermetic; REPO_ROOT conflation; decide TIER1_REPOS_BASE; site-1 & coverage paths untested |
| Claude r1 (scope) | NON-APPROVE | check-all alone won't unblock; run-all-tests + coverage-ratchet + secrets-scan share the bug; centralize resolver |
| Gemini r2 | MAJOR | `/tmp` race; mypy/coverage ratchets fail-closed nested; mock-uv needed; `local`; decide TIER1_REPOS_BASE |
| Codex r2 | UNAVAILABLE | CLAUDECODE stdin-hang — re-run from plain terminal |

All findings folded in: scope expanded to the gate surface; resolver centralized (shell+Python); TIER1_REPOS_BASE decided; marker-check + warn-on-both + realpath + local; hermetic two-level tests + coverage-path + e2e-integration; T2→T3.

## Complexity: T3
Shared resolver in two languages across five gate scripts + the pre-push surface; systemic; requires 3-provider review.
