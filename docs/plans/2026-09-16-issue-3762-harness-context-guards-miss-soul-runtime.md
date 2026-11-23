# Plan for #3762: fix(harness): both context guards are name-based and miss the 20KB file that actually auto-loads

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-09-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3762
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-16-plan-3762-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/readiness/nightly-readiness.sh` lines 69–97 — `check_r5()` function with a hardcoded `candidates` array: `("${WORKSPACE_HUB}/AGENTS.md" "${WORKSPACE_HUB}/.claude/rules/coding-style.md" "${WORKSPACE_HUB}/.claude/rules/patterns.md")`. No entry for `config/agents/claude/SOUL.runtime.md` or `config/agents/SHARED_SOUL.md`.
- Found: `scripts/readiness/nightly-readiness.sh` lines 297–321 — `check_r_harness()` function with a `harness_map` covering `CLAUDE.md`, `MEMORY.md`, `AGENTS.md`, `CODEX.md`, `GEMINI.md`. No entry for `SOUL.runtime.md`.
- Found: `scripts/enforcement/check-harness-file-size.sh` lines 63–64 — `git ls-files` glob pattern: `'CLAUDE.md' 'MEMORY.md' 'AGENTS.md' 'GEMINI.md' '**/CLAUDE.md' '**/MEMORY.md' '**/AGENTS.md' '**/GEMINI.md'`. No `SOUL.runtime.md` or `SHARED_SOUL.md` pattern.
- Gap: No test file that mutation-verifies either guard. The comment in `check_r5` at line 81–82 explains the policy ("a missing candidate must FAIL") but there is no automated test that confirms this property holds when the candidate list is wrong.

### Standards

| Standard | Status | Source |
|---|---|---|
| Not applicable | — | Harness/Infrastructure issue; no external standards apply |

### LLM Wiki pages consulted

- No relevant wiki pages identified for this topic.

### Documents consulted

- Issue #3762 — defines the defect with a measured evidence table (SOUL.runtime.md at 245 lines / 20 KB; SHARED_SOUL.md at 178 lines / 15 KB; neither covered by either guard). This is source 1.
- Issue #3744 — dangling-reference precedent: R5 reported PASS while summing 3 of 7 files after a deletion; the same fail-on-missing semantics that #3744 added were not extended to cover the SOUL surface. Confirms the defect class is known and recurs on rename/retirement events.
- PR #3749 — introduced the `~/.claude/CLAUDE.md → config/agents/claude/SOUL.runtime.md` symlink on 2026-08-01. The PR notes mention the uncovered file as an "open consideration" but do not file a follow-on issue or extend the guard. This is the creation event for the gap.
- Related issue #3743 — retirement decision and the do-not-recreate guards for CLAUDE.md.
- `docs/plans/README.md` — searched; no prior plan for this issue exists.
- Drive file search: no relevant drive files for harness readiness guard scope.

### Gaps identified

- `check_r5` candidates list will be extended to include `config/agents/claude/SOUL.runtime.md` and `config/agents/SHARED_SOUL.md` by path. A role-based lookup (glob or a harness-surfaces config file) will be introduced so that a future rename triggers a FAIL rather than silent omission.
- `check-harness-file-size.sh` glob set will be extended with `'**/SOUL.runtime.md'` and `'**/SHARED_SOUL.md'` (or a role-based pattern). The MAX_LINES cap will be reviewed against the current 245-line SOUL.runtime.md; if the cap is raised or exempted for these surfaces, the exemption will be documented inline.
- A mutation test does not exist and will be created. It will: (a) confirm R5 fails when a known harness surface is absent from the candidate list, and (b) confirm `check-harness-file-size.sh` flags SOUL.runtime.md when the glob matches it.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-09-16T00:00Z via `gh issue view`):
- `#3762` — OPEN — fix(harness): both context guards are name-based and miss the 20KB file that actually auto-loads
- `#3744` — referenced — dangling-reference precedent, same defect class
- `#3749` — referenced PR — symlink introduction event

**File existence** (`ls` 2026-09-16):
- EXISTS: `scripts/readiness/nightly-readiness.sh`
- EXISTS: `scripts/enforcement/check-harness-file-size.sh`
- EXISTS: `config/agents/claude/SOUL.runtime.md` — 245 lines (verified via `wc -l`)
- EXISTS: `config/agents/SHARED_SOUL.md` — 178 lines (verified via `wc -l`)
- MISSING (this plan creates): `tests/enforcement/test_check_harness_context_guards.py`

