# Adversarial Review — Plan for Issue #500 (OrcaWave mesh preflight + auto-copy)

> **Reviewer stance:** defect-hunter. Charitable reading forbidden. Every ambiguity = defect.
> **Plan reviewed:** `docs/plans/2026-04-24-issue-500-orcawave-mesh-preflight-auto-copy.md`
> **Intel:** `/tmp/orca-batch-2026-04-24/intel-500.md`
> **Issue JSON:** `/tmp/orca-batch-2026-04-24/issue-500.json`
> **Date:** 2026-04-24

---

## Verdict: **MINOR**

Plan is structurally sound and correctly acknowledges the pre-existing `_copy_mesh_files` / `_validate_mesh_references` scaffolding (explicit "not greenfield" framing in Resource Intelligence §Found). All three load-bearing tradeoffs surfaced with explicit recommendations. Scope fence vs #501 is stated in prose AND in an acceptance-criteria line. However, multiple concrete defects that will bite during implementation — specification ambiguities, contradictions between pseudocode and acceptance criteria, and one silent-corruption hazard the plan itself introduces via the `suffix` collision policy. Plan is APPROVE-able after MINOR revisions.

---

## Defect checklist (full sweep)

| # | Category | Status | Notes |
|---|---|---|---|
| 1 | Acknowledges existing `_copy_mesh_files` (lines 460-527) | PASS | Cited explicitly with line refs in RI §1 |
| 2 | Acknowledges existing `_validate_mesh_references` (lines 529-549) | PASS | Cited with "warn-only" gap in RI §2 |
| 3 | Greenfield framing avoided | PASS | "extension of existing scaffolding, not greenfield" in §Complexity |
| 4 | Three tradeoffs explicitly addressed | PASS | §Risks lists strict-vs-warn, basename collision, format strictness with [TRADEOFF FOR USER] tags + recommendations |
| 5 | Scope fenced from #501 | PASS | Stated in §Deliverable AND acceptance-criteria line |
| 6 | Resource intel citations ≥ 3 | PASS | 8 sources cited |
| 7 | Artifact map complete | PASS | |
| 8 | TDD list complete | PARTIAL | See Defects D1, D5 below |
| 9 | Acceptance criteria testable | PARTIAL | See Defect D2 |
| 10 | Pseudocode consistent with text | FAIL | See Defect D3 |
| 11 | Licensed-win-1 cross-platform handled | PARTIAL | See Defect D4 |
| 12 | No config-schema drift | PASS | RunConfig additions are runner config (Pydantic `RunConfig`), not spec schema |
| 13 | Test fixtures protected | PASS | Explicit "do NOT mutate shared fixtures" in risks |
| 14 | Negative-path coverage | PARTIAL | See Defect D5 |
| 15 | Basename-collision `suffix` policy downstream consistency | FAIL | See Defect D6 (silent-corruption hazard) |
| 16 | `spec_dir=None` semantics under `strict=False` | FAIL | See Defect D7 |
| 17 | `validate_panel_count` thresholds config-overridable | FAIL | See Defect D8 |
| 18 | GDF vertex-row count check resolved | FAIL | See Defect D9 (open question left unresolved) |
| 19 | `validate_with_preflight` API surface defined | PARTIAL | See Defect D10 |
| 20 | DAT format validation | FAIL | See Defect D11 |

---

## Specific defects

### D1 — FAIL — MESH_SURFACE_ITER pseudocode ≠ acceptance criteria (load-bearing)

Pseudocode line 118-120 says the iterator yields tuples for bodies, control_surface, damping_lid, free_surface_zone — but TDD list `test_runner_prepare_multibody_preflight_all_surfaces` is described as "multibody + lid + cs + fsz → all 4 resolved". The iterator is supposed to be extensible for #501's 5th surface (field-points). There is no test that asserts the iterator is extensible — no `test_mesh_surface_iter_registry_pattern` or similar. Claim "#501's 5th surface auto-registers" (§Risks) is unsubstantiated without a registry test. Either drop the extensibility claim, or add a test that exercises the registry with a synthetic surface.

### D2 — FAIL — Acceptance criterion "Backward compat: existing tests still pass with new strict default" is un-runnable as written

The acceptance criterion says "existing tests in `test_orcawave_runner.py:189-233` still pass with new strict default (fixtures point at real meshes)". But the plan never verifies that the shared fixtures `ship_raos_spec_path` and `fpso_turret_spec_path` actually point at extant meshes under `spec_dir` resolution — intel says they "point at real mesh files that exist on-disk (confirmed by passing tests)" but the passing tests today do NOT do strict-mode resolution. Under the new strict default, the `spec_dir` passed into `prepare()` must be the directory containing the spec.yml. If any existing test calls `prepare()` without passing `spec_path`, the new `spec_dir=None + strict_preflight=True → ValueError` rule breaks that test. Plan must enumerate which existing call sites pass `spec_path` and which don't, then either (a) backfill `spec_path` in those tests or (b) default fallback for test contexts. This check is missing and is the single most likely post-implementation regression.

