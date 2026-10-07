# Plan for #3834: fix(enforcement): check-engineering-register.py --self-test fails on non-UTF-8 locales

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-09-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3834
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-16-plan-3834-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/enforcement/check-engineering-register.py` — `CAPTION_ABOVE` regex at line 130: `re.compile(r"^\s*(?:Table|Figure)\s+\d+[.\-]\d+\s*[-–:].*\n\s*\|", re.M)`. Regex is correct and will match the fixture when the en-dash is intact.
- Found: `scripts/enforcement/check-engineering-register.py` — `check()` function at line 193: `path.read_text(encoding="utf-8", errors="replace")`. Reads files as UTF-8; silently replaces un-decodable bytes with U+FFFD (the replacement character).
- Found: `scripts/enforcement/check-engineering-register.py` — `self_test()` function at lines 282–292: uses `tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)` with no `encoding` kwarg. On a non-UTF-8 platform locale (Windows cp1252, ASCII), Python writes the fixture string using the platform encoding. The `caption_above` fixture contains an en-dash "–" (U+2013); on non-UTF-8 systems, this is written as a non-UTF-8 byte (0x96 in cp1252). When `check()` reads it back as UTF-8 with `errors="replace"`, the byte becomes U+FFFD, and `[-–:]` in the regex does not match U+FFFD — producing 0 findings instead of 1.
- Found: `.github/workflows/enforcement-gate.yml` — lists `check-brand-token-drift.py`, `check-scheduler-mutation-surfaces.py`, and several shell scripts. `check-engineering-register.py` is NOT invoked in any CI workflow (confirmed by grep returning no matches).
- Found: `tests/enforcement/` — contains `test_check_brand_drift.py`, `test_check_model_id_sourcing.py`, and 16 other test files. No `test_check_engineering_register.py` file exists.
- Gap: The `self_test()` function writes fixtures without `encoding='utf-8'`. One-line fix. No other encoding-related issue in the script.
- Gap: CI does not run `--self-test`, so a future regression would only be caught on a workstation. A CI step or pytest wrapper is required per the issue acceptance criteria.

### Standards

| Standard | Status | Source |
|---|---|---|
| Not applicable | — | Enforcement tooling issue; no external standards apply |

### LLM Wiki pages consulted

- No relevant wiki pages identified for this topic.

### Documents consulted

- Issue #3834 — defines the defect with a reproduction trace (ace-win-1, `e4a796e8f`, confirmed non-CRLF artifact, "defect is in the script as committed"). The fixture `caption_above` expects 1 finding, finds 0. This is source 1.
- `scripts/enforcement/check-engineering-register.py` — full inspection confirms: regex correct, read uses UTF-8, write in `self_test()` uses platform encoding. This is source 2.
- `.github/workflows/enforcement-gate.yml` — confirms `check-engineering-register.py` is absent from CI. This is source 3.
- `tests/enforcement/` directory listing — confirms no existing test file for this script. Source 4.
- `.claude/rules/engineering-register.md` — governs the caption rule and states `--self-test` is the script's own evidence that its rules work. Cited in issue body.
- `docs/plans/README.md` — no prior plan for this issue.
- Drive file search: no relevant drive files.

### Gaps identified

- `self_test()` writes fixtures without explicit `encoding='utf-8'` — will be fixed with a one-line change.
- A regression test covering caption-above and caption-below does not exist — will be created, either inline in a new `tests/enforcement/test_check_engineering_register.py` or by integrating `--self-test` into CI.
- `check-engineering-register.py` does not appear in any CI workflow — will be added to `enforcement-gate.yml`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-09-16T00:00Z via `gh issue view`):
- `#3834` — OPEN — [WRK] check-engineering-register.py --self-test harness writes fixtures in the platform encoding, so it fails on non-UTF-8 locales

**File existence** (`ls` 2026-09-16):
- EXISTS: `scripts/enforcement/check-engineering-register.py`
- EXISTS: `.github/workflows/enforcement-gate.yml`
- EXISTS: `tests/enforcement/` directory
- MISSING: `tests/enforcement/test_check_engineering_register.py` (this plan creates it)

**Line excerpts** (`sed` 2026-09-16):

`self_test()` — NamedTemporaryFile call without encoding (line ~282):
```python
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(body)
            p = Path(fh.name)
```

`check()` — reads as UTF-8 with replacement (line 193):
```python
    raw = path.read_text(encoding="utf-8", errors="replace")
```

`caption_above` fixture (contains en-dash U+2013):
```python
    "caption_above": ("Table 4.1 – Wall thickness\n| a | b |\n|---|---|\n", 1),
```

**Gap proofs**:
- `grep -n "engineering.register" .github/workflows/enforcement-gate.yml` → 0 matches — confirms CI does not run the script.
- `ls tests/enforcement/test_check_engineering_register.py` → "No such file or directory" — confirms no existing test.

