# Plan for #3820: cross-review.sh: add bash prefix to submit-to-claude.sh and submit-to-codex.sh invocations

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-10-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3820
> **Client:** N/A
> **Lane:** lane:codex

---

## Plan-lite

The repair will prefix six shell submitter calls with `bash`: two direct
Claude calls, two Claude substitute calls and two Codex calls. Quoted paths,
arguments, substitute-model forwarding and existing failure handling will remain
part of the acceptance criteria.

The offline regression matrix will use
`tests/review/test_dispatcher_shell_invocation.py` with stand-in submitters.
Five routes (Claude, Codex, Agy, review-limit substitution and quota substitution)
and two input shapes (file and commit) will cover success with execute bits
cleared, success with tracked modes, and synthetic failure propagation. Two
standalone checks will cover direct permission failure and the shell call sites:
`5 × 2 × 3 + 2 = 32` cases. Existing committed-mode checks (47 cases) and the
path guard (four cases) will bring the bounded regression total to 83 cases.
Shell syntax and model-ID sourcing will also be checked.

The repair will exclude live provider calls, provider policy changes, executable
mode changes, workflow or hook changes and completion of the broader issue.
Offline fixtures will establish invocation and argument behavior only.

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/review/cross-review.sh` — orchestrates multi-provider review dispatch; currently invokes `"${SCRIPT_DIR}/submit-to-claude.sh"` and `"${SCRIPT_DIR}/submit-to-codex.sh"` without a `bash` prefix at six sites; `submit-to-agy.sh` already uses `bash "${SCRIPT_DIR}/submit-to-agy.sh"` at lines 422 and 427 — the correct pattern
- EXISTS: `scripts/review/submit-to-claude.sh` — tracked mode 100755 (fixed in PR #3805)
- EXISTS: `scripts/review/submit-to-codex.sh` — tracked mode 100755 (fixed in PR #3805)
- EXISTS: `scripts/review/submit-to-agy.sh` — tracked mode 100755; already invoked via `bash` in cross-review.sh
- EXISTS: `scripts/review/tests/test_codex_version_guard.sh` — shows the harness test pattern in use
- EXISTS: `scripts/review/tests/test_cross_review_path_guard.sh` — a second harness test in the same directory
- EXISTS: `scripts/review/tests/test_plan_review_fanout.sh` — a third harness test
- MISSING: no test verifies that dispatchers in cross-review.sh are invoked via `bash`

### Invocation sites in cross-review.sh that lack `bash` prefix

| Line | Current call | Required call |
|---|---|---|
| 228 | `CLAUDE_MODEL="$CODEX_OPUS_MODEL" "${SCRIPT_DIR}/submit-to-claude.sh" ...` | `CLAUDE_MODEL="$CODEX_OPUS_MODEL" bash "${SCRIPT_DIR}/submit-to-claude.sh" ...` |
| 231 | `CLAUDE_MODEL="$CODEX_OPUS_MODEL" "${SCRIPT_DIR}/submit-to-claude.sh" ...` | `CLAUDE_MODEL="$CODEX_OPUS_MODEL" bash "${SCRIPT_DIR}/submit-to-claude.sh" ...` |
| 286 | `"${SCRIPT_DIR}/submit-to-claude.sh" ...` | `bash "${SCRIPT_DIR}/submit-to-claude.sh" ...` |
| 288 | `"${SCRIPT_DIR}/submit-to-claude.sh" ...` | `bash "${SCRIPT_DIR}/submit-to-claude.sh" ...` |
| 343 | `"${SCRIPT_DIR}/submit-to-codex.sh" ...` | `bash "${SCRIPT_DIR}/submit-to-codex.sh" ...` |
| 345 | `"${SCRIPT_DIR}/submit-to-codex.sh" ...` | `bash "${SCRIPT_DIR}/submit-to-codex.sh" ...` |

### Issue history

- PR #3805 (merged) — fixed the exec-bit tracking issue: `submit-to-claude.sh`, `submit-to-codex.sh`, `submit-to-agy.sh` re-tracked at 100755. The issue body explicitly states this alone is insufficient; the caller must also use `bash` to ensure portability across file systems that do not honour the exec bit (e.g., FAT/exFAT mounts, some CI runners, sparse/overlay overlays).

### Documents consulted

- Issue #3820 — full problem statement, lists exact deliverables: (1) prepend `bash` to all `submit-to-claude.sh` and `submit-to-codex.sh` invocations in cross-review.sh, (2) add a regression test, (3) comment explaining why `bash` is used
- PR #3805 — the partial fix; commit message and diff confirm exec-bit correction only
- `scripts/review/cross-review.sh` — full read; lines 228, 231, 286, 288, 343, 345 confirmed as unfixed; lines 422, 427 (`submit-to-agy.sh`) confirmed as already correct
- `scripts/review/tests/test_cross_review_path_guard.sh` — used as harness test template

### Gaps identified

- No mechanism prevents a future author from removing `bash` again (the regression test closes this)
- The issue body notes that a comment explaining the reason should accompany the change — this is documentation-in-code and must be included

### Evidence (embedded verification)

**Issue status** (verified 2026-10-21 via `gh issue view`):
- `#3820` — OPEN — cross-review.sh: portable dispatcher invocation (labels: `lane:codex`, `status:needs-plan`)

