# Plan for #3811: openfoam-analysis: SIMPLEC written with plain-SIMPLE relaxation, and p in the wrong sub-dictionary

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-08-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3811
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-26-plan-3811-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/openfoam-analysis/run-analysis.sh` lines 101–107 — Python inline code that generates `system/fvSolution` for `simpleFoam`. Confirmed the two defective lines at lines 104–106:
  - Line 102: `f.write('SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }\n')` — enables SIMPLEC mode
  - Line 104: `f.write('relaxationFactors { equations {\n')` — opens equations sub-dictionary (correct for U/k/omega; wrong for p)
  - Line 105: `f.write(f'  U {relax.get("U", 0.7)}; p {relax.get("p", 0.3)};\n')` — puts `p` into `equations` (wrong sub-dict), keeps 0.3 pressure relaxation (wrong for SIMPLEC), and defaults U to 0.7 (low for SIMPLEC)
- Found: `scripts/openfoam-analysis/validate-analysis.py` — post-run output checker; does not validate `fvSolution` content; not a test surface for this fix
- Found: `scripts/openfoam-analysis/generate-calc-yaml.py` — calc report generator; reads convergence verdicts; not affected by this fix
- Found: `tests/openfoam/test_verify_openfoam_baseline.py` — existing OpenFOAM test module; tests `verify-openfoam-baseline.sh` and `run-openfoam-tutorials.sh`, not `run-analysis.sh`. Gap: no unit test exists for the fvSolution generation logic in `run-analysis.sh`.

### Standards

| Standard | Status | Source |
|---|---|---|
| OpenFOAM v2312 User Guide — SIMPLEC `consistent yes` eliminates need for pressure relaxation | Confirmed (cited in issue body) | Issue #3811 body + OpenFOAM v2312 docs |
| OpenFOAM fvSolution structure — `p` is a field relaxation factor, belongs under `relaxationFactors.fields`, not `relaxationFactors.equations` | Confirmed | Issue #3811 body + OpenFOAM v2312 User Guide §6.3 |

### LLM Wiki pages consulted

- No relevant wiki pages found under `knowledge/wikis/` for OpenFOAM fvSolution dict structure.

### Documents consulted

- Issue #3811 body — two defects precisely identified with corrected block included; cited the v2312 User Guide statement
- `scripts/openfoam-analysis/run-analysis.sh` (live checkout) — confirmed exact defective code at lines 102–106
- `tests/openfoam/test_verify_openfoam_baseline.py` (live checkout) — confirmed no test coverage for fvSolution generation in `run-analysis.sh`

### Gaps identified

- No unit test for the Python fvSolution generation block in `run-analysis.sh`; this plan adds one using `--dry-run` mode to extract the generated file without running OpenFOAM

### Evidence (embedded verification)

**Issue status** (verified 2026-08-26 via `gh issue view 3811`):
- `#3811` — OPEN — openfoam-analysis: SIMPLEC written with plain-SIMPLE relaxation, and p in the wrong sub-dictionary

**File existence** (`ls -la` 2026-08-26):
- EXISTS: `scripts/openfoam-analysis/run-analysis.sh`
- EXISTS: `scripts/openfoam-analysis/validate-analysis.py`
- EXISTS: `tests/openfoam/test_verify_openfoam_baseline.py`
- MISSING (new — this plan creates): `tests/openfoam/test_run_analysis_fvsolution.py`

**Line excerpts** (`sed -n 101,107p scripts/openfoam-analysis/run-analysis.sh` 2026-08-26):
```python
    if solver['application'] in ['simpleFoam']:
        f.write('SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }\n')
        relax = solver.get('relaxation', {})
        f.write('relaxationFactors { equations {\n')
        f.write(f'  U {relax.get("U", 0.7)}; p {relax.get("p", 0.3)};\n')
        f.write('} }\n')
```

**Gap proof** (`grep -n "run-analysis" tests/openfoam/test_verify_openfoam_baseline.py 2>/dev/null | wc -l` → 0 — confirms no existing test for run-analysis.sh fvSolution generation):
- `VERIFY_SCRIPT = REPO_ROOT / "scripts" / "openfoam" / "verify-openfoam-baseline.sh"` — test file targets a different script