### D3 — FAIL — Pseudocode contradicts itself on strict/warn mode behavior in `_copy_mesh_files`

Line 191: `self._copy_mesh_files(spec, output_dir, spec_dir)  # now raises on missing unless strict=False`. But line 184-189 shows the strict-mode path already short-circuits via `validate_with_preflight` BEFORE reaching `_copy_mesh_files` — so by the time control gets to line 191, strict mode has already gated on missing meshes. The "`now raises on missing unless strict=False`" comment implies `_copy_mesh_files` itself raises under strict, which is redundant with the earlier short-circuit AND means under `strict=False`, `_copy_mesh_files` silently skips (restoring the bug). Specify: under `strict=False`, does `_copy_mesh_files` still silently skip, or does it warn? Plan is silent. Recommend: warn-log on skip when `strict=False`, raise when `strict=True` AND preflight was somehow bypassed (defense in depth).

### D4 — PARTIAL — Cross-platform path risk "mitigation" is under-specified

§Risks line 280: "make preflight advisory (warn-only) when `spec_dir` resolves to a path with drive letter or `\` separators on non-Windows". What is the detection heuristic? `re.match(r'^[A-Za-z]:', str(path))`? What about UNC paths (`\\server\share`)? What if a linux-CI spec has a legitimate `\` in a filename (unlikely but legal)? No pseudocode for the cross-platform detector. No test listed for `test_preflight_cross_platform_advisory`. Acceptance criteria doesn't mention the `platform_check: str` field in `RunResult`. This is a correctness requirement per intel line 68, but plan treats it as a footnote.

### D5 — PARTIAL — Negative tests missing for damping-lid and FSZ surfaces

TDD list has `test_runner_prepare_damping_lid_mesh_copied` and `test_runner_prepare_fsz_mesh_copied` — these are HAPPY-PATH tests ("mesh covered"). No negative-path tests for missing damping-lid mesh or missing FSZ mesh. Intel §Existing tests line 29 explicitly calls out "No test for damping-lid/CS/FSZ mesh resolution or copy" as a gap. Plan only adds missing-mesh negative tests for body surface (`test_runner_prepare_strict_fails_fast` — uses spec with missing body mesh). Add `test_runner_prepare_strict_fails_on_missing_damping_lid_mesh` and `test_runner_prepare_strict_fails_on_missing_fsz_mesh`.

### D6 — FAIL — `basename_collision_policy="suffix"` introduces a silent-corruption hazard downstream

Per plan (§Risks line 276): "(C) `suffix` — auto-rename dest to `{stem}_{body_index}{ext}`; preserves both files but mutates `BodyMeshFileName` writes in backend and requires downstream reference rewrite."

The backend (`orcawave_backend.py:237-266`) emits `BodyMeshFileName` via `Path(mesh_file).name` — i.e., the ORIGINAL basename. If `_copy_mesh_files` renames the destination to `hull_0.gdf` / `hull_1.gdf` but the backend still emits `BodyMeshFileName: hull.gdf`, OrcaWave will fail to find the file (or find only one copy, silently using the wrong one for body 1 vs body 0). This is the exact "silent corruption" class the plan sets out to prevent. Plan acknowledges "requires downstream reference rewrite" but does NOT list `orcawave_backend.py` in Files-to-Change. No test for `test_runner_prepare_basename_collision_suffix` actually verifies the backend-emitted `BodyMeshFileName` references the renamed file. This is a **correctness defect in the `suffix` policy itself** that gets checked in as a supported option.

Recommendations:
- Either (a) add `orcawave_backend.py` to Files-to-Change with a `mesh_file_override` dict plumbed through, OR
- (b) Drop `suffix` as a supported policy in v1 — leave only `error` and `overwrite` until #501 settles schema — OR
- (c) Explicitly document `suffix` as "future option — not implemented in #500" in RunConfig.

### D7 — FAIL — `spec_dir=None` under `strict_preflight=False` behavior unspecified

Pseudocode (line 124): `if spec_dir is None: raise ValueError("spec_dir required for strict preflight")` — but this is INSIDE `validate_mesh_exists`, which is only called under strict mode. What about `spec_dir=None` under `strict_preflight=False`? Does `_copy_mesh_files` still fall through to `Path(mesh_file_str)` (CWD-relative), preserving the current bug? Plan recommends (line 274) that default is `strict=True`, so this case seems edge — but intel line 62 specifically calls this out as a gap: "Planner must either make `spec_path` required when `copy_mesh_files=True` OR document the CWD fallback explicitly." Plan did neither. Acceptance criterion line 248 only covers the strict case.

### D8 — FAIL — Panel-count thresholds not config-overridable despite intel requirement

Intel line 56: "Threshold values should be config-overridable." Plan hardcodes `min=50, max=50_000` in pseudocode (line 147) with no config surface for override. If a user has a legitimately tiny debug mesh (20 panels) or a high-fidelity mesh (80_000 panels), they cannot suppress the warnings. Either add `panel_count_min: int = 50` + `panel_count_max: int = 50_000` to RunConfig, or document that advisory warnings are non-silenceable (and test that the warning doesn't escalate).

### D9 — FAIL — Open question about `4 * NPAN` vertex-row check left unresolved

Line 288: "Open: should the shallow GDF header parser also cross-check that the vertex-line count equals `4 * NPAN`?". This is an open question for the USER, not the reviewer. Plans must not ship with unresolved open questions that affect scope. Per `issue-planning-mode` skill, unresolved design questions block `status:plan-approved`. Plan author must pick: include the check (adds test `test_parse_gdf_header_truncated`) or explicitly defer to follow-up.

### D10 — PARTIAL — `SpecConverter.validate_with_preflight(spec, spec_dir)` signature under-specified

Files-to-Change line 203: "add `validate_with_preflight(spec, spec_dir)`". But §Pseudocode line 185 calls `self._spec_converter.validate_with_preflight(spec, spec_dir)` as if it's a method on the runner's converter instance. Is this a new public method? Does it return the same `list[str]` as `validate()`, or does it raise? Does `validate()` itself call the new `_validate_mesh_files`, or is that only via `validate_with_preflight`? The relationship between the existing `validate()` (which current callers use — intel §Existing tests line 30) and the new `validate_with_preflight()` is ambiguous. Recommend: specify that `validate()` remains as-is (return list[str], no raise) and `validate_with_preflight()` is additive with the same contract; do NOT change `validate()` semantics — protects existing callers.

### D11 — FAIL — DAT format validation is absent

Pseudocode line 132: `if ext not in {"gdf", "dat"}: return warning(unknown_format)` — but there is NO `parse_dat_header` or any `.dat` format check beyond suffix. Intel line 55 mentions DAT as a valid `MeshFormatType` enum member. Plan's Gap §2 says "Format-suffix sanity" but §3 says "GDF header validity" only — DAT is unvalidated. Is that acceptable? Orcina/WAMIT DAT files have their own structure (OrcaWave-native panelled form). Either explicitly document "DAT validation: suffix only, content opaque" as a deliberate scope decision, or add a DAT check. Current plan leaves a half-preflight for one of the two supported formats.

---

## Other minor nits (not blocking, but worth tightening)

- N1: §Pseudocode line 166: `if warn: issues.append(warn)  # warning goes to issues list` — conflates warnings with errors in the same list. Callers can't distinguish. Consider `dict {"warnings": [...], "errors": [...]}` or sentinel prefix.
- N2: §Risks line 284: mention of `validate_geometry.py` duplication correctly flagged as out-of-scope, but plan should file a follow-up issue number (or note "file before close") to make the follow-up concrete.
- N3: §Deliverable line 109 says "default strict" but §Acceptance Criteria line 246 requires `RunConfig()` with no args has `strict_preflight=True` — consistent, good. But there is no acceptance criterion for `basename_collision_policy` default — add "defaults to `error`" check.
- N4: Plan mentions `SYMMETRY_MAP` in pseudocode (line 143) but never defines its keys. Is the mapping `{"none": (0,0), "XZ": (1,0), "YZ": (0,1), "XZ_YZ": (1,1)}`? Confirm against `SymmetryType` enum in `input_schemas.py` (not cited in plan).
- N5: Artifact Map line 103: "Docs update — docstring" is listed under a file that is ALSO listed under Modify. Dedup the row or mark it as the same edit.

