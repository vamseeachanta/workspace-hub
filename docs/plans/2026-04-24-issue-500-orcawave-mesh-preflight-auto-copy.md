# Plan for #500: OrcaWave mesh file pre-flight validation + auto-copy in runner

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/500
> **Review artifacts:** scripts/review/results/2026-04-24-plan-500-claude.md | scripts/review/results/2026-04-24-plan-500-codex.md | scripts/review/results/2026-04-24-plan-500-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- **Found:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_runner.py:460-527` — `_copy_mesh_files(spec, output_dir, spec_dir=None)` already iterates bodies, damping lid, control surface, and free-surface zone and resolves relative paths against `spec_dir`. **Silently skips** sources that do not exist (line 483). This is the critical gap for strict preflight.
- **Found:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_runner.py:529-549` — `_validate_mesh_references(spec, output_dir)` already returns warning strings when expected meshes are absent from output_dir. Warn-only — no raise, no failed status. Gap: promotion to fail-fast.
- **Found:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_runner.py:246-288` — `prepare()` proceeds to `execute()` even when `error_message` is set. Gap: preflight gate with short-circuit.
- **Found:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_runner.py:89-108` — `RunConfig` Pydantic model already has `copy_mesh_files: bool = True`. Extension point: add `strict_preflight: bool` and basename-collision policy flag.
- **Found:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/spec_converter.py:130-171` — `SpecConverter.validate()` returns list-of-strings. Checks mesh_file non-empty but NOT existence, format match, symmetry consistency. Gap: this is where preflight lands.
- **Found:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py:237-266, 560-590` — backend writes `BodyMeshFileName` as `Path(...).name` (basename). Confirms auto-copy design and enumerates four mesh-consuming surfaces: body, control surface, damping lid, free-surface-zone.
- **Found:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py:47-48, 127-135, 551, 577-588` — `MeshFormatType` enum (GDF/DAT); `Geometry` model exposes `mesh_file`, `mesh_format`, `symmetry`; damping-lid and FSZ each have their own mesh_file.
- **Found:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/gmsh_mesh_builder.py:54-64` — `_build_gdf_header` authoritative reference for GDF header structure (header line + ULEN/GRAV + ISX/ISY + NPAN).
- **Found:** `digitalmodel/src/digitalmodel/solvers/orcawave/diffraction/scripts/validate_geometry.py:1-521` — sibling `GeometryValidator` CLI for STL/OBJ only. Flagged as follow-up consolidation — not in #500 scope.
- **Gap:** `_validate_mesh_files_exist()` method in `SpecConverter`; `strict_preflight` config flag; shallow GDF header parser; format-suffix mismatch check; symmetry-flag consistency check; basename-collision detection.

### Standards

| Standard | Status | Source |
|---|---|---|
| WAMIT v7 User Manual §3.1 (GDF format: ULEN/GRAV + ISX/ISY + NPAN + vertices) | gap (not ledgered) | `data/document-index/standards-transfer-ledger.yaml` (search for `wamit`/`gdf`/`orcawave` returns no entries) |
| Orcina `ImportMesh` behavior | gap (not ledgered) | same |