**Line excerpts** (`sed` 2026-09-16):

`check_r5` candidates array (nightly-readiness.sh lines 73–77):
```
  local candidates=(
    "${WORKSPACE_HUB}/AGENTS.md"
    "${WORKSPACE_HUB}/.claude/rules/coding-style.md"
    "${WORKSPACE_HUB}/.claude/rules/patterns.md"
  )
```

`check-harness-file-size.sh` glob pattern (lines 63–64):
```
    git ls-files 'CLAUDE.md' 'MEMORY.md' 'AGENTS.md' 'GEMINI.md' \
                 '**/CLAUDE.md' '**/MEMORY.md' '**/AGENTS.md' '**/GEMINI.md' \
```

**Gap proofs**:
- `grep -n "SOUL" scripts/readiness/nightly-readiness.sh` → matches only comment references (lines 167, 197, 558) — confirms SOUL.runtime.md is NOT in the candidates or harness_map arrays.
- `grep -n "SOUL" scripts/enforcement/check-harness-file-size.sh` → 0 matches — confirms SOUL.runtime.md is NOT in the file-size glob.

**Reproduction proofs**:
N/A — this defect does not produce a runtime failure; it produces a silent false-PASS. The reproduction is confirmed by reading the candidate list (above) and comparing it to the actual auto-loaded files listed in the issue evidence table.