---

## Justification for MINOR (not APPROVE, not MAJOR)

**Not APPROVE** because:
- D2 (backward-compat acceptance criterion un-runnable) is a pre-implementation gap that will cause test regressions on first run.
- D6 (`suffix` collision policy is itself a silent-corruption hazard) is a correctness defect the plan introduces as a supported option — this must be resolved before implementation begins.
- D9 (unresolved open question about vertex-row check) blocks `status:plan-approved` per workflow rules.
- D11 (DAT format left unvalidated) contradicts the Deliverable claim "across all four mesh-consuming surfaces" — if one of two formats is silently passed through, the preflight is incomplete.

**Not MAJOR** because:
- All three load-bearing tradeoffs ARE surfaced with recommendations (strict-vs-warn, basename collision, format strictness) — the plan did not duck the hard decisions.
- Resource intelligence is strong: existing code is acknowledged with line ranges, not treated as greenfield.
- Scope fence vs #501 is explicit and redundantly stated.
- The defects are specification gaps and inconsistencies, not structural misalignment with the issue or the codebase. Fixable in a single revision pass.

**Recommendation:** author addresses D1–D11 + picks a lane for D9 + tightens N1–N5, then re-request approval. Estimate: 45-90 min of plan-revision work, no code changes.

---

## Verdict summary

- **Verdict:** MINOR
- **Defect count:** 11 specific defects (4 FAIL, 4 PARTIAL, 3 PASS-with-nit) + 5 minor nits
- **Critical finding:** `basename_collision_policy="suffix"` would silently desync `BodyMeshFileName` in `orcawave_backend.py` from renamed destination files — reintroduces the exact silent-corruption class the plan claims to prevent, and `orcawave_backend.py` is not listed in Files-to-Change (D6).
