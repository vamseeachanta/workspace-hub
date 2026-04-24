# Adversarial Review — Plan for Issue #501 (r2)

**Reviewer:** Claude (adversarial, defect-hunter, 2nd pass)
**Plan:** `docs/plans/2026-04-24-issue-501-orcawave-qtf-fieldpoints-irregfreq.md`
**Prior reviews:** `scripts/review/results/2026-04-24-plan-501-adversarial.md` (r1 MAJOR, 10 defects) + `scripts/review/results/2026-04-24-plan-501-claude.md` (2nd-pass MAJOR, 3 findings)
**Intel:** `/tmp/orca-batch-2026-04-24/intel-501.md`
**Date:** 2026-04-24

---

## Verdict

**MINOR** — r2 resolves every r1/2nd-pass critical defect by construction and the C1 cross-field validator is implementable as specified. However, r2 introduces two new path/evidence defects (paths relative to repo root miss the `digitalmodel/` prefix) and one mischaracterization ("L02 family" vs. a single spec.yml) that, left unfixed, will break the golden-capture helper the moment it runs. Fixes are one-line edits. No re-draft required.

---

## Prior-Defect Resolution Audit

### r1 adversarial defects (10)

| # | Defect (r1) | Status in r2 | Evidence |
|---|---|---|---|
| D1 | CRITICAL — Headings QTF crossing-angle emission gated by `qtf_calculation OR is_qtf`, not unconditional. | **RESOLVED** | r2 pseudocode L296-302 explicitly preserves `if spec.solver_options.qtf_calculation or is_qtf(spec) or qtf.enabled:` gate. New test `test_qtf_crossing_angle_not_emitted_when_qtf_disabled` (plan L398) makes the gate falsifiable. |
| D2 | CRITICAL — `_build_qtf_section` keyed on `solve_type`, not `qtf_calculation`; nested `QTFOptions.enabled=True` with non-QTF `solve_type` silently drops load-calc overrides. | **RESOLVED** | r2 retains the solve_type early-return gate (L306-307) AND adds a schema-level cross-field validator (L285-293) that raises `ValidationError` when `enabled=True` conflicts with `solve_type`. Plan explicitly chooses option (a) — raise — and surfaces the tradeoff for the user (L460). Three dedicated tests (`test_qtf_crossing_angle_not_emitted_when_solve_type_nonqtf`, `test_qtf_crossing_angle_not_emitted_when_qtf_disabled`, `test_qtf_enabled_raises_when_solve_type_nonqtf`) cover the three branches. |
| D3 | HIGH — `remove_irregular_frequencies` default-type change could break implicit back-compat. | **RESOLVED** | Pseudocode L222-224 spells out `None → interior_panels` default preservation. New test `test_remove_irregular_frequencies_legacy_unset` (plan L393) covers the unset-both-fields case. AC-D (plan L419) asserts no DeprecationWarning on the common legacy path. |
| D4 | HIGH — `DetectAndSkipFieldPointsInsideBodies` misdescription of current state. | **RESOLVED** | r2 explicitly notes the field does NOT currently exist on the schema (plan L42) and Sub-task 3 creates `OutputSpec.detect_field_points_inside_bodies: bool = True` (C2 fix). Two dedicated tests (`test_detect_field_points_inside_bodies_default_preserves_yes`, `test_detect_field_points_inside_bodies_false_renders_no`) assert byte-preservation. |
| D5 | MEDIUM — flat-to-nested QTF default-drift (int vs. float literals). | **RESOLVED** | `QTFOptions.min_crossing_angle: int = 0`, `max_crossing_angle: int = 180` (L254-255). Backend casts via `int(qtf.min_crossing_angle)` (L300-301). `test_qtf_crossing_angle_override` asserts int tokens. |
| D6 | MEDIUM — byte-identity golden-file source unnamed. | **RESOLVED** | Sub-task 0 names the golden directory (`digitalmodel/tests/hydrodynamics/diffraction/benchmarks/golden/`), the helper (`golden_capture.py`), and the naming convention (`{spec_path.parent.name}.yml`). Goldens are captured from pre-change tree before any schema edit. |
| D7 | MEDIUM — `_build_general_section` (L414-451) ignored as downstream QTF consumer. | **RESOLVED** | Pseudocode §Sub-task 2 re-routes `_build_general_section` through `resolved_qtf()` (L317-321). New test `test_build_general_section_unchanged_under_flat_compat` (plan L405). |
| D8 | LOW — `load_calculation_method` Literal mapping unverified vs. OrcaWave manual. | **RESOLVED** | L1 fix: `Literal["Direct", "Indirect", "Both"]` pass-through; caller supplies OrcaWave's own vocabulary. AC-E (plan L420) requires code-comment cite to the OrcaWave User Manual section. |
| D9 | LOW — `test_field_points_empty_unchanged` relies on unnamed golden. | **RESOLVED** | Absorbed into the Sub-task 0 golden corpus (explicit in C4 row). |
| D10 | LOW — `load_calculation_method` string-literal drift. | **RESOLVED** | Single canonical vocabulary (`Direct` / `Indirect` / `Both`) used throughout pseudocode + tests. |

