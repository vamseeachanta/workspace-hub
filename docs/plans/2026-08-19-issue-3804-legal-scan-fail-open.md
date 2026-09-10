# Plan for #3804: legal-sanity-scan.sh --repo=<name> scans NOTHING and exits 0 (fail-open legal gate)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-08-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3804
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-19-plan-3804-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/legal/legal-sanity-scan.sh:168` — first definition of `resolve_repo_path()` uses `printf '%s\n' "$c"` (stdout) and `return 2` on not-found. Correct calling convention.
- Found: `scripts/legal/legal-sanity-scan.sh:324` — **second definition** of `resolve_repo_path()` sets `RESOLVED_REPO_PATH` global, returns `1` on not-found, and prints **nothing to stdout**. This definition wins (bash: last write wins). Callers capture stdout → get empty string → scan empty path → PASS.
- Found: `scripts/legal/legal-sanity-scan.sh:496` — caller: `repo_path="$(resolve_repo_path "$TARGET_REPO")" || exit 2` — stdout-capture form. Gets empty string from second definition; `|| exit 2` does not trigger because function returns 0 (path found via global). `--repo=` passes with empty path.
- Found: `scripts/legal/legal-sanity-scan.sh:511` — same stdout-capture pattern for `--all` submodule loop.
- Found: `.github/workflows/legal-rule-authority-gate.yml:34` — `bash scripts/legal/legal-sanity-scan.sh --repo=workspace-hub` — the CI caller that is silently scanning nothing and reporting PASS.
- Found: `tests/legal/test_repo_resolution.py` — pytest wrapper driving `tests/legal/test_repo_resolution.sh` (git-bash-style tests).
- Found: `tests/legal/test_legal_scan_resolution.py` — pytest wrapper for a wider resolution test set.
- Found: `tests/legal/` — full bash test suite: `test_repo_resolution.sh`, `test_nested_wins.sh`, `test_sibling_fallback.sh`, `test_env_override_wins.sh`, `test_not_found_exit2.sh`, `test_all_env_roots.sh`, `test_all_empty_enumeration_exit2.sh`, `test_walk_up.sh`.
- Found: `scripts/cron/commit-learning-artifacts.sh:10` — calls legal-sanity-scan (comment confirms `--diff-only` path); this is the root-scan form, not affected by the defect.
- Found: `scripts/readiness/nightly-readiness.sh:637` — greps for `legal-sanity-scan` in pre-commit config; does not invoke `--repo=`.

### Standards
| Standard | Status | Source |
|---|---|---|
| N/A — enforcement script, not engineering calculation | N/A | N/A |

### LLM Wiki pages consulted
- No relevant wiki pages for a bash script defect fix.

### Documents consulted
- Issue [#3803](https://github.com/vamseeachanta/workspace-hub/issues/3803) — OPEN — `fix(legal): count each match once — the root scan parsed one deny list twice`. Found while fixing this unrelated double-count bug; issue body says PR #3803 deliberately did NOT touch the duplicate-definition defect.
- Issue [#3800](https://github.com/vamseeachanta/workspace-hub/issues/3800) — Prior legal gate work in the same sprint; fix scope was deny-list parsing, not resolution.
- PR [#3799](https://github.com/vamseeachanta/workspace-hub/issues/3799) — MERGED — `fix(legal): scope the client-name scan out of the public field-development corpus`. Same file, different section. Confirms active work stream around this script in W32.
- `docs/plans/` — searched for "3804", "legal-scan", "legal-sanity" — no prior plan found for this issue.

### Gaps identified
- No existing guard to prevent `resolve_repo_path()` from being re-duplicated in the future. A test that catches this (defined-twice check) must be added.
- The second definition's `RESOLVED_REPO_PATH` global and `RESOLVE_CANDIDATES` array are referenced nowhere else in the file per grep review — they are safe to remove.
- Return code on failure is `1` in the second definition vs `2` in the first. Callers use `|| exit 2`; a function returning `1` still triggers `|| exit 2` (any non-zero), so callers work either way. However, the issue body and the `--all` path convention both specify `exit 2` for "not found" vs `exit 1` for other errors. The surviving definition must use `return 2`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-08-19 via `gh issue view`):
- `#3804` — OPEN — legal-sanity-scan.sh --repo=<name> scans NOTHING and exits 0 (fail-open legal gate)
- `#3803` — OPEN — fix(legal): count each match once — the root scan parsed one deny list twice
- `#3799` — MERGED — fix(legal): scope the client-name scan out of the public field-development corpus

**File existence** (`ls` verified 2026-08-19):
- EXISTS: `scripts/legal/legal-sanity-scan.sh`
- EXISTS: `.github/workflows/legal-rule-authority-gate.yml`
- EXISTS: `tests/legal/test_repo_resolution.py`
- EXISTS: `tests/legal/test_legal_scan_resolution.py`
- EXISTS: `tests/legal/test_repo_resolution.sh`
- MISSING (this plan creates): no new files; this is a deletion + single-function fix

**Line excerpts** (`grep -n` verified 2026-08-19):
```
scripts/legal/legal-sanity-scan.sh:168:resolve_repo_path() {
scripts/legal/legal-sanity-scan.sh:324:resolve_repo_path() {
scripts/legal/legal-sanity-scan.sh:496:  repo_path="$(resolve_repo_path "$TARGET_REPO")" || exit 2
scripts/legal/legal-sanity-scan.sh:511:      sub_path="$(resolve_repo_path "$sub")" || exit 2
.github/workflows/legal-rule-authority-gate.yml:34:        run: bash scripts/legal/legal-sanity-scan.sh --repo=workspace-hub
```

