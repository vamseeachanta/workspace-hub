# Plan for #3871: fix(legal): reject empty resolved scan targets and reconcile duplicate resolver definitions

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-09-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3871
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-23-plan-3871-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/legal/legal-sanity-scan.sh:166–212` — first `resolve_repo_path()` definition; comment reads "Prints the resolved repo path on stdout; returns 2 on no-match"; function body uses `printf '%s\n' "$c"` to emit the path to stdout and returns 0.
- Found: `scripts/legal/legal-sanity-scan.sh:309–376` — second `resolve_repo_path()` definition; this definition overwrites the first in bash; sets `RESOLVED_REPO_PATH` as a side-effect variable; does **not** print to stdout; returns 0 on success, 1 on failure.
- Found: `scripts/legal/legal-sanity-scan.sh:496` — single-repo caller: `repo_path="$(resolve_repo_path "$TARGET_REPO")" || exit 2` followed by `echo "Scanning: $TARGET_REPO ($repo_path)"` at line 497. Command substitution captures stdout; the active (second) definition never prints to stdout, so `repo_path` is always empty.
- Found: `scripts/legal/legal-sanity-scan.sh:511` — `--all` submodule caller: `sub_path="$(resolve_repo_path "$sub")" || exit 2`; same empty-capture defect.
- Found: `scripts/legal/tests/` — contains `test_genesis_broker_bundle.py`, `test_rule_authority_*.py`, etc.; **no test file exists for `legal-sanity-scan.sh` resolver behavior**. All existing tests target Python modules.
- Gap: No regression test asserts that a named initialized sibling is actually visited (non-empty path passed to `scan_directory`).

### Standards
Not applicable — tooling fix, not an engineering calculation.

### LLM Wiki pages consulted
No relevant wiki pages found for legal scanner resolver behavior.

### Documents consulted

- Issue #3871 body — exact root cause: "Source contains two resolve_repo_path definitions. The later definition assigns RESOLVED_REPO_PATH without stdout, while the caller captures stdout with command substitution."
- `docs/plans/README.md` — no prior plan exists for `legal-sanity-scan.sh` resolver.
- Issue #3560 — related: provider sink isolation (different concern; addresses in-process review concurrency, not scanner path resolution); confirms fail-closed pattern is established practice in this codebase.
- `scripts/legal/genesis_broker.py:1` — "Small fail-closed retained-FD primitives"; confirms fail-closed idiom as an accepted engineering norm in `scripts/legal/`.

### Gaps identified

- No bash integration test infrastructure exists for `legal-sanity-scan.sh`; tests will be written as Python subprocess tests alongside existing `scripts/legal/tests/test_*.py` files.
- The `RESOLVE_CANDIDATES` sidecar variable declared by the second definition (line 326) is not currently exposed by any caller; the plan will leave it in place for debugging but will not add a dedicated test for it.

### Evidence (embedded verification)

**Issue status** (verified 2026-09-23 via `gh issue view 3871`):
- `#3871` — OPEN — fix(legal): reject empty resolved scan targets and reconcile duplicate resolver definitions

**File existence** (verified 2026-09-23 via `ls`):
- EXISTS: `scripts/legal/legal-sanity-scan.sh` (554 lines)
- EXISTS: `scripts/legal/tests/` (directory)
- MISSING (new — this plan creates): `scripts/legal/tests/test_legal_scan_resolver.py`

**Line excerpts** (`sed -n 166,170p scripts/legal/legal-sanity-scan.sh`):
```
166: # resolve_repo_path <name>
167: # Prints the resolved repo path on stdout; returns 2 on no-match.
168: resolve_repo_path() {
169:   local name="$1"
170:   local candidates=()
```

**Line excerpts** (`sed -n 309,327p scripts/legal/legal-sanity-scan.sh`):
```
309: # resolve_repo_path: resolve a repository name to a directory.
321: # On success: sets RESOLVED_REPO_PATH, returns 0.
322: # On failure: returns 1 with RESOLVE_CANDIDATES holding every path tried.
324: resolve_repo_path() {
325:   local name="$1"
326:   RESOLVED_REPO_PATH=""
327:   RESOLVE_CANDIDATES=()
```

**Line excerpts** (`sed -n 494,499p scripts/legal/legal-sanity-scan.sh`):
```
494: if [[ -n "$TARGET_REPO" ]]; then
495:   # Scan specific repo (shared candidate resolver)
496:   repo_path="$(resolve_repo_path "$TARGET_REPO")" || exit 2
497:   [[ "$JSON_OUTPUT" != "true" && "$QUIET" != "true" ]] && echo "Scanning: $TARGET_REPO ($repo_path)"
498:   scan_directory "$repo_path" "$TARGET_REPO" || true
```