### 2nd-pass Claude review (3 findings)

| # | Finding (2nd-pass) | Status in r2 | Evidence |
|---|---|---|---|
| 1 | `OutputSpec.detect_field_points_inside_bodies` does not exist on the schema. | **RESOLVED** | r2 Sub-task 3 creates the field (C2 row, plan L18); backend reads from it instead of hardcoding (pseudocode L341-343). |
| 2 | `tests/hydrodynamics/diffraction/benchmarks/` infrastructure does not exist. | **RESOLVED** | r2 Sub-task 0 creates `__init__.py`, `golden_capture.py`, `test_benchmark_infrastructure.py`, and the golden corpus; precursor test must pass on unmodified tree before Sub-task 1 begins (plan L19, L195-202, AC-A L416). |
| 3 | "L00 fixture" sub-spec enumeration ambiguous (10 sub-specs). | **RESOLVED** | r2 enumerates via `enumerate_byte_identity_fixtures()` helper with glob patterns; Byte-Identity Corpus section (plan L128-136) names L00 ×10 + L02 + L03. |

**Summary:** 10 r1 defects + 3 2nd-pass findings = **13/13 RESOLVED**. No PARTIAL, no UNRESOLVED.

---

## Pydantic v2 Cross-Field Validator Verification (C1 approach)

**Question:** Can the r2 cross-field validator actually see `solve_type` when declared on `SolverOptions`?

**Evidence from live code (`input_schemas.py:446-495`):**
```
class SolverOptions(BaseModel):
    solve_type: str = Field(default="potential_and_source", ...)   # line 449
    remove_irregular_frequencies: bool = ...                       # line 457
    qtf_calculation: bool = ...                                    # line 461
    ...
    qtf_min_frequency: Optional[float] = ...                       # line 488
```

**Critical finding:** `solve_type` lives on **`SolverOptions` itself**, NOT on `DiffractionSpec`. Therefore the r2 pseudocode at L288 — `solve_type = self.solve_type` — works directly. A `@model_validator(mode="after")` decorated method on `SolverOptions` has full access to all its own fields, including `solve_type`, `qtf_calculation`, `qtf` (the new nested model), and the flat `qtf_min/max_frequency`. This is the idiomatic Pydantic v2 pattern, and `input_schemas.py` already uses exactly this idiom at 4 locations (lines 230, 359, 420, 714).

**Minor imprecision in r2 plan:** pseudocode L288 reads `# or however SolverOptions references DiffractionSpec.solve_type` — this is a stale comment from when the r1 revision planner was uncertain about the parent-child relationship. The comment should be removed or corrected to `# self.solve_type — same model, no parent lookup needed`. This is a **documentation nit**, not a validator-design defect.

