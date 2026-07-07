# Plan for #3397: R-HOOKS false-missing on Windows CRLF paths

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-07-07
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3397
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-07-06-plan-3397-claude.md | scripts/review/results/2026-07-06-plan-3397-codex.md | scripts/review/results/2026-07-06-plan-3397-gemini.md

---

## Resource Intelligence Summary

Execution mode for implementation: `single-lane`. The change is small and tightly scoped to one readiness check plus regression tests.

### Existing repo code

- Found: `scripts/readiness/nightly-readiness.sh:480-506` implements `check_r_hooks()`. It extracts hook command paths from `.claude/settings.json` through `jq -r`, then checks each path with `[[ -f "$abs_path" ]]`.
- Found: `tests/readiness/test_nightly_readiness_hook_static_and_telegram.py` already drives `nightly-readiness.sh` against an isolated temporary `WORKSPACE_HUB`, which is the right test harness for a focused `R-HOOKS` regression.
- Found: `.claude/settings.json` contains the real hook command strings that `check_r_hooks()` scans.
- Found: the existing Python readiness helper sets a narrow `PATH`. The `R-HOOKS` regression must explicitly provide a fake `jq`, convert the fake-bin path to a Bash-usable path on Windows when needed, and assert `command -v jq` resolves to that fake. Otherwise the check can pass as `R-HOOKS: jq absent - skip` without exercising hook-path logic.
- Gap: no test currently proves that `R-HOOKS` normalizes CRLF-derived carriage returns before file existence checks.

### Standards

| Standard | Status | Source |
|---|---|---|
| Control-plane contract | context | `docs/standards/CONTROL_PLANE_CONTRACT.md` defines provider adapter surfaces and repo entry points; it is background context, not hook-specific authority. |
| Parallel-first execution | applicable | `docs/standards/PARALLEL_FIRST_EXECUTION.md` supports `single-lane` for small deterministic fixes. |
| Enforcement gradient | applicable | `.claude/rules/patterns.md` says binary yes/no rules should be scripts/tests; this issue fixes a Level-2 readiness script. |

### LLM Wiki pages consulted

- No relevant wiki pages. This is a local harness/readiness script defect.

### Documents consulted