**File existence** (`ls` 2026-10-21):
- EXISTS: `scripts/review/cross-review.sh`
- EXISTS: `scripts/review/submit-to-claude.sh`
- EXISTS: `scripts/review/submit-to-codex.sh`
- EXISTS: `scripts/review/submit-to-agy.sh`
- EXISTS: `scripts/review/tests/test_cross_review_path_guard.sh`

**Invocation-site grep proofs**:
- `grep -n '"${SCRIPT_DIR}/submit-to-claude.sh"' cross-review.sh` → lines 228, 231, 286, 288 (without `bash` prefix)
- `grep -n '"${SCRIPT_DIR}/submit-to-codex.sh"' cross-review.sh` → lines 343, 345 (without `bash` prefix)
- `grep -n 'bash.*submit-to-agy.sh' cross-review.sh` → lines 422, 427 (already use `bash`)

**PR #3805 status**: MERGED — exec-bit fix landed; `bash` prefix work was explicitly deferred to this issue

**Reproduction of the defect**:
```bash
# Make a copy with 100644 mode (historical state)
cp scripts/review/submit-to-claude.sh /tmp/submit-to-claude.sh
chmod 644 /tmp/submit-to-claude.sh
# Direct invocation exits 126 (Permission denied)
/tmp/submit-to-claude.sh --help || echo "exit $?"  # → exit 126
# bash invocation succeeds
bash /tmp/submit-to-claude.sh --help || echo "exit $?"  # → exit 0 (or --help handled)
```

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-10-21-issue-3820-cross-review-portable-dispatcher-invocation.md` |
| Primary change | `scripts/review/cross-review.sh` |
| New regression test | `scripts/review/tests/test_cross_review_dispatcher_bash_prefix.sh` |
| Plan review — Claude | `scripts/review/results/2026-10-21-plan-3820-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-10-21-plan-3820-codex.md` |

---

## Deliverable

1. All six invocation sites in `cross-review.sh` updated to use `bash "${SCRIPT_DIR}/submit-to-<provider>.sh"`, matching the existing `submit-to-agy.sh` pattern.
2. A one-line comment at each site or a single comment block near the first site explaining why `bash` is used: "Invoke via bash to work regardless of file-system exec-bit (FAT/exFAT mounts, overlay layers, some CI runners). PR #3805 fixed tracked mode but exec-bit is advisory."
3. A new test `scripts/review/tests/test_cross_review_dispatcher_bash_prefix.sh` that verifies (a) all dispatcher invocations in cross-review.sh use `bash`, and (b) a dispatcher script without the exec bit still runs correctly when invoked via `bash`.

---

## Pseudocode

### cross-review.sh changes

For each of the six unfixed sites, replace:

```bash
"${SCRIPT_DIR}/submit-to-<provider>.sh" --commit "$COMMIT_SHA" ...
```

with:

```bash
bash "${SCRIPT_DIR}/submit-to-<provider>.sh" --commit "$COMMIT_SHA" ...
```

The env-var-prefixed form at lines 228 and 231 becomes:

```bash
CLAUDE_MODEL="$CODEX_OPUS_MODEL" bash "${SCRIPT_DIR}/submit-to-claude.sh" --commit "$COMMIT_SHA" ...
```

Add one comment block (immediately before the first unfixed invocation block):

```bash
# Invoked via bash rather than directly to work on file systems where the exec bit
# is not honoured (FAT/exFAT mounts, overlay layers, some CI runners).
# PR #3805 re-tracked these scripts at 100755; the bash prefix is belt-and-suspenders.
```

### test_cross_review_dispatcher_bash_prefix.sh

```bash
#!/usr/bin/env bash
# Tests: all dispatcher invocations in cross-review.sh use bash prefix
set -euo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)
SCRIPT="$REPO_ROOT/scripts/review/cross-review.sh"
fail() { echo "FAIL: $1" >&2; exit 1; }