**Verdict on C1 approach:** **THE VALIDATOR WIRING WORKS AS SPECIFIED.** No Pydantic v2 mechanic contradicts the chosen approach. The existing `@model_validator(mode="after")` precedent in the same file proves the pattern is already idiomatic here.

---

## New Defects Introduced by r2

### N1 — [HIGH] Fixture paths are wrong: missing `digitalmodel/` repo prefix

**Location:** plan lines 51, 109, 131-134, 181-182, pseudocode L175-181, Files to Change row 0d.

**Plan claim:** `docs/domains/orcawave/L00_validation_wamit/` contains 10 sub-specs; `docs/domains/orcawave/L02_*/spec.yml`; `docs/domains/orcawave/L03_ship_benchmark/spec.yml`.

**Live tree (verified):**
```
$ ls /mnt/local-analysis/workspace-hub/docs/domains/orcawave/
ls: cannot access ...: No such file or directory

$ find /mnt/local-analysis/workspace-hub -path '*L00_validation_wamit*' -name 'spec.yml'
/mnt/local-analysis/workspace-hub/digitalmodel/docs/domains/orcawave/L00_validation_wamit/2.1/spec.yml
...<9 more>
```

The entire `docs/domains/orcawave/` tree lives under the **`digitalmodel/` sub-repo**, not at repo root. The r2 plan's pseudocode helper:
```python
root = repo_root / "docs/domains/orcawave"
```
will silently enumerate an empty list from the workspace-hub repo root. The helper would then write 0 golden files and the precursor test `test_benchmark_infrastructure_generates_golden_from_pre_change_tree` would vacuously pass (or fail with zero fixtures — depends on the assertion style). Either way, Sub-task 0's safety guarantee is nullified on the very first invocation.

**Required remediation:** Change every path reference from `docs/domains/orcawave/...` to `digitalmodel/docs/domains/orcawave/...` OR define `repo_root` in the helper as the `digitalmodel` sub-repo root (whichever is consistent with where the helper is invoked). Either way, AC-A's `uv run pytest` command at plan L416 is inside `cd digitalmodel`, so the helper's `repo_root` anchor must be stated.

### N2 — [MEDIUM] "L02 family" is overstated; L02 is a single spec.yml

**Location:** plan lines 133, 153, 165, 181, 367.

**Plan claim:** "L02 family" — implying multiple specs.

**Live tree (verified):**
```
$ find /mnt/local-analysis/workspace-hub/digitalmodel/docs/domains/orcawave -path '*L02*' -name 'spec.yml'
/mnt/local-analysis/workspace-hub/digitalmodel/docs/domains/orcawave/L02_barge_benchmark/spec.yml
```

Only **one** L02 spec.yml exists. The helper's glob `L02_*/spec.yml` will return a single path, so the parametrization degenerates silently, but the "family" framing suggests a broader corpus than exists. The `digitalmodel/docs/domains/orcawave/examples/L02 OC4 Semi-sub/` directory exists but does not contain a `spec.yml` at that level.

**Required remediation:** Replace "L02 family" with "L02 (`L02_barge_benchmark` — single spec)". Alternatively, broaden the glob to include `examples/` if additional L02 fixtures are in scope — but that would require an explicit enumeration decision.

### N3 — [LOW] Stale uncertainty comment in C1 validator pseudocode

**Location:** plan L288.

Pseudocode reads:
```
solve_type = self.solve_type   # or however SolverOptions references DiffractionSpec.solve_type
```
The "or however..." clause is a leftover from the revision-planning step when it was unclear whether `solve_type` lives on `SolverOptions` or `DiffractionSpec`. It's been verified (live code line 449) to live on `SolverOptions`. Stripping the comment removes reviewer-distraction and tightens the plan's authority.

**Required remediation:** Replace with `solve_type = self.solve_type   # lives on SolverOptions (line 449)`.

### N4 — [LOW] `DiffractionSpec.from_yaml(spec_path.read_text())` API unverified

**Location:** pseudocode L190, L200.