**Reproduction proof** (verified 2026-09-23 against source at commit 4195e9a8563253c0fb785ecaad505447a0a5e490 per issue body):
- Failure mode: `--repo=digitalmodel-data` printed `Scanning: digitalmodel-data ()` and `scan_directory` received an empty path argument, allowing a PASS with no files examined.
- Failure mode observed matches issue claim: YES — empty `repo_path` from command substitution against a side-effect-only function.

**Gap proof** (no existing bash resolver tests):
- `ls scripts/legal/tests/test_*scan*.py 2>&1` → "No such file or directory" → confirms no test for the scanner resolver currently exists.

<!-- Verification: distinct sources: issue #3871 (1), legal-sanity-scan.sh:166–212 (2), legal-sanity-scan.sh:309–376 (3), legal-sanity-scan.sh:496/511 (4), tests/ directory inspection (5), issue #3560 (6), genesis_broker.py:1 (7). Count: 7. Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-09-23-issue-3871-legal-scanner-empty-scan-target.md |
| Implementation | `scripts/legal/legal-sanity-scan.sh` |
| Tests | `scripts/legal/tests/test_legal_scan_resolver.py` |
| Plan review — Claude | scripts/review/results/2026-09-23-plan-3871-claude.md |
| Plan review — Codex | scripts/review/results/2026-09-23-plan-3871-codex.md |
| Plan review — Gemini | scripts/review/results/2026-09-23-plan-3871-gemini.md |

---

## Deliverable

`legal-sanity-scan.sh` will have a single `resolve_repo_path()` definition whose contract — set `RESOLVED_REPO_PATH` as a side-effect, do not print to stdout — will be consistently honored by all callers; an empty or nonexistent resolved path will cause the script to error and exit 2 rather than silently passing with no files scanned; regression tests will confirm an initialized sibling is visited with a non-empty path.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/legal/legal-sanity-scan.sh` | Remove first (stdout-printing) definition; update callers to use `RESOLVED_REPO_PATH`; add fail-closed empty-path guard |
| Create | `scripts/legal/tests/test_legal_scan_resolver.py` | TDD: assert resolver and caller behave correctly under nominal, empty, and nonexistent-target conditions |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_resolver_sets_resolved_repo_path_for_existing_sibling` | resolver populates `RESOLVED_REPO_PATH` for a tmp dir that looks like a sibling repo | temp dir named `fakerepo` adjacent to a workspace root | script exits 0; output contains `Scanning: fakerepo (/tmp/.../fakerepo)` |
| `test_resolver_empty_path_exits_nonzero` | empty target causes exit 2 (fail-closed) | `--repo=""` or repo name that resolves to empty string | exit code 2 |
| `test_resolver_nonexistent_target_exits_nonzero` | nonexistent repo name causes exit 2 | `--repo=does-not-exist-xyz` with no matching dir | exit code 2 |
| `test_scan_directory_not_called_with_empty_arg` | `scan_directory` is never reached with empty path | nonexistent repo name | output does NOT contain `Scanning: does-not-exist-xyz ()` |
| `test_all_mode_nonexistent_submodule_exits_nonzero` | `--all` mode fails closed when submodule resolver returns empty | mocked submodule list with nonexistent path | exit code 2 |

---

## Acceptance Criteria

- [ ] `scripts/legal/legal-sanity-scan.sh` contains exactly one `resolve_repo_path` function definition.
- [ ] All callers of `resolve_repo_path` use `RESOLVED_REPO_PATH` after the call; none use command substitution.
- [ ] After `resolve_repo_path` call, script validates `[[ -n "$RESOLVED_REPO_PATH" && -d "$RESOLVED_REPO_PATH" ]]` or equivalent; exits 2 on failure.
- [ ] All new tests pass: `uv run pytest scripts/legal/tests/test_legal_scan_resolver.py -v`
- [ ] No regression: `uv run pytest scripts/legal/tests/ -v` passes.
- [ ] Manual smoke test: `bash scripts/legal/legal-sanity-scan.sh --repo=does-not-exist` exits with code 2 and prints an error message (not "Scanning: does-not-exist ()").
- [ ] Manual smoke test: `bash scripts/legal/legal-sanity-scan.sh --repo=workspace-hub` succeeds and prints a non-empty path in the Scanning line.
- [ ] Review artifacts posted to `scripts/review/results/`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Gemini | pending | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** The first `resolve_repo_path` definition (stdout-printing) may be referenced in documentation, comments, or external scripts not captured by the live checkout; search for callers before removal.
- **Risk:** Removing the first definition changes the public bash API for any caller that sources `legal-sanity-scan.sh` and calls `resolve_repo_path` expecting stdout. Verify no such callers exist outside the script itself.
- **Open:** Should `RESOLVED_REPO_PATH` be declared `local` or remain global? Current second definition makes it global (accessible to callers after return). The plan preserves global scope to minimize diff surface — flag for user during approval if a `local` scoping is preferred.

---

## Complexity: T1

**T1** — single bash script file repair; root cause fully documented in issue body; no new modules or cross-repo changes required; test file is the only new artifact.