**Decision:** keep format validation shallow (header line count + numeric parse + symmetry-flag consistency) to avoid depending on an unregistered standard. Cite WAMIT §3.1 inline with gap caveat.

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/**` — searched for `OrcaWave`, `WAMIT`, `GDF`, `diffraction mesh`: no direct wiki pages. Only indirect sibling `leverette-sbm-drytreepanel.md` (unrelated). **Gap:** no wiki entry documents mesh-format matrix or path-resolution convention. Recommend follow-up seed (not blocking).

### Documents consulted

- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md` — establishes runner architecture; mentions "mesh path resolution" as runner responsibility but no preflight design.
- `docs/plans/2026-04-22-issue-2458-orcawave-multibody-benchmark-fixture.md` — multibody fixture work cross-references the same mesh-copy surface.
- `docs/plans/2026-04-23-issue-2457-orcawave-l03-ship-roundtrip-proof.md` — L03 roundtrip uses `prepare()` path; hit the silent-mesh-skip failure mode this plan fixes.
- `docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md` — batch dispatch parent; splits #500 (runner) from #501 (config schema).
- Related issue **#501** — config-schema additions for QTF/field-points/irregular-freq. Coupling flagged; NOT in #500 scope.

### Gaps identified

1. **Existence check** — runner silently skips missing meshes; `SpecConverter.validate()` has no existence check. Must raise or return structured error.
2. **Format-suffix sanity** — no check that file extension matches `geom.mesh_format` enum.
3. **GDF header validity** — no parse of ULEN/GRAV/ISX/ISY/NPAN.
4. **Symmetry-flag consistency** — no check that `geom.symmetry` matches GDF header ISX/ISY (silent-corruption class).
5. **Basename collisions** — `_copy_mesh_files` uses `output_dir / src.name`; two bodies referencing `hull.gdf` from different source dirs overwrite silently.
6. **`spec_dir=None` fallback** — silent CWD-relative resolution; callers may not always pass `spec_path`.
7. **No `strict_preflight` config flag** — policy not expressible.
8. **No negative-path tests** for missing mesh, format mismatch, symmetry mismatch, basename collision.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#500` — OPEN — "OrcaWave: mesh file pre-flight validation + auto-copy in runner"
- `#501` — OPEN — config-schema additions (sibling pod, out of scope here)

**File existence** (confirmed via intel reconnaissance 2026-04-24):
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_runner.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/spec_converter.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py`
- EXISTS: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_runner.py`
- EXISTS: `digitalmodel/tests/hydrodynamics/diffraction/test_spec_converter.py`
- MISSING (new — this plan creates): `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/mesh_preflight.py`

**Line excerpts** (from intel §"Relevant source files"):
```
orcawave_runner.py:483 — silent skip branch in _copy_mesh_files
orcawave_runner.py:529-549 — _validate_mesh_references warn-only
spec_converter.py:130-171 — validate() lacks file-existence check
input_schemas.py:47-48 — MeshFormatType enum {GDF, DAT}
```

**Gap proofs** (from intel §"Standards applicable" and §"Wiki pages applicable"):
- `data/document-index/standards-transfer-ledger.yaml` searched for `wamit|gdf|orcawave` → no entries → WAMIT §3.1 is ungrounded in ledger.
- `knowledge/wikis/marine-engineering/**` searched for `OrcaWave|WAMIT|GDF|diffraction mesh` → no direct pages.

Source count: issue body (1) + intel file with ~10 file-path citations (2) + prior plans x4 (3-6) + standards ledger (7) + wiki tree (8). Well above the 3-source minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-500-orcawave-mesh-preflight-auto-copy.md |
| Tests (runner) | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_runner.py` |
| Tests (converter) | `digitalmodel/tests/hydrodynamics/diffraction/test_spec_converter.py` |
| Tests (preflight unit) | `digitalmodel/tests/hydrodynamics/diffraction/test_mesh_preflight.py` (new) |
| Implementation (new module) | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/mesh_preflight.py` |
| Implementation (edit) | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_runner.py` |
| Implementation (edit) | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/spec_converter.py` |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-500-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-500-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-500-gemini.md |
| Docs update | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_runner.py` docstring (path-resolution convention) |

---

## Deliverable

A strict, fail-fast mesh preflight gate in `OrcaWaveRunner.prepare()` and `SpecConverter.validate()` — existence, format-suffix, shallow GDF header, and symmetry-flag-consistency checks across all four mesh-consuming surfaces (body, control surface, damping lid, free-surface zone), with a `strict_preflight` config flag (default strict), a basename-collision policy flag, and full negative-path test coverage. No config-schema changes (those are #501).

---

## Pseudocode

```
# mesh_preflight.py (new module under hydrodynamics/diffraction/)

MESH_SURFACE_ITER(spec):
    yield every (surface_kind, mesh_file_str, mesh_format, symmetry_or_none) tuple
    across bodies[].vessel.geometry, control_surface, damping_lid, free_surface_zone
    — this is the registry/iterator pattern so #501's 5th surface auto-registers.

validate_mesh_exists(mesh_file_str, spec_dir) -> Path | raises FileNotFoundError:
    if spec_dir is None: raise ValueError("spec_dir required for strict preflight")
    resolved = (spec_dir / mesh_file_str).resolve()
    if not resolved.is_file(): raise FileNotFoundError(resolved)
    return resolved

validate_format_suffix(resolved_path, declared_format) -> None | raises ValueError:
    ext = resolved_path.suffix.lower().lstrip(".")
    if ext not in {"gdf", "dat"}: return warning(unknown_format)  # warn, not raise
    if ext != declared_format.value.lower(): raise ValueError(f"suffix {ext} ≠ declared {declared_format}")

parse_gdf_header(resolved_path) -> GdfHeader:
    read first 5 non-empty lines; expect
      line1: header comment
      line2: ULEN GRAV (two floats)
      line3: ISX ISY (two 0/1 ints)
      line4: NPAN (positive int)
    return GdfHeader(ulen, grav, isx, isy, npan); raise ValueError on parse fail.

validate_symmetry_consistency(header, declared_symmetry) -> None | raises ValueError:
    expected_isx, expected_isy = SYMMETRY_MAP[declared_symmetry]
    if (header.isx, header.isy) != (expected_isx, expected_isy):
        raise ValueError(f"GDF ISX/ISY {(header.isx, header.isy)} ≠ declared {declared_symmetry}")

validate_panel_count(npan, min=50, max=50_000) -> Warning | None:
    return warning if out of range; never raise (advisory).

detect_basename_collisions(resolved_paths) -> dict[basename, list[Path]]:
    group by .name; any group with >1 distinct resolved path is a collision.

# SpecConverter.validate() extension (spec_converter.py)

def _validate_mesh_files(self, spec, spec_dir) -> list[str]:
    issues = []
    for surface in MESH_SURFACE_ITER(spec):
        try:
            resolved = validate_mesh_exists(surface.mesh_file, spec_dir)
            validate_format_suffix(resolved, surface.format)
            if resolved.suffix.lower() == ".gdf":
                header = parse_gdf_header(resolved)
                if surface.symmetry is not None:
                    validate_symmetry_consistency(header, surface.symmetry)
                warn = validate_panel_count(header.npan)
                if warn: issues.append(warn)  # warning goes to issues list
        except (FileNotFoundError, ValueError) as e:
            issues.append(f"{surface.kind}: {e}")
    collisions = detect_basename_collisions(...)
    if collisions: issues.append(f"basename collision: {collisions}")
    return issues

# RunConfig extension (orcawave_runner.py)

class RunConfig:
    copy_mesh_files: bool = True                    # existing
    strict_preflight: bool = True                   # NEW — fail-fast default
    basename_collision_policy: Literal["error","overwrite","suffix"] = "error"  # NEW

# prepare() extension (orcawave_runner.py)

def prepare(self):
    ...  # existing input-file generation
    if self.config.strict_preflight:
        issues = self._spec_converter.validate_with_preflight(spec, spec_dir)
        if issues:
            self._result.status = FAILED
            self._result.error_message = "\n".join(issues)
            return self._result  # SHORT-CIRCUIT — do not proceed to execute
    if self.config.copy_mesh_files:
        self._copy_mesh_files(spec, output_dir, spec_dir)  # now raises on missing unless strict=False
    ...
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/mesh_preflight.py` | new helpers: `MESH_SURFACE_ITER`, `validate_mesh_exists`, `validate_format_suffix`, `parse_gdf_header`, `validate_symmetry_consistency`, `validate_panel_count`, `detect_basename_collisions` |
| Create | `digitalmodel/tests/hydrodynamics/diffraction/test_mesh_preflight.py` | unit tests for each preflight helper |
| Modify | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/spec_converter.py` | add `_validate_mesh_files(spec, spec_dir)`; extend `validate()` entry; add `validate_with_preflight(spec, spec_dir)` |
| Modify | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_runner.py` | add `strict_preflight` + `basename_collision_policy` to `RunConfig`; promote `_validate_mesh_references` to raise under strict; add short-circuit in `prepare()`; raise `FileNotFoundError` in `_copy_mesh_files` under strict; enforce collision policy; add path-resolution docstring |
| Modify | `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_runner.py` | add negative-path tests (missing mesh, format mismatch, symmetry mismatch, basename collision); warn-mode non-fatal test |
| Modify | `digitalmodel/tests/hydrodynamics/diffraction/test_spec_converter.py` | add negative-path validate() tests with tmp_path specs |
| Update | docs/plans/README.md | add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_validate_mesh_exists_happy | existing file resolves | tmp spec_dir + real mesh file | returns resolved Path |
| test_validate_mesh_exists_missing_raises | missing mesh raises | tmp spec_dir + non-existent mesh | FileNotFoundError |
| test_validate_mesh_exists_none_spec_dir_raises | spec_dir=None rejects under strict | spec_dir=None | ValueError |
| test_validate_format_suffix_match | .gdf + GDF passes | (path.gdf, GDF) | no raise |
| test_validate_format_suffix_mismatch | .dat + GDF raises | (path.dat, GDF) | ValueError |
| test_parse_gdf_header_valid | parses sample 4-line header | synthetic GDF | GdfHeader with correct NPAN |
| test_parse_gdf_header_malformed | raises on bad header | truncated file | ValueError |
| test_validate_symmetry_consistency_match | XZ symmetry + ISX=1 passes | declared=XZ, header.isx=1 | no raise |
| test_validate_symmetry_consistency_mismatch | XZ + ISX=0 raises | declared=XZ, header.isx=0 | ValueError |
| test_validate_panel_count_in_range | 100 panels → no warning | npan=100 | None |
| test_validate_panel_count_under | 10 panels → warning | npan=10 | warning string |
| test_validate_panel_count_over | 100000 panels → warning | npan=100000 | warning string |
| test_detect_basename_collisions_none | unique basenames | [a/hull.gdf, b/lid.gdf] | empty dict |
| test_detect_basename_collisions_found | duplicate basename | [a/hull.gdf, b/hull.gdf] | collision dict |
| test_spec_converter_validate_missing_mesh | validate returns issue on missing | tmp spec w/ bad mesh_file | issue in list |
| test_spec_converter_validate_format_mismatch | validate catches .dat vs GDF | tmp spec mismatched | issue in list |
| test_runner_prepare_strict_fails_fast | strict=True short-circuits | spec with missing mesh | result.status=FAILED, no execute() call |
| test_runner_prepare_warn_mode_proceeds | strict=False logs and proceeds | spec with missing mesh | result.status=PREPARING, error_message set |
| test_runner_prepare_basename_collision_error | collision_policy=error raises | multibody sharing basename | ValueError |
| test_runner_prepare_basename_collision_suffix | collision_policy=suffix renames | multibody sharing basename | two distinct dest files |
| test_runner_prepare_damping_lid_mesh_copied | lid mesh covered | spec with damping lid | lid mesh in output_dir |
| test_runner_prepare_fsz_mesh_copied | FSZ mesh covered | spec with FSZ | FSZ mesh in output_dir |
| test_runner_prepare_multibody_preflight_all_surfaces | iterator covers all 4 | multibody + lid + cs + fsz | all 4 resolved |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest digitalmodel/tests/hydrodynamics/diffraction/ -v`
- [ ] No regression: `uv run pytest digitalmodel/` passes
- [ ] Strict-mode default: `RunConfig()` with no args has `strict_preflight=True`
- [ ] Backward compat: existing tests in `test_orcawave_runner.py:189-233` still pass with new strict default (fixtures point at real meshes)
- [ ] Path-resolution convention documented in `orcawave_runner.py` module docstring: mesh paths are relative to spec.yml
- [ ] `spec_dir=None` with `strict_preflight=True` raises `ValueError` (no silent CWD fallback)
- [ ] Basename-collision policy defaults to `error` (fail-loud); `suffix` and `overwrite` available
- [ ] #501 coupling noted in code comment but no #501 schema fields touched
- [ ] Review artifacts posted to scripts/review/results/

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE / MINOR / MAJOR | (pending) |
| Codex | APPROVE / MINOR / MAJOR | (pending) |
| Gemini | APPROVE / MINOR / MAJOR | (pending) |

**Overall result:** PENDING

Revisions made based on review:
- (pending)

---

## Risks and Open Questions

- **[TRADEOFF FOR USER] Strict-vs-warn default on missing mesh.** Options: (A) `strict_preflight=True` default — fail-fast; existing CI gains signal but any caller currently relying on silent-skip-and-continue (e.g., L03 roundtrip partial-artifact inspection) breaks. (B) `strict_preflight=False` default — preserves current behavior; callers must opt-in to strict. **Recommendation:** (A) strict=True default. Every in-tree fixture points at real meshes; negative-path callers are bugs we want to surface. User must confirm before implementation.

- **[TRADEOFF FOR USER] Basename-collision policy.** Options: (A) `error` — raise on any two bodies with the same mesh basename from different source dirs; safest, loudest. (B) `overwrite` — current silent behavior; risk of wrong-answer silent corruption. (C) `suffix` — auto-rename dest to `{stem}_{body_index}{ext}`; preserves both files but mutates `BodyMeshFileName` writes in backend and requires downstream reference rewrite. **Recommendation:** (A) `error` default with (C) `suffix` available as opt-in. User must confirm; (C) is more invasive because it touches backend reference emission.

- **[TRADEOFF FOR USER] Format/symmetry check strictness.** Options: (A) block unknown formats (anything ≠ `.gdf`/`.dat`) — strictest; rejects future-valid formats OrcaWave may add. (B) warn-only on unknown format; raise only on suffix-vs-declared-format mismatch and on symmetry-flag-vs-GDF-header mismatch. (C) full permissive — only existence check, no format/header validation. **Recommendation:** (B) — raise on declared-vs-actual mismatches (these are the silent-corruption class); warn-only on unknown extensions (forward compat). User must confirm.

- **Risk — licensed-win-1 path divergence:** preflight runs on linux CI but solver runs on win-1 via OrcFxAPI. `C:\Meshes\hull.gdf` existence check fails on linux even though solver succeeds on win-1. **Mitigation:** make preflight advisory (warn-only) when `spec_dir` resolves to a path with drive letter or `\` separators on non-Windows; add `platform_check: str` to `RunResult` surfacing which platform ran the check. This is NOT a user tradeoff — it is a correctness requirement for cross-platform specs.

- **Risk — cross-issue coupling to #501:** #501 may add a 5th mesh-consuming surface (e.g., field-points). `MESH_SURFACE_ITER` iterator pattern mitigates — #501's new surface registers via the iterator without #500 revision. Coupling flagged in code comment; no schema changes in #500.

- **Risk — `validate_geometry.py` duplication:** sibling STL/OBJ validator lives in `solvers/orcawave/diffraction/scripts/`. This plan creates a NEW `mesh_preflight.py` under `hydrodynamics/diffraction/` for scope-locality and format-disjointness (GDF/DAT vs. STL/OBJ). Consolidation is flagged as follow-up — NOT in #500 scope.

- **Risk — fixture mutation:** negative-path tests must use `tmp_path`-built specs with deliberately missing mesh files. Do NOT delete or mutate `ship_raos_spec_path` / `fpso_turret_spec_path` shared fixtures.

- **Open:** should the shallow GDF header parser also cross-check that the vertex-line count equals `4 * NPAN`? Adds ~15 LOC; catches truncated files. Recommend yes (test: `test_parse_gdf_header_truncated`). Flag for user confirmation.

---

## Complexity: T2

**T2** — extension of existing scaffolding, not greenfield. One new module (`mesh_preflight.py`), two existing files modified (`orcawave_runner.py`, `spec_converter.py`), one new test file plus extensions to two existing test files. Net-new code ~250-350 LOC + ~120 LOC test code. The load-bearing complexity is the three user-tradeoff decisions (strict-vs-warn default, basename-collision policy, format-strictness) — these must be locked in the approval gate before implementation. Not T1 because three design decisions are load-bearing; not T3 because no new subsystem, no cross-repo coupling, no config-schema work (that's #501).