**Reproduction proof**: N/A — this is a static code defect in the generated file content, not a runtime failure. The defect exists whenever `run-analysis.sh` is called with a `simpleFoam` solver; the generated `system/fvSolution` will contain contradictory `consistent yes` + `p 0.3` under `equations`.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-08-26-issue-3811-openfoam-simplec-relaxation-fix.md` |
| Fix target | `scripts/openfoam-analysis/run-analysis.sh` (lines 102–106) |
| New tests | `tests/openfoam/test_run_analysis_fvsolution.py` |
| Plan review — Claude | `scripts/review/results/2026-08-26-plan-3811-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-08-26-plan-3811-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-08-26-plan-3811-agy.md` |

---

## Deliverable

`scripts/openfoam-analysis/run-analysis.sh` will generate a correct SIMPLEC `fvSolution` block — no `p` entry under `equations`, default U relaxation 0.9 — backed by a unit test that parses the generated file without invoking the OpenFOAM solver.

---

## Files to Change

1. **`scripts/openfoam-analysis/run-analysis.sh`** — change lines 104–106 (the simpleFoam relaxation block):
   - Remove `p` from the `equations` sub-dictionary entirely (it belongs in `fields`, and SIMPLEC makes it unnecessary)
   - Change default U relaxation from 0.7 to 0.9 (appropriate for SIMPLEC)
   - Use the wildcard pattern `".*"` to apply to all equation relaxation factors, matching the corrected block from issue #3811

   Before:
   ```python
   f.write('relaxationFactors { equations {\n')
   f.write(f'  U {relax.get("U", 0.7)}; p {relax.get("p", 0.3)};\n')
   f.write('} }\n')
   ```

   After:
   ```python
   f.write('relaxationFactors { equations {\n')
   f.write(f'  ".*" {relax.get("U", 0.9)};\n')
   f.write('} }\n')
   ```

2. **`tests/openfoam/test_run_analysis_fvsolution.py`** (new file) — unit test that:
   - Creates a minimal `analysis.yaml` with `solver.application: simpleFoam`
   - Calls `run-analysis.sh --dry-run` against it
   - Reads the generated `system/fvSolution` from the output directory
   - Asserts: `consistent yes` is present, no `p` key appears under `equations`, `".*"` entry exists under `equations`

---

## TDD Test List

Red → green sequence:

1. **`test_fvsolution_no_p_in_equations`** — assert generated fvSolution does NOT contain `p` under `relaxationFactors.equations`; FAILS before fix (line 105 puts `p` there)

2. **`test_fvsolution_wildcard_relaxation_present`** — assert generated fvSolution contains `".*"` under `relaxationFactors.equations` with a value ≥ 0.8; FAILS before fix (wildcard absent)

3. **`test_fvsolution_consistent_yes_preserved`** — assert generated fvSolution contains `consistent yes` inside `SIMPLE { ... }`; PASSES before fix (this line is correct already), guards against regression

4. **`test_fvsolution_u_default_is_09`** — assert default U/wildcard relaxation is 0.9 when no `relaxation` key in YAML; FAILS before fix (default is 0.7)

5. **`test_fvsolution_custom_relaxation_honored`** — assert that a YAML with `solver.relaxation.U: 0.7` produces `".*" 0.7` (override respected); PASSES after fix, regression guard

---

## Acceptance Criteria

1. `tests/openfoam/test_run_analysis_fvsolution.py` — all 5 tests green (`uv run --with pytest python -m pytest tests/openfoam/test_run_analysis_fvsolution.py -v`)
2. `run-analysis.sh` with a simpleFoam analysis YAML generates `fvSolution` with no `p` key under `relaxationFactors.equations`
3. Default equation relaxation factor is `0.9` (not `0.7`)
4. `consistent yes` in `SIMPLE {}` block is unchanged
5. No regression in existing `tests/openfoam/test_verify_openfoam_baseline.py` (which covers unrelated scripts)

---

## Risks and Open Questions

- **Wildcard pattern quoting**: `".*"` must appear verbatim with quotes in the OpenFOAM dict file. The Python `f.write` must emit the quote characters. Low risk — straightforward string literal.
- **YAML `relaxation` key semantics**: the current code reads `relax.get("U", 0.7)` and `relax.get("p", 0.3)`. After fix, only `relax.get("U", 0.9)` is used (mapped to `".*"`). If any analysis YAML explicitly sets `relaxation.p`, that key will be silently ignored rather than placed in the `fields` sub-dictionary. **Decision**: drop `p` silently for now (SIMPLEC mode); if pressure relaxation override is ever needed, it should go under `fields` — that is a future enhancement, not in scope here.
- **`--dry-run` availability**: the test approach assumes `run-analysis.sh` can generate `system/fvSolution` without OpenFOAM installed. The script already has a `--dry-run` path (line 18–25 of the script) that exits early if OpenFOAM bashrc is missing when not in dry-run mode. Test must explicitly pass `--dry-run` to avoid OpenFOAM dependency in CI.