**Gap proofs** (`grep -c` verified 2026-08-19):
- `grep -c "^resolve_repo_path()" scripts/legal/legal-sanity-scan.sh` → `2` → confirms duplicate definition.
- `grep -n "RESOLVED_REPO_PATH" scripts/legal/legal-sanity-scan.sh` → only inside the second definition (lines ~324-360) → safe to remove without breaking callers.

**Reproduction proofs:**
```
$ grep -n "^resolve_repo_path()" scripts/legal/legal-sanity-scan.sh
168:resolve_repo_path() {
324:resolve_repo_path() {
```
- Defect confirmed present in `origin/main` as of 2026-08-19.
- Issue body reproduction confirms `Scanning: submod ()` with empty path and `rc=0` PASS on a planted marker.
- 7 pre-existing failures in `tests/legal/test_repo_resolution.py` and `tests/legal/test_legal_scan_resolution.py` per issue body — these are live specifications of the intended behaviour that the second definition overrides.

N/A — reproduction is a bash defect (wrong function wins); no `uv run pytest` step needed to reproduce, but the failing tests are cited above as the specification contract.

<!-- Verification: distinct sources consulted: (1) scripts/legal/legal-sanity-scan.sh at lines 168+324+496+511, (2) .github/workflows/legal-rule-authority-gate.yml, (3) tests/legal/ test suite, (4) issue #3803, (5) PR #3799. Count: 5 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-08-19-issue-3804-legal-scan-fail-open.md |
| Primary fix | `scripts/legal/legal-sanity-scan.sh` |
| Regression test (new) | `tests/legal/test_no_duplicate_resolve_definition.sh` |
| Plan review — Claude | scripts/review/results/2026-08-19-plan-3804-claude.md |
| Plan review — Codex | scripts/review/results/2026-08-19-plan-3804-codex.md |
| Plan review — Agy | scripts/review/results/2026-08-19-plan-3804-agy.md |

---

## Deliverable

`scripts/legal/legal-sanity-scan.sh` will have exactly one `resolve_repo_path()` definition that outputs to stdout, returns 2 on not-found, and is guarded by a test that fails if the function is defined more than once — ensuring the fail-open regression cannot return silently.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/legal/legal-sanity-scan.sh` | Delete second definition (lines ~324–~370); verify first definition is the sole remaining one |
| Create | `tests/legal/test_no_duplicate_resolve_definition.sh` | Guard against re-duplication: test fails if `grep -c "^resolve_repo_path()"` is not exactly 1 |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_exactly_one_resolve_definition` | `grep -c "^resolve_repo_path()"` returns 1 | `scripts/legal/legal-sanity-scan.sh` | exit 0 (count == 1) |
| `test_repo_resolution_contract` (pre-existing, currently failing) | Planted-marker repo found via `--repo=` | fixture submodule with `ZZLEAKMARKERZZ` | exit 2 (marker found, FAIL verdict) |
| `test_not_found_exit2` (pre-existing bash test) | Unresolvable name exits 2 | non-existent repo name | exit 2 |
| `test_nested_wins` (pre-existing bash test) | Nested checkout resolves correctly | fixture workspace | exit 0 with correct path |
| `test_env_override_wins` (pre-existing bash test) | `LEGAL_SCAN_REPO_ROOTS` overrides walk-up | env set to fixture root | exit 0 with env-specified path |
| `test_sibling_fallback` (pre-existing bash test) | Sibling path used when nested not found | fixture with sibling layout | exit 0 with correct sibling path |

All "pre-existing, currently failing" tests must turn green after the fix. The new `test_exactly_one_resolve_definition` test must fail before the fix and pass after.

---

## Acceptance Criteria

- [ ] `grep -c "^resolve_repo_path()" scripts/legal/legal-sanity-scan.sh` returns `1`
- [ ] All pre-existing failures in `tests/legal/test_repo_resolution.py` and `tests/legal/test_legal_scan_resolution.py` pass
- [ ] New test `tests/legal/test_no_duplicate_resolve_definition.sh` passes
- [ ] `bash scripts/legal/legal-sanity-scan.sh --repo=workspace-hub` prints a non-empty path in the `Scanning: workspace-hub (PATH)` line
- [ ] A fixture test where a planted marker (`ZZLEAKMARKERZZ`) exists in the named repo causes the scan to exit non-zero (not PASS)
- [ ] CI workflow `legal-rule-authority-gate.yml` passes on main
- [ ] The surviving definition uses `return 2` (not `return 1`) on not-found, matching the `--all` path's convention and consistent with `|| exit 2` callers

---

## Risks and Open Questions

- **Risk:** The second definition at line 324 may have been added to support a feature (e.g., `LEGAL_SCAN_REPO_ROOTS` via `split_repo_roots()`) that the first definition does not handle identically. **Mitigation:** The first definition already uses `REGISTERED_ROOTS` which is populated from `LEGAL_SCAN_REPO_ROOTS` via a registration loop earlier in the script. The semantics are equivalent; the difference is only naming (`REGISTERED_ROOTS` array vs `split_repo_roots()` function). Verify with `test_env_override_wins` to confirm.
- **Risk:** PR #3803 (open) touches the same file. If it merges before this fix, there may be a merge conflict around the duplicate definition. **Mitigation:** Check PR #3803 diff before implementation; coordinate merge order or apply this fix as a follow-on commit on top of #3803.
- **Open:** Should `RESOLVED_REPO_PATH` global be preserved for callers outside this script? Current evidence shows no external callers (global is only set inside the second definition), but this should be verified with a repo-wide grep during implementation.

---

## Complexity: T1

Single bash script; delete one function definition (~40 lines), add one guard test (~8 lines). No new modules, no cross-repo changes. 7 pre-existing test failures provide the specification; fix turns them green.