<!-- Verification: distinct sources: issue body (#3762) + issue #3744 + PR #3749 + nightly-readiness.sh + check-harness-file-size.sh + wc -l counts = 6 sources. Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-09-16-issue-3762-harness-context-guards-miss-soul-runtime.md` |
| Guard 1 (context budget) | `scripts/readiness/nightly-readiness.sh` |
| Guard 2 (file-size enforcement) | `scripts/enforcement/check-harness-file-size.sh` |
| New test | `tests/enforcement/test_check_harness_context_guards.py` |
| Plan review — Claude | `scripts/review/results/2026-09-16-plan-3762-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-09-16-plan-3762-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-09-16-plan-3762-agy.md` |

---

## Deliverable

Both harness context guards will cover `SOUL.runtime.md` and `SHARED_SOUL.md` by role-anchored pattern, a mutation test will confirm that adding a new harness surface without updating the guard produces a FAIL, and R5 will report the true per-session context budget (≥35 KB as of 2026-09-16).

---

## Pseudocode

```
# nightly-readiness.sh check_r5 — extend candidates by role
SOUL_RUNTIME = path of file at $(readlink -f ~/.claude/CLAUDE.md)   # resolves symlink
SHARED_SOUL  = WORKSPACE_HUB/config/agents/SHARED_SOUL.md
candidates = [
  WORKSPACE_HUB/AGENTS.md,
  WORKSPACE_HUB/.claude/rules/coding-style.md,
  WORKSPACE_HUB/.claude/rules/patterns.md,
  SOUL_RUNTIME,                 # resolves via symlink; fail if symlink broken
  SHARED_SOUL,
]
# rest of check_r5 unchanged: sum sizes, fail on missing, fail on > 16KB
# NOTE: cap will likely need raising to 64KB to match reality

# check-harness-file-size.sh — extend glob set
git ls-files 'CLAUDE.md' 'MEMORY.md' 'AGENTS.md' 'GEMINI.md' \
             '**/CLAUDE.md' '**/MEMORY.md' '**/AGENTS.md' '**/GEMINI.md' \
             '**/SOUL.runtime.md' '**/SHARED_SOUL.md'
# MAX_LINES cap: SOUL.runtime.md is 245 lines; either raise cap to 250
# or document the exemption with an explicit inline comment and an
# --allow flag matching the file pattern

# test_check_harness_context_guards.py
def test_r5_fails_on_missing_candidate():
    # Temporarily rename SOUL.runtime.md out of place, run check_r5,
    # assert non-zero exit code

def test_r5_reports_full_budget():
    # Run check_r5, capture stdout, assert reported KB >= 30

def test_file_size_check_catches_soul_runtime():
    # Create a temp file named SOUL.runtime.md with 300 lines,
    # run check-harness-file-size.sh against it, assert non-zero exit

def test_file_size_check_passes_under_cap():
    # Create a temp file named SOUL.runtime.md with 10 lines,
    # run check-harness-file-size.sh, assert exit 0
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/readiness/nightly-readiness.sh` | Extend `check_r5` candidates to include SOUL.runtime.md (via symlink resolution) and SHARED_SOUL.md; raise or document the 16 KB cap |
| Modify | `scripts/enforcement/check-harness-file-size.sh` | Extend glob to include `**/SOUL.runtime.md` and `**/SHARED_SOUL.md`; adjust MAX_LINES cap or add pattern-specific allow logic |
| Create | `tests/enforcement/test_check_harness_context_guards.py` | Mutation-verified tests per the Acceptance criteria in #3762 |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_r5_candidate_list_covers_soul_runtime` | SOUL.runtime.md is in the R5 candidates | live checkout | grep of nightly-readiness.sh candidates block includes SOUL path |
| `test_r5_candidate_list_covers_shared_soul` | SHARED_SOUL.md is in the R5 candidates | live checkout | grep of candidates block includes SHARED_SOUL path |
| `test_r5_fails_when_soul_runtime_missing` | Missing candidate → FAIL, not PASS | temp removal of SOUL.runtime.md | `check_r5` exits non-zero with message |
| `test_r5_reports_budget_including_soul_surfaces` | Reported KB includes SOUL.runtime.md size | live files | reported budget ≥ 30 KB |
| `test_file_size_guard_catches_soul_runtime_oversize` | SOUL.runtime.md at 300 lines fails the cap check | temp 300-line SOUL.runtime.md | `check-harness-file-size.sh` exits non-zero |
| `test_file_size_guard_passes_soul_runtime_under_cap` | SOUL.runtime.md under cap passes | temp 10-line SOUL.runtime.md | exit 0 |

---

## Acceptance Criteria

- [ ] `check_r5` in `scripts/readiness/nightly-readiness.sh` lists `config/agents/claude/SOUL.runtime.md` (or its symlink target) and `config/agents/SHARED_SOUL.md` as candidates. Verified by: `grep -c SOUL scripts/readiness/nightly-readiness.sh` returns ≥ 2.
- [ ] `check_r5` fails (non-zero exit and FAIL log line) when any listed candidate is missing — mutation verified by temporarily renaming SOUL.runtime.md.
- [ ] `check_r5` reports the true budget (≥ 30 KB in current state). Verified by running the function and inspecting stdout.
- [ ] `scripts/enforcement/check-harness-file-size.sh` includes `SOUL.runtime.md` in its file scan, verified by: passing a temporary 300-line file named `SOUL.runtime.md` returns non-zero.
- [ ] All new tests pass: `uv run pytest tests/enforcement/test_check_harness_context_guards.py -v`
- [ ] No regression: existing nightly-readiness checks that currently pass continue to pass.
- [ ] If the KB cap is raised, the new value is documented inline with rationale citing issue #3762.

---

## Adversarial Review Summary

<!-- To be populated after adversarial review step completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Agy | — | — |

---

## Risks and Open Questions

- **Risk:** The symlink `~/.claude/CLAUDE.md → config/agents/claude/SOUL.runtime.md` resolves at runtime on a specific host. On other machines, the symlink may point elsewhere or not exist. The candidate lookup should use the repo-relative path `${WORKSPACE_HUB}/config/agents/claude/SOUL.runtime.md` directly rather than resolving the symlink — this is more portable and the symlink is already documented as a runtime convenience, not the canonical path.
- **Open:** Should the 16 KB budget cap in R5 be raised? SOUL.runtime.md alone is 20 KB (245 lines). The current cap is already exceeded. Raising to 64 KB or removing the hard cap in favour of a WARNING threshold is a design decision that requires user input before implementation. The plan leaves the cap-decision open; the implementer will flag it as an open question at plan-approved stage.
- **Open:** Should `SHARED_SOUL.md` be in the file-size guard? At 178 lines, it exceeds MAX_LINES=20 significantly. The current guard is explicitly for "agent harness files" — SHARED_SOUL.md is arguably the canonical harness. Decision: yes, it should be covered; the MAX_LINES cap for non-stub harness files should be separately defined or the two files should be explicitly documented as "large-by-design" in the guard script.

---

## Complexity: T2

**T2** — modifies two existing scripts plus creates a new test file. The scripts contain non-trivial logic (fail-on-missing semantics, glob scan, wc-based line counting). Test requires temporary file manipulation and subprocess invocation of bash scripts. No new module is introduced; all changes are local to existing files.