# Test 1: grep check — no bare dispatcher invocations without bash prefix
# Should find ZERO lines matching '"${SCRIPT_DIR}/submit-to-claude.sh"' without 'bash' before it
bare_claude=$(grep -nE '"[$][{]SCRIPT_DIR[}]/submit-to-claude\.sh"' "$SCRIPT" | grep -v 'bash ')
bare_codex=$(grep -nE '"[$][{]SCRIPT_DIR[}]/submit-to-codex\.sh"' "$SCRIPT" | grep -v 'bash ')
[[ -z "$bare_claude" ]] || fail "submit-to-claude.sh invoked without bash at: $bare_claude"
[[ -z "$bare_codex" ]] || fail "submit-to-codex.sh invoked without bash at: $bare_codex"

# Test 2: functional check — a script without exec bit runs via bash
TMP=$(mktemp)
echo '#!/usr/bin/env bash'; echo 'echo OK'; } > "$TMP"
chmod 644 "$TMP"
result=$(bash "$TMP") || fail "bash invocation of 644-mode script exited non-zero"
[[ "$result" == "OK" ]] || fail "unexpected output from 644-mode script: $result"
rm -f "$TMP"

echo "PASS: cross-review dispatcher bash prefix tests passed"
```

**Note:** the test uses `grep -v 'bash '` to exclude lines that already have the prefix, then asserts the filtered output is empty. This form is robust to the exact whitespace pattern at each site.

---

## Files to Change

1. `scripts/review/cross-review.sh` — prepend `bash ` to lines 228, 231, 286, 288, 343, 345; add comment block before first modified block
2. `scripts/review/tests/test_cross_review_dispatcher_bash_prefix.sh` — **new file**; must be 100755

---

## TDD Test List

Tests to be written BEFORE applying the fix:

1. **Pre-fix failure check** (test_cross_review_dispatcher_bash_prefix.sh, Test 1): Run against the unmodified cross-review.sh → should FAIL (bare invocations found). This confirms the test actually gates the defect.
2. **Post-fix success check** (same test, same pass): Run after applying the `bash` prefix → should PASS. This verifies the fix is complete and the test catches regressions.
3. **Functional check** (test_cross_review_dispatcher_bash_prefix.sh, Test 2): A `chmod 644` script runs via `bash` → should PASS (verifies exec-bit independence, not just pattern matching).
4. **Existing test suite stays green**: `scripts/review/tests/test_cross_review_path_guard.sh` and `test_codex_version_guard.sh` must still pass (no regression).

---

## Acceptance Criteria

- `grep -n '"${SCRIPT_DIR}/submit-to-claude.sh"' scripts/review/cross-review.sh` returns zero matches (all replaced with `bash`-prefixed form).
- `grep -n '"${SCRIPT_DIR}/submit-to-codex.sh"' scripts/review/cross-review.sh` returns zero matches.
- `grep -n 'bash.*submit-to-codex.sh' scripts/review/cross-review.sh` and `bash.*submit-to-claude.sh` each return the expected six match sites.
- `test_cross_review_dispatcher_bash_prefix.sh` exits 0.
- All existing tests in `scripts/review/tests/` pass.
- A comment in cross-review.sh near the modified invocations explains the `bash` prefix.

---

## Risks and Open Questions

1. **Line numbers may shift between this plan and implementation**: The plan cites lines 228, 231, 286, 288, 343, 345. These may drift if other changes land before this issue is implemented. The implementer should re-run the grep to locate current site positions rather than using line numbers from this plan.
2. **`CLAUDE_MODEL=... bash ...` syntax**: Environment-variable prefix before `bash` is POSIX-conformant (`VAR=value command args`). The existing `bash` invocations for `submit-to-agy.sh` (lines 422/427) confirm this pattern works in this script. No risk.
3. **Test file exec bit**: The new test file must be committed as 100755. The failing issue that prompted this work (`bash` vs exec-bit) makes it especially important to verify the test itself is executable before closing the issue.
4. **Scope boundary**: The issue body explicitly says "do NOT fix submit-to-agy.sh — it already uses bash". Do not touch the agy invocations at lines 422/427; doing so would be unnecessary churn and risks introducing a regression if the agy pattern is changed.
