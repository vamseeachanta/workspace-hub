# On-Bottom Stability Unification Investigation

**Issue:** [#2694](https://github.com/vamseeachanta/workspace-hub/issues/2694) — Cross-domain
duplicate-implementation cleanup epic. Originating finding: [#2692](https://github.com/vamseeachanta/workspace-hub/issues/2692)
Pipelines R5, §5 Finding 1.
**Investigator:** Claude (read-only recon, 2026-05-13)
**Status:** Findings only — no code changes, no commits.

## Executive Summary

The R5 audit identified two DNV-RP-F109 on-bottom stability implementations in `digitalmodel`.
Both are **distinct, live code** (different md5, different shapes, different formulas). The
R5 finding misclassified the test situation: the "empty" file is **not** `tests/test_on_bottom_stability.py`
(which has **14 functional tests**), but `tests/subsea/pipeline/test_on_bottom_stability.py`
(which has 215 lines of tests but imports from a **module that doesn't exist** —
`digitalmodel.subsea.pipeline.on_bottom_stability` is not in the source tree at all). That
test file is silently excluded by `tests/conftest.py:19` in `collect_ignore`.

**Critical numerical finding:** the two implementations use DIFFERENT FORMULAS while both
claiming "DNV-RP-F109". On a borderline scenario (W_s=500, F_H=183, F_L=150, μ=0.6) the
subsea impl reports `utilisation=1.000, is_stable=False` while the geotechnical impl reports
`utilisation=0.957, is_stable=True`. **Same physical scenario, opposite verdicts at the
design margin.** This is the silent-numerical-drift hazard #2694 warned about.

The cleanest path is to canonicalize on `digitalmodel.subsea.on_bottom_stability` (correctly
implements both DNV-RP-F109 §4.3.1 absolute AND §4.3.2 generalized methods with the right
formulas, has a `manifest.yaml`, has 20 well-grounded tests with clause/equation references)
and migrate or delete the geotechnical copy (mislabelled formula, no callers, separate kN
wrappers worth porting forward).

## Implementations

| # | File (relative to `digitalmodel/`) | md5 | Lines | Shape | Algorithm | Standards in docstring |
|---|---|---|---|---|---|---|
| 1 | `src/digitalmodel/subsea/on_bottom_stability/dnv_rp_f109.py` | `a7551810982ea7650dfbd9860994cadb` | 317 | `NamedTuple` (`StabilityResult`) | Absolute Eq 4.1 + Generalized Eq 4.5 (§4.3.1 + §4.3.2) | **DNV-RP-F109 (Edition Oct 2021)** with §3.2.1 Eq 3.1/3.2, §2.2, §4.3.1 Eq 4.1, §4.3.2 Eq 4.5, Tables 3-3 / 4-1 clause refs |
| 2 | `src/digitalmodel/geotechnical/on_bottom_stability.py` | `404fad7577cd7e0450c5ba625fe4c879` | 337 | `@dataclass` (4 result types) | "Simplified" (Eq 4.5 form with F_R=0); plus kN wrappers + vertical-stability check | DNV-RP-F109 (no edition, no clause refs in docstrings) |

> **Not byte-identical** (unlike 3 of the 7 catenary files in #2686 finding #1). These are
> genuinely separate codebases with different defaults, different return types, and different
> default formulas masquerading under the same standard name.

## Public-Surface Comparison

**Impl 1 (`subsea/on_bottom_stability/dnv_rp_f109.py`):**

| Symbol | Signature | Clause |
|---|---|---|
| `StabilityResult` | `NamedTuple(utilisation: float, is_stable: bool, details: dict)` | — |
| `C_D_SMOOTH/C_L_SMOOTH/C_M_SMOOTH` | `0.9 / 0.9 / 3.29` | Table 3-3 |
| `C_D_ROUGH/C_L_ROUGH/C_M_ROUGH` | `1.2 / 1.0 / 3.29` | Table 3-3 |
| `GAMMA_SC_NORMAL` | `1.1` | Table 4-1 |
| `hydrodynamic_force_per_meter(rho_w, D, U, a, C_D=0.9, C_M=3.29) -> float` | Eq 3.1 (drag + inertia, signed) | §3.2.1 |
| `lift_force_per_meter(rho_w, D, U, C_L=0.9) -> float` | Eq 3.2 (½ρCₗD U²) | §3.2.1 |
| `submerged_weight_per_meter(D, t_wall, rho_steel, rho_coat, t_coat, rho_contents, rho_w) -> float` | g=9.80665, full coating+contents annulus model | §2.2 |
| `absolute_stability_check(W_s, F_H, F_L, mu, gamma_SC=1.1) -> StabilityResult` | `util = γ_SC*(F_H + μ*F_L) / (μ*W_s)` | §4.3.1 Eq 4.1 |
| `generalized_stability_check(W_s, F_H, F_L, mu, F_R, gamma_SC=1.1) -> StabilityResult` | `util = γ_SC*F_H / (μ*(W_s − F_L) + F_R)` | §4.3.2 Eq 4.5 |

`subsea/on_bottom_stability/__init__.py` re-exports the full surface. There is also a
machine-readable `manifest.yaml` mapping each public function to its DNV clause + equation.

**Impl 2 (`geotechnical/on_bottom_stability.py`):**

| Symbol | Signature | Note |
|---|---|---|
| `STANDARD` | `"DNV-RP-F109"` (string constant) | No edition |
| `DEFAULT_CL` | `0.9` | Single value; no smooth/rough split |
| `G` | `9.81` (vs 9.80665 in Impl 1) | Numerical drift on weight |
| `SubmergedWeightResult` | `@dataclass(ws_n_per_m, buoyancy_n_per_m, dry_weight_n_per_m)` | |
| `HydrodynamicLoadResult` | `@dataclass(drag, inertia, total_horizontal, lift)` (per m) | |
| `StabilityResult` | `@dataclass(is_stable, utilization, required_weight_n_per_m, standard)` | `utilization` (US spelling) vs `utilisation` in Impl 1 |
| `VerticalStabilityResult` | `@dataclass(is_stable, utilization, standard)` | |
| `submerged_weight(od_steel_m, wt_steel_m, coating_thickness_m, rho_steel, rho_coating, rho_contents, rho_seawater)` | Same physics as Impl 1, but g=9.81 | |
| `hydrodynamic_loads(od_total_m, U, a, rho, cd, cm, cl=0.9)` | Combined drag+inertia+lift; cd/cm REQUIRED, no defaults | |
| `lateral_stability_check(W_s, F_H, F_L, mu, gamma) -> StabilityResult` | **`util = γ*F_H / (μ*(W_s − F_L))`** — this is the **§4.3.2 generalized form with F_R=0**, but the file calls it the "simplified method" | Mis-labelled in docstring; raises `ValueError` on W_s≤0 (vs Impl 1 returning inf) |
| `drag_force_per_meter(U, D, rho, cd)` / `lift_force_per_meter(U, D, rho, cl)` / `inertia_force_per_meter(a, D, rho, cm)` | Components broken out as 3 separate functions | API duplication with `hydrodynamic_loads` |
| `check_lateral_stability(W_s_kN, F_H_kN, F_L_kN, mu, gamma)` | **kN wrapper** that scales by 1000 then calls `lateral_stability_check` | Useful for kN-input call sites; not in Impl 1 |
| `check_vertical_stability(W_s_kN, F_L_kN, gamma)` | `util = γ*F_L/W_s; stable if ≤1.0` | Not in Impl 1; useful upward-stability check |

## Test Inventory

| Test file | Lines | Target module | Tests | Status |
|---|---|---|---|---|
| `tests/subsea/on_bottom_stability/test_dnv_rp_f109.py` | 297 | `digitalmodel.subsea.on_bottom_stability.dnv_rp_f109` (Impl 1) | **20 functions** (collect-only confirmed) | LIVE — collects + runs |
| `tests/test_on_bottom_stability.py` | 207 | `digitalmodel.geotechnical.on_bottom_stability` (Impl 2) | **14 functions** (collect-only confirmed) | LIVE — collects + runs (R5 reported "0", incorrect) |
| `tests/subsea/pipeline/test_on_bottom_stability.py` | 215 | `digitalmodel.subsea.pipeline.on_bottom_stability` (**DOES NOT EXIST**) | 16 functions, but **0 actually collect** | DEAD — `tests/conftest.py:19` puts it in `collect_ignore`. Phantom test against a phantom module. |

> R5 said one file was "empty / 0 tests". The actual situation is more interesting: the
> orphaned file at `tests/subsea/pipeline/test_on_bottom_stability.py` contains **215
> lines of well-formed tests** referencing functions like `peak_combined_velocity`,
> `keulegan_carpenter`, `current_velocity_ratio`, `generalized_stability_number`,
> `required_stability_number`, `stability_check`, `full_stability_assessment`,
> `MU_SAND`, `MU_CLAY` — none of which exist anywhere in `src/`. The target module
> `digitalmodel.subsea.pipeline.on_bottom_stability` has **no git history**: it was
> never present in the repo. So this is either (a) tests written ahead of an unbuilt
> implementation, or (b) tests written against a deleted draft that never landed.
> Either way the tests are dead — `conftest.py:19` silently excludes them.

## Active Callers (src/)

`grep -rn "from digitalmodel.subsea.on_bottom_stability\|from digitalmodel.geotechnical.on_bottom_stability"
src/digitalmodel/` returns:

- `src/digitalmodel/subsea/on_bottom_stability/__init__.py:9` — internal re-export, **zero downstream importers in src/** outside the package itself
- `src/digitalmodel/specs/manifest_schema.py:45` — docstring example only, not a real import
- `src/digitalmodel/geotechnical/on_bottom_stability.py` — no callers anywhere

**Net: zero downstream src/ callers for either implementation.** Both are pure
public-surface candidates with no upstream pipeline orchestrator yet calling them.
(R5 noted the broader `subsea/pipeline/pipeline.py` orchestrator dispatches to LB/TB/UB/PL
but not OBS — that's a gap, not a caller.)

## Numerical-Divergence Analysis

This is the load-bearing finding for #2694's "silent numerical drift" classification.

**Coefficient defaults:**

| Pipe type | Standard (DNV-RP-F109 Table 3-3, 2021) | Impl 1 | Impl 2 |
|---|---|---|---|
| Smooth pipe, C_L | 0.9 | `C_L_SMOOTH = 0.9` ✓ | `DEFAULT_CL = 0.9` ✓ |
| Rough pipe, C_L | 1.0 | `C_L_ROUGH = 1.0` ✓ | (no rough variant — single default) ✗ |
| Smooth pipe, C_D | 0.9 | `C_D_SMOOTH = 0.9` ✓ | (no default — required arg) — |
| Rough pipe, C_D | 1.2 | `C_D_ROUGH = 1.2` ✓ | (no default) — |
| Inertia C_M | 3.29 | `C_M_SMOOTH = 3.29` ✓ | (no default) — |

Impl 1 is **standards-compliant** for both smooth and rough cases (Table 3-3). Impl 2 has
**only a single C_L default at 0.9** (smooth) — there is no way to call it with the
rough-pipe lift coefficient without the caller knowing to pass `cl=1.0`. **This is the
defect R5 flagged.** Functionally, Impl 2's call sites must hand-specify rough-pipe
coefficients out of band; if a caller forgets, a rough-pipe scenario gets calculated with
smooth-pipe lift (~10% under-prediction on lift force).

**Formula divergence on the lateral-stability check itself:**

| | Formula | Source |
|---|---|---|
| Impl 1 `absolute_stability_check` | `util = γ_SC*(F_H + μ*F_L) / (μ*W_s)` | DNV-RP-F109 **§4.3.1 Eq 4.1** (absolute method) |
| Impl 1 `generalized_stability_check` | `util = γ_SC*F_H / (μ*(W_s − F_L) + F_R)` | DNV-RP-F109 **§4.3.2 Eq 4.5** (generalized method, F_R = passive soil resistance) |
| Impl 2 `lateral_stability_check` | `util = γ*F_H / (μ*(W_s − F_L))` | DNV-RP-F109 §4.3.2 Eq 4.5 with **F_R = 0** (no passive soil), called the "simplified method" in the docstring |

**Both implementations are present in DNV-RP-F109 (Eq 4.1 and Eq 4.5 respectively), but
they answer different questions.** Eq 4.1 is the conservative "absolute" check; Eq 4.5
gives credit for both lift-relief and passive soil resistance.

**Verdict-flip test:** for `W_s=500, F_H=183, F_L=150, μ=0.6, γ_SC=1.1`:

- Impl 1 (Eq 4.1): `util = 1.1*(183+0.6*150)/(0.6*500) = 1.0000` → **is_stable=False**
- Impl 2 (Eq 4.5 with F_R=0): `util = 1.1*183/(0.6*(500−150)) = 0.9572` → **is_stable=True**

**Same physical scenario, same DNV-RP-F109 standard cited, opposite stable/unstable verdicts
at the design margin.** Engineers reading the two implementations would never know
they're applying different design philosophies (one conservative, one with lift-relief
credit) absent close reading.

**Additional numerical drift (independent of formula choice):** Impl 1 uses `g = 9.80665`,
Impl 2 uses `G = 9.81`. On the same pipe (12" steel + 50mm concrete coat, seawater-filled):
W_s = 1991.60 N/m (Impl 1) vs 1992.28 N/m (Impl 2). ~0.034 % drift on submerged weight —
within rounding for design purposes but still indefensible at audit.

## Standards-Compliance Verdict

| Criterion | Impl 1 | Impl 2 |
|---|---|---|
| Edition cited | Edition Oct 2021 (module docstring) | None |
| Clause references in docstring | §3.2.1 Eq 3.1/3.2, §2.2, §4.3.1 Eq 4.1, §4.3.2 Eq 4.5, Tables 3-3 / 4-1 | DNV-RP-F109 only; no clauses |
| Both absolute (§4.3.1) and generalized (§4.3.2) methods | YES (separate functions) | NO (only §4.3.2 with F_R=0, mislabelled "simplified") |
| Smooth/rough coefficient split | YES (Table 3-3) | NO (single `DEFAULT_CL`) |
| Safety class factor (Table 4-1) | YES (`GAMMA_SC_NORMAL = 1.1`, parameterised) | Caller-supplied (`safety_factor` argument) |
| `manifest.yaml` machine-readable trace | YES | NO |
| Citation contract (`.claude/rules/calc-citation-contract.md`) | None yet (zero pipeline-domain modules emit citations; pending mooring pilot fix #2685) | None |

**Impl 1 is the standards-faithful implementation. Impl 2 is functionally a subset of Impl 1's
generalized method, mislabelled, missing the rough-pipe variant, missing the absolute method,
and using a less-precise gravity constant.**

## Canonical Candidate Ranking

Scoring rubric (each 0–3, weighted by audit criteria):

| Implementation | Test coverage | Active callers | Std refs | API quality | Total |
|---|---|---|---|---|---|
| (1) `subsea/on_bottom_stability/dnv_rp_f109.py` | 3 (20 test fns, edition+clause-referenced) | 0 (live re-export) | 3 (edition + clause + Eq refs + manifest.yaml) | 2 (NamedTuple — readable but not subclassable, lacks kN wrapper) | **8** |
| (2) `geotechnical/on_bottom_stability.py` | 2 (14 test fns, no clause refs) | 0 | 0 (standard name only, no edition, no clauses) | 2 (4 dataclasses — more extensible than NamedTuple — but mislabelled formula) | **4** |

**Top canonical candidate: (1) `digitalmodel.subsea.on_bottom_stability`.**

Rationale: it (a) implements **both** DNV-RP-F109 lateral-stability methods (absolute §4.3.1
+ generalized §4.3.2) correctly, (b) has the smooth/rough coefficient split that the
standard mandates, (c) lives under the topically-correct `subsea/` namespace (consistent
with the catenary canonicalisation pattern — physically-coupled pipeline mechanics belong
under `subsea/`, not `geotechnical/`), (d) carries a `manifest.yaml` machine-readable trace,
and (e) has the higher test count with explicit equation references in docstrings.

Caveat: Impl 1 lacks the kN-input wrapper (`check_lateral_stability`) and the vertical
stability check (`check_vertical_stability`) that Impl 2 ships. **Port these forward as
thin convenience wrappers into Impl 1 before deleting Impl 2.**

## Shadow Copy / Deletion Candidates

| # | File | Risk | Notes |
|---|---|---|---|
| (2) | `src/digitalmodel/geotechnical/on_bottom_stability.py` | low — 0 src/ callers; only `tests/test_on_bottom_stability.py` exercises it | After porting `check_lateral_stability` + `check_vertical_stability` wrappers into Impl 1, this file can be deleted |
| — | `tests/subsea/pipeline/test_on_bottom_stability.py` | none — already in `collect_ignore` since at least 2026-02-28 | Phantom tests against non-existent module. Best disposition: **delete the file and the `collect_ignore` entry**. (Alt: salvage 1-2 test names like `MU_SAND/MU_CLAY` constants if they're useful additions to Impl 1.) |

**Net: 1 implementation file + 1 dead test file recommended for removal**, after porting
the kN-input and vertical-stability wrappers into the canonical surface.

## Active Callers Needing Migration

**None.** Both implementations have zero downstream src/ importers (verified via grep).
The migration is test-file rewriting only:

| Caller | Currently imports | Migration target |
|---|---|---|
| `tests/test_on_bottom_stability.py` (14 tests against Impl 2 — `submerged_weight`, `hydrodynamic_loads`, `lateral_stability_check`, `drag/lift/inertia_force_per_meter`, `check_lateral_stability`, `check_vertical_stability`) | `digitalmodel.geotechnical.on_bottom_stability` | `digitalmodel.subsea.on_bottom_stability` after Impl 1 absorbs the kN + vertical-stability surface. Renames: `lateral_stability_check` → `generalized_stability_check(F_R=0)`; `submerged_weight` (kw differences) → `submerged_weight_per_meter`; `check_lateral_stability` → new kN-wrapper; `check_vertical_stability` → new function. |
| `tests/subsea/pipeline/test_on_bottom_stability.py` (dead — in `collect_ignore`) | `digitalmodel.subsea.pipeline.on_bottom_stability` (DNE) | Delete the file. |
| `tests/subsea/on_bottom_stability/test_dnv_rp_f109.py` (20 tests against Impl 1) | `digitalmodel.subsea.on_bottom_stability.dnv_rp_f109` | NO CHANGE — already against canonical. |

**Net: 1 test file's 14 functions need re-targeting; 1 test file deleted; 1 test file
untouched. No src/ callers to migrate.**

## Recommended Deprecation Plan

1. **Port forward the kN-input + vertical-stability surface** into `subsea/on_bottom_stability/`:
   - Add `check_lateral_stability(W_s_kN, F_H_kN, F_L_kN, mu, gamma_SC) -> StabilityResult` —
     kN wrapper around `generalized_stability_check` (matches Impl 2's surface; preserves
     the F_R=0 behaviour as the explicit default).
   - Add `check_vertical_stability(W_s_kN, F_L_kN, gamma_SC) -> StabilityResult` — vertical
     stability is a real DNV-RP-F109 check (uplift) Impl 1 currently doesn't expose. The
     manifest.yaml should be updated with its §-ref (the standard's §3.4 / vertical
     equilibrium section — to be verified in the wiki page when Domain Knowledge Sweep
     #2667 produces the DNV-RP-F109 entry).
   - Add `MU_SAND = 0.5, MU_CLAY = 0.2` (or whatever the actual values are per
     DNV-RP-F109 §3.4 / Table 3-5) as named constants — both implementations omit
     them today; the dead `subsea/pipeline` test file references them as a hint.

2. **Re-target the 14 tests** in `tests/test_on_bottom_stability.py` to point at
   `digitalmodel.subsea.on_bottom_stability` with the new wrapper names. Replace the
   `submerged_weight` (positional kwargs) calls with `submerged_weight_per_meter` (Impl 1's
   signature). The `StabilityResult` field name change (`utilization` → `utilisation`) is
   the only ABI break — either rename or expose a property alias.

3. **Delete the two redundant files** in one commit:
   - `src/digitalmodel/geotechnical/on_bottom_stability.py`
   - `tests/subsea/pipeline/test_on_bottom_stability.py`
   - Also remove the line at `tests/conftest.py:19` (no longer needed once the dead
     test file is gone).

4. **Verify with pytest** that the 20 + 14 retained tests pass against the canonical surface
   before merging.

5. **Update `docs/field-development/subsea-production-systems-mapping.md`** if it points at
   `geotechnical/on_bottom_stability.py` anywhere (one match found; verify it's the canonical
   pointer).

6. **Calc citation follow-up:** when the mooring pilot (#2685) lands, wire `Citation`
   emission into Impl 1 for DNV-RP-F109 Table 3-3 (C_D / C_L / C_M values) and Table 4-1
   (GAMMA_SC). Manifest.yaml already provides the clause/equation hooks.

## Findings (Surprises)

1. **The "empty test file" claim in R5 was wrong.** `tests/test_on_bottom_stability.py`
   has 14 working tests. The actual problem child is `tests/subsea/pipeline/test_on_bottom_stability.py`
   — 215 lines of tests imported from a module that never existed in the source tree
   (`digitalmodel.subsea.pipeline.on_bottom_stability`), already silently excluded by
   `tests/conftest.py:19`'s `collect_ignore`. R5 conflated three different test files.

2. **The "different default coefficients" warning in R5 (single `C_L=0.9` vs separate
   `C_L_SMOOTH=0.9 / C_L_ROUGH=1.0`) is symptomatic of a much larger formula divergence.**
   The two implementations actually implement **different DNV-RP-F109 methods** — Impl 1
   has both §4.3.1 absolute and §4.3.2 generalized; Impl 2 has only §4.3.2-with-F_R=0
   (and calls it "simplified", which is non-standard nomenclature). At a borderline
   scenario the two return **opposite stable/unstable verdicts** even with identical
   coefficient values. This is the worst case for the #2694 "silent numerical drift"
   classification.

3. **Both implementations have zero downstream src/ callers.** Neither is wired into
   the `subsea/pipeline/pipeline.py` orchestrator, the OrcaFlex code-check engine, or
   anywhere else. This is a pure public-API duplication; deletion is unusually safe.
   (Contrast: the catenary case in #2686 had real upstream importers that needed
   migration in two `__init__.py` files.)

4. **Impl 2 ships kN-input and vertical-stability surface that Impl 1 lacks.** A naive
   "delete Impl 2" plan loses two callable surfaces (`check_lateral_stability(kN)` and
   `check_vertical_stability(kN)`). The migration plan must port these forward to Impl 1
   before deletion — otherwise downstream user-facing tools that haven't yet been built
   on top of Impl 2 will silently regress against Impl 1's N-only, lateral-only surface.

5. **Gravity-constant drift between the two implementations** (`9.80665` vs `9.81`)
   produces ~0.034 % drift on submerged weight in the same scenario. Negligible for
   design, but indicative of how undisciplined the duplication has been — neither file
   sourced their constants from a shared physical-constants module.

## File Inventory (for the cleanup PR)

Files referenced (absolute paths):

- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/subsea/on_bottom_stability/dnv_rp_f109.py` — **CANONICAL**
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/subsea/on_bottom_stability/__init__.py` — keeps re-export surface
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/subsea/on_bottom_stability/manifest.yaml` — needs new entries for `check_lateral_stability` (kN) and `check_vertical_stability` once ported
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/geotechnical/on_bottom_stability.py` — **delete after porting kN + vertical-stability surface forward**
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/subsea/on_bottom_stability/test_dnv_rp_f109.py` — **keep** (20 tests against canonical)
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/test_on_bottom_stability.py` — re-target 14 tests to canonical surface
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/subsea/pipeline/test_on_bottom_stability.py` — **delete** (phantom tests vs phantom module)
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/conftest.py` — remove line 19 (`collect_ignore` entry for the deleted phantom test file)
- `/mnt/local-analysis/workspace-hub/digitalmodel/docs/field-development/subsea-production-systems-mapping.md` — verify the OBS row points at the canonical module path