- Issue [#3397](https://github.com/vamseeachanta/workspace-hub/issues/3397) - reports `R-HOOKS` false-missing on Windows while direct file checks pass.
- `docs/plans/README.md` - confirms the issue-plan workflow and plan index requirements.
- `scripts/data/drive-index-search/search.py "R-HOOKS R-PRECOMMIT legal-sanity pre-commit" --json --caller plan-resource-intel` - returned no relevant drive-file hits; several drive indexes were unreachable on this Windows host and two metadata indexes were stale, so no off-repo evidence is used.

### Gaps identified

- `check_r_hooks()` does not strip `\r` from jq output before constructing paths.
- `check_r_hooks()` only checks `command -v jq`; it does not prove `jq --version` can execute or that the extraction evaluated at least one literal hook path in the real settings file.
- The test suite lacks a deterministic CRLF jq-output fixture for `R-HOOKS`.
- The current Python readiness helper can hide the bug if `jq` is absent from its test `PATH`; the test must assert the non-skip success/failure detail and verify the fake `jq` path is actually used.
- The fix must preserve real missing-hook detection and skip behavior for variable-expanded paths.

### Evidence

**Issue status** (verified 2026-07-07 via `gh issue view 3397`):
- `#3397` - OPEN - `bug(readiness): R-HOOKS false-missing on Windows CRLF paths`; labels include `status:needs-plan` and `lane:codex`.

**File existence** (verified 2026-07-07):
- EXISTS: `scripts/readiness/nightly-readiness.sh`
- EXISTS: `tests/readiness/test_nightly_readiness_hook_static_and_telegram.py`
- EXISTS: `.claude/settings.json`

**Line excerpts**:

```text
scripts/readiness/nightly-readiness.sh:485-499
local missing=()
while IFS= read -r hook_path; do
  ...
  [[ -f "$abs_path" ]] || missing+=("$hook_path")
done < <(jq -r '.. | strings | select(test("bash ")) | split("bash ")[1]
                   | split(" ")[0] | select(length > 0)
                   | select(startswith("-") | not)
                   | select(contains("/") or test("\\.sh$"))' \
             "$settings" 2>/dev/null | sort -u || true)
```

**Reproduction proofs**:

```text
$ git rev-parse --short HEAD
9e8cd55b0
$ jq --version
jq-1.8.1
$ bash scripts/readiness/nightly-readiness.sh 2>&1 | grep 'R-HOOKS'
FAIL R-HOOKS: hook scripts missing from disk: .claude/hooks/check-state-file-size-precommit.sh
```

```text
$ jq hook-path extraction under Git Bash, with hex dump
first extracted path bytes:
2e 63 6c 61 75 64 65 2f ... 70 72 65 63 6f 6d 6d 69 74 2e 73 68 0d 0a
```

```text
$ same extraction piped through tr -d '\r' and checked with [[ -f ]]
OK:.claude/hooks/check-state-file-size-precommit.sh
OK:.claude/hooks/check-state-file-size-prepush.sh
...
OK:.claude/statusline-combined.sh
```

Reproduced at: 2026-07-07. Failure mode observed matches issue claim: YES.

Source count: 8 distinct sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-07-issue-3397-readiness-hooks-crlf-normalization.md` |
| Tests | `tests/readiness/test_nightly_readiness_hook_static_and_telegram.py` |
| Implementation | `scripts/readiness/nightly-readiness.sh` |
| Plan index | `docs/plans/README.md` |
| Plan review - Claude | `scripts/review/results/2026-07-06-plan-3397-claude.md` |
| Plan review - Codex | `scripts/review/results/2026-07-06-plan-3397-codex.md` |
| Plan review - Gemini | `scripts/review/results/2026-07-06-plan-3397-gemini.md` |

---

## Deliverable

`R-HOOKS` will normalize CRLF-derived carriage returns before static hook path checks, with regression coverage proving Windows CRLF hook paths pass while genuinely missing hooks still fail.

---

## Pseudocode

```text
function check_r_hooks:
    require jq to be on PATH and executable via jq --version
    extract hook_path strings from settings.json with jq
    if jq extraction exits nonzero, fail R-HOOKS instead of passing with an empty list
    normalize each extracted hook_path by removing carriage returns
    skip empty paths and variable-expanded paths as today
    count literal hook paths actually evaluated
    resolve relative paths under WORKSPACE_HUB
    if resolved file is missing, add normalized hook_path to missing[]
    pass only when missing[] is empty and include evaluated count in the pass detail

function test helper for fake jq:
    create fake-bin/jq script that prints deterministic path tokens ending in \r\n
    convert fake-bin to a Bash path with cygpath -u when available
    run nightly-readiness with PATH=fake-bin:/usr/bin:/bin:/usr/local/bin
    assert command -v jq from the same PATH points at fake-bin/jq
    for missing-path output tests, capture stdout as bytes and assert no literal \r remains in the R-HOOKS line
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/readiness/nightly-readiness.sh` | Strip `\r` from jq-derived hook paths before static file checks. |
| Modify | `tests/readiness/test_nightly_readiness_hook_static_and_telegram.py` | Add deterministic fake-`jq` CRLF-output regression, missing-hook preservation, and variable-expanded path skip tests for `R-HOOKS`. |
| Update | `docs/plans/README.md` | Add this plan to the index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_r_hooks_crlf_jq_output_paths_pass_when_files_exist` | CRLF-derived `\r` from the jq-output stream is normalized before `[[ -f ]]`. | Temporary workspace with a fake `jq` placed first on Bash `PATH` that emits `.claude/hooks/existing.sh\r\n`, plus a matching hook file. | `command -v jq` resolves to fake `jq`; `R-HOOKS` line starts with `OK`, contains `all hook scripts present`, and does not contain `jq absent`. |
| `test_r_hooks_still_fails_for_missing_normalized_hook` | Normalization does not mask real missing files and does not print a carriage return in the missing path. | Fake `jq` emits `.claude/hooks/missing.sh\r\n` and no matching hook file exists. Capture stdout as bytes, not `text=True`. | Raw `R-HOOKS` bytes contain `.claude/hooks/missing.sh`, do not contain `.claude/hooks/missing.sh\r`, and do not contain `jq absent`. |
| `test_r_hooks_broken_jq_fails_not_passes_empty` | A `jq` executable that cannot run does not make `R-HOOKS` pass vacuously. | Fake `jq` exists first on `PATH` but exits nonzero. | `R-HOOKS` line starts with `FAIL` and identifies jq execution/extraction failure. |
| `test_r_hooks_still_skips_variable_expanded_paths` | Existing skip behavior for `${...}` and `$(...)` path tokens is preserved while at least one real literal path is evaluated. | Fake `jq` emits one existing static hook path plus `${WORKSPACE_HUB}/...` and `$(git rev-parse --show-toplevel)/...` CRLF path tokens. | `R-HOOKS` does not report variable-expanded paths missing and pass detail shows a nonzero evaluated count. |
| `test_hook_static_real_hooks_pass` | Existing adjacent readiness behavior remains green. | Real repo hooks. | Existing `R-HOOK-STATIC` test continues to pass. |

---

## Acceptance Criteria

- [ ] New `R-HOOKS` tests are written first and fail before implementation; they must exercise hook-path checking, not the `jq absent` skip path.
- [ ] `uv run pytest tests/readiness/test_nightly_readiness_hook_static_and_telegram.py -q` passes after implementation.
- [ ] `bash -lc "command -v jq; jq --version"` succeeds on ace-win-2 before accepting the real-run result.
- [ ] `bash scripts/readiness/nightly-readiness.sh` no longer fails `R-HOOKS` on ace-win-2, and the `R-HOOKS` pass detail proves a nonzero number of literal hook paths were evaluated.
- [ ] A purposely missing hook path still fails `R-HOOKS` in the regression test.
- [ ] `bash scripts/legal/legal-sanity-scan.sh --diff-only` passes in `workspace-hub`.
- [ ] Plan and implementation receive the required adversarial review before approval/merge.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | CLI trust dialog blocked non-interactive review. |
| Codex r1 | MAJOR | Test could pass through `jq absent` skip; CRLF fixture was not deterministic; variable-expanded skip requirement lacked coverage; review artifact paths used the wrong date. |
| Codex r2 | MAJOR | Fake-`jq` PATH mechanics were underspecified for the current helper/Windows Git Bash; missing-hook test needed raw-byte assertions; reproduction evidence needed commit/jq state; standards citation overclaimed control-plane contract. |
| Codex r3 | MAJOR | Valid: real-run acceptance needed working `jq --version` and nonzero evaluated-path proof. Stale/incorrect: Codex artifact was rechecked locally as non-empty (2700 bytes, 18 lines). |
| Gemini | UNAVAILABLE | No non-interactive Gemini auth configured. |

**Overall result:** FAIL - re-draft required before approval.

Revisions made based on review:
- Tightened the TDD list to require a fake `jq` on `PATH` emitting CRLF path tokens, with assertions that the line is not the `jq absent` skip.
- Added a variable-expanded path skip regression because the plan names that preservation requirement.
- Reconciled review artifact paths to the actual 2026-07-06 fanout output names.
- Added fake-`jq` helper requirements: optional PATH injection, Bash path conversion on Windows, and `command -v jq` assertion.
- Changed the missing-hook output regression to inspect raw stdout bytes so carriage-return leakage cannot be hidden by `text=True` or `splitlines()`.
- Replaced the overclaimed control-plane citation with a context-only citation and refreshed reproduction evidence with commit and `jq` version.
- Added implementation and acceptance requirements for `jq --version`, jq extraction failure handling, and nonzero evaluated-hook-path proof in the `R-HOOKS` pass detail.

---

## Risks and Open Questions

- **Risk:** stripping `\r` in the wrong place could alter intentionally literal hook command strings. Mitigation: normalize only the extracted path token, not the full JSON command.
- **Risk:** a broad "remove all control characters" patch could hide malformed settings. Mitigation: strip only carriage return and keep `R-SETTINGS` as the JSON validity gate.
- **Open:** none.

---

## Complexity: T1

**T1** - one script fix plus focused regression tests; no architecture or cross-repo write surface.