The `golden_capture.py` helper assumes `DiffractionSpec.from_yaml(text: str)` exists. Neither intel nor the plan names this as an existing method; if it's `DiffractionSpec.parse_yaml(path)` or a free function, the helper breaks. This is a new surface introduced by r2 (Sub-task 0) and should be grep-verified before landing.

**Required remediation:** Add one line to §Resource Intelligence Summary citing the actual loader API (e.g., `DiffractionSpec.from_yaml` at `input_schemas.py:<line>` or `load_spec_from_yaml(path)` at `<module>:<line>`). If the constructor pattern used by existing tests differs (common pattern is `yaml.safe_load` + `DiffractionSpec(**data)`), align the helper with it.

### N5 — [LOW] Golden-file naming collision risk for L00 numeric sub-dirs

**Location:** pseudocode L186.

`golden_path_for` returns `benchmarks/golden/{spec_path.parent.name}.yml`. L00 sub-specs live at `L00_validation_wamit/2.1/spec.yml`, `.../2.2/spec.yml`, etc. — so goldens become `2.1.yml`, `2.2.yml`, ..., `3.3.yml`. These filenames collide in name-space with L02 (`L02_barge_benchmark.yml`) and L03 (`L03_ship_benchmark.yml`) only by luck — any future fixture named `2.1` at another level would collide. Not a blocker, but a low-risk naming trap the plan should acknowledge.

**Required remediation:** Either (a) prefix goldens with the level tag — `L00_2.1.yml`, `L02_barge_benchmark.yml`, `L03_ship_benchmark.yml`; or (b) encode the full relative path — `L00_validation_wamit__2.1.yml`. Pick one and freeze it in Sub-task 0.

---

## Defect Checklist (standard)