**Reproduction proofs**:
Observed on `ace-win-1` at `e4a796e8f`. Issue body confirms: extracted blob via git with LF preserved still fails — the defect is in the Python source, not in line-ending handling. Root cause is the missing `encoding='utf-8'` kwarg in `NamedTemporaryFile`.

<!-- Verification: distinct sources: issue body (#3834) + check-engineering-register.py code + enforcement-gate.yml + tests/enforcement/ directory = 4 sources. Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-09-16-issue-3834-engineering-register-self-test-encoding.md` |
| Fix target | `scripts/enforcement/check-engineering-register.py` |
| New test | `tests/enforcement/test_check_engineering_register.py` |
| CI update | `.github/workflows/enforcement-gate.yml` |
| Plan review — Claude | `scripts/review/results/2026-09-16-plan-3834-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-09-16-plan-3834-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-09-16-plan-3834-agy.md` |

---

## Deliverable

`check-engineering-register.py --self-test` will exit 0 with all 29 fixtures passing on any platform, CI will fail on a self-test regression, and a pytest wrapper in `tests/enforcement/` will cover the caption-above and caption-below cases as named regression tests.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/enforcement/check-engineering-register.py` | Add `encoding='utf-8'` to `NamedTemporaryFile` call in `self_test()` |
| Create | `tests/enforcement/test_check_engineering_register.py` | Pytest wrapper invoking `--self-test` + dedicated caption-rule regression tests |
| Modify | `.github/workflows/enforcement-gate.yml` | Add `check-engineering-register.py --self-test` step so CI catches regressions |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_self_test_exits_zero` | All 29 fixtures pass on the current platform | run `--self-test` | exit code 0, no FAIL lines in stdout |
| `test_caption_above_detected` | Caption placed before table is flagged | `"Table 4.1 – Wall thickness\n| a | b |\n|---|---|\n"` | 1 finding, code R4 |
| `test_caption_below_clean` | Caption placed after table is not flagged | `"| a | b |\n|---|---|\n**Table 4.1** Wall thickness\n"` | 0 findings |
| `test_caption_above_with_hyphen` | Caption uses hyphen separator instead of en-dash | `"Table 4.1 - Wall thickness\n| a | b |\n|---|---|\n"` | 1 finding, code R4 |
| `test_caption_above_with_colon` | Caption uses colon separator | `"Table 4.1: Wall thickness\n| a | b |\n|---|---|\n"` | 1 finding, code R4 |
| `test_no_regression_on_existing_fixtures` | Parametrize all 29 SELF_TEST entries | each body | expected count matches |

---

## Acceptance Criteria

- [ ] `check-engineering-register.py --self-test` exits 0 with all fixtures passing on a UTF-8 locale. Verified by: `python scripts/enforcement/check-engineering-register.py --self-test` exits 0 and no "FAIL" appears in output.
- [ ] The caption-placement rule (`CAPTION_ABOVE`) detects the `caption_above` fixture construction. The fixture string is not changed; the fix is in the write path.
- [ ] `test_caption_above_detected` passes (R4 finding on above-caption input).
- [ ] `test_caption_below_clean` passes (0 findings on below-caption input).
- [ ] All `test_no_regression_on_existing_fixtures` parameterized cases pass.
- [ ] CI step in `enforcement-gate.yml` runs `--self-test` and the job fails if any fixture fails.
- [ ] `uv run pytest tests/enforcement/test_check_engineering_register.py -v` exits 0.
- [ ] No regression in other enforcement tests.

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

- **Risk:** Adding `encoding='utf-8'` to `NamedTemporaryFile` in `self_test()` is the one-line fix. However, on Windows, `NamedTemporaryFile(delete=False)` already creates a file that cannot be opened twice while the context manager is open (a known Windows behavior). The existing code opens it in the `with` block then reads it via `check(p)` outside the block — this pattern is correct. The `encoding` addition does not change this pattern.
- **Risk:** If the CI step invokes `--self-test` via `uv run python scripts/enforcement/check-engineering-register.py --self-test`, the CI runner's locale must support UTF-8 for the temp-file write to work even after the fix (i.e., the runner must allow Python to write UTF-8 via `NamedTemporaryFile`). With the `encoding='utf-8'` kwarg explicit, Python opens the file in binary mode under the hood with UTF-8 encoding — locale is irrelevant. This fix is therefore cross-platform and locale-agnostic.
- **Open:** The `delete=False` pattern in `self_test()` leaves temp files on disk after each run. On repeated CI runs, temp files accumulate in `/tmp`. This is not introduced by this fix but should be noted as a pre-existing cleanup gap. Out of scope for this plan; file a follow-on if it causes CI disk issues.

---

## Complexity: T1

**T1** — single one-character fix (`"w"` → `"w", encoding='utf-8'`) in one file, plus a new pytest wrapper and a CI step. All three changes are in isolated locations with no cross-file dependencies. No architectural change.