| # | Class of check | Result |
|---|---|---|
| 1 | Scope drift into #500 runner territory | **PASS** — r2 preserves strict schema-lane scope (L79, L452). |
| 2 | Evidence gaps (paths + existence verified) | **FAIL — see N1, N2** — L00/L02/L03 paths miss `digitalmodel/` prefix; L02 mischaracterized. |
| 3 | TDD completeness (one test per new behavior, falsifiable) | **PASS** — 24 tests enumerated; each has concrete input + expected output. All r1 defects + 2nd-pass findings mapped to specific named tests. |
| 4 | Edge cases (empty fixture list, unset-both-fields, gate boundary) | **PASS** — `test_remove_irregular_frequencies_legacy_unset`, `test_qtf_crossing_angle_not_emitted_when_qtf_disabled`, `test_enumerate_byte_identity_fixtures_covers_l00_sub_specs` all present. |
| 5 | Coupling (no implicit dependencies on #500 or runner) | **PASS** — mesh-file existence explicitly deferred to #500 (plan L452); runner changes out of scope. |
| 6 | Past-tense / "already implemented" claims about proposed work | **PASS** — plan consistently uses "must be created", "does not exist", "r2 creates". |
| 7 | Self-labeling `status:plan-approved` in plan body | **PASS** — Adversarial Review Summary is placeholder (L437-441); Status is `draft`. |
| 8 | Plan-vs-intel alignment | **PARTIAL** — content aligned; paths are not. Intel uses `digitalmodel/src/digitalmodel/...` consistently; plan drops the `digitalmodel/` prefix for `docs/domains/orcawave/` only. |
| 9 | Complexity justification (T2) | **PASS** — four sub-tasks justified; benchmarks helper explicit. |
| 10 | Hard-forbidden self-approval language | **PASS** — residual-uncertainty section (L31) invites user approval on TRADEOFF C1 but does not self-approve. |
| 11 | Golden-file pre-change freezing | **PASS** — Sub-task 0 order enforced (L204); goldens captured from unmodified tree before any schema edit. |
| 12 | Pydantic v2 cross-field validator wiring correctness | **PASS** — verified `solve_type` lives on `SolverOptions` (line 449); `@model_validator(mode="after")` pattern already used 4 times in the same file. |
| 13 | Distinct-source attestation (≥6) | **PASS** — 18 sources enumerated at L126. |
| 14 | Acceptance criteria are executable commands | **PASS** — 8 `uv run pytest` lines runnable from `cd digitalmodel`. |
| 15 | Byte-identity gate mechanism explicit | **PASS** — AC-B enumerates `bytes(backend.render(spec)) == Path(golden_path_for(spec)).read_bytes()`; no numeric tolerance; token-level. |

---

## Specific Defects Found (consolidated list)

1. **[HIGH]** N1 — L00/L02/L03 fixture paths miss `digitalmodel/` prefix. **Fix:** rewrite all 4 path references in §Byte-Identity Corpus + pseudocode + Files to Change row 0d.
2. **[MEDIUM]** N2 — "L02 family" is a single `L02_barge_benchmark/spec.yml`; no family exists unless `examples/` is explicitly added. **Fix:** rename to "L02 (single spec)" and correct the corpus enumeration count from "L00 ×10 + L02 family + L03" to "L00 ×10 + L02 ×1 + L03 ×1 = 12 fixtures".
3. **[LOW]** N3 — stale uncertainty comment in C1 validator pseudocode (L288). **Fix:** replace with `# lives on SolverOptions (line 449)`.
4. **[LOW]** N4 — `DiffractionSpec.from_yaml(spec_path.read_text())` API unverified. **Fix:** one-line grep-verified citation of the actual loader API in §Resource Intelligence Summary.
5. **[LOW]** N5 — Golden-file naming for numeric L00 sub-dirs collides by luck. **Fix:** prefix goldens with level tag (`L00_2.1.yml`, `L02_barge_benchmark.yml`, `L03_ship_benchmark.yml`).

---

## Verdict Justification

**Why MINOR, not APPROVE:** r2 resolves every load-bearing defect from r1 + 2nd-pass (13/13 RESOLVED). The Pydantic v2 cross-field validator approach is verified-implementable — `solve_type` lives on `SolverOptions`, so `self.solve_type` just works, and the pattern is already used at 4 locations in the same file. The C1 three-layer defense (validator + `_build_headings_section` gate preservation + `_build_qtf_section` solve_type gate preservation) is internally consistent and the dedicated tests make each layer falsifiable.

However, the new defects N1 (wrong fixture paths) and N2 (mischaracterized L02) would break Sub-task 0 on its first invocation — the byte-identity gate is the plan's entire back-compat safety net, and the golden-capture helper would silently enumerate zero fixtures if run from the workspace-hub repo root. These are one-line fixes, not structural issues, so MINOR (not MAJOR): the plan's design is sound; its path evidence isn't.

**Why not MAJOR:** No r1 CRITICAL defect is PARTIAL or UNRESOLVED. The Pydantic v2 validator approach IS implementable. N1 is a find-and-replace across ~5 references; N2 is a word-swap. The plan can ship after a targeted path-correction pass — no re-planning, no scope change.

**Why not APPROVE:** N1 is a HIGH defect that, unfixed, nullifies Sub-task 0's safety guarantee. APPROVE requires zero new HIGH defects.

**Re-draft scope:** ~5 edits — fix path prefix in 4 locations, correct "L02 family" phrasing in 4 locations, drop the stale uncertainty comment, verify and cite the `DiffractionSpec` loader API, pick a golden-file naming convention.

---

## Critical findings summary (for Summary row)

r2 resolves 13/13 prior defects (all RESOLVED, none PARTIAL or UNRESOLVED); the Pydantic v2 cross-field validator approach works as specified because `solve_type` lives on `SolverOptions` itself (line 449) and `@model_validator(mode="after")` is already used 4× in the file. r2 introduces 1 HIGH + 1 MEDIUM + 3 LOW new defects, all around fixture-path evidence (`docs/domains/orcawave/` should be `digitalmodel/docs/domains/orcawave/`) and "L02 family" mischaracterization (single spec, not family). Fix the five items above and the plan is APPROVE-ready.
