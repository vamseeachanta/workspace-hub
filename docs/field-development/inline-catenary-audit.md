# Inline `solve_catenary()` Audit — `orcaflex/mooring_design.py`

**Issue:** [#2686](https://github.com/vamseeachanta/workspace-hub/issues/2686) Phase 3 — review inline
solver against canonical `marine_ops/marine_analysis/catenary/solver.py`.
**Investigator:** Claude (read-only, 2026-05-13).
**Status:** Findings only. No code changes. No commits.
**Predecessor:** `docs/field-development/catenary-canonicalization-investigation.md` (2026-05-12).

## Scope

The investigation doc preliminarily marked the inline `solve_catenary` as
*"keep — different problem (pretension/anchor-radius design helper, pydantic results)"*
(scoring 9 vs canonical's 9 — tied). Phase 3 instructs a deeper functional comparison to
confirm or overturn that recommendation.

## Inline solver — exact location

- File: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/orcaflex/mooring_design.py`
- Function definition: **lines 155–246** (signature line 155, body 162–246).
- Result model `CatenaryResult` (pydantic): **lines 143–152**.
- Sole src caller: `MooringLineDesign.estimate_catenary()` at **lines 283–301** (calls at line 295).
- Re-export: `orcaflex/__init__.py:43-44` (and `__all__` line 144).

## Comparison Matrix — inline vs canonical

| Dimension | Inline `solve_catenary` (mooring_design.py:155) | Canonical `CatenarySolver.solve` (marine_analysis/catenary/solver.py) |
|---|---|---|
| **Signature** | `solve_catenary(water_depth, line_length, submerged_weight_per_m, fairlead_depth=0.0, pretension=None) -> CatenaryResult` | `CatenarySolver().solve(CatenaryInput(length, horizontal_span, vertical_span, weight_per_length, ea_stiffness, water_depth=None, seabed_friction=0.0)) -> CatenaryResults` |
| **Inputs known** | water depth, line length, w (N/m), fairlead depth, *optional pretension* | length, **horizontal_span**, **vertical_span**, w (N/m), **EA stiffness** |
| **Inputs missing on the other side** | NO horizontal_span input — inline *solves for* anchor_radius (geometric output, not input) | NO pretension input; NO standalone "given vertical drop only" mode |
| **BVP solved** | 1D: given (h, L, w) and optionally T_pretension, find H and anchor offset. Low-point assumed at anchor (no negative-x branch). | 2D BVP: given (X, Y, L, w, EA), find (H, x1, x2) so both endpoints + length are satisfied. fsolve over 3 equations; 1D `brentq` fallback. |
| **Algorithm** | Lines 190–212: hand-rolled 100-iteration Newton-like step on `h_calc(H) - h` when pretension is given (initial guess `H = T cos 30°`). Lines 214–219: closed-form `a = (s² − h²)/(2h)` when no pretension. | scipy `fsolve` (Powell hybrid) over 3-equation system; `brentq` fallback on length-only error. Includes elongation `H·L/EA`. |
| **Elongation modelled?** | **No** — line is rigid (no axial stiffness input). | **Yes** — `elongation = H·L/EA`. |
| **Units (force)** | **kN internally**, kN out (line 188 converts w from N/m → kN/m; results all rounded `kN`). | **N internally**, N out. |
| **Units (weight input)** | N/m (converted at line 188). | N/m (no conversion). |
| **Result fields** | `horizontal_tension`, `vertical_tension_top`, `top_tension`, `top_angle` (deg), `suspended_length`, `grounded_length`, `anchor_radius`, `catenary_parameter` — all **rounded to 2 dp** | `horizontal_tension`, `vertical_tension_fairlead`, `total_tension_fairlead`, `total_tension_anchor`, `elongation`, `touchdown_distance`, `catenary_parameter`, `shape_x` (np.array, 100 pts), `shape_y`, `tension_distribution`, `converged`, `iterations` — full precision |
| **Result type** | Pydantic `CatenaryResult` (validates schema, JSON-serializable) | `@dataclass CatenaryResults` (numpy arrays in shape_x/y not JSON-clean) |
| **Anchor radius output** | **Yes** — `x_h + grounded` at line 235; load-bearing for `SpreadMooringConfig.generate_layout()` (mooring_design.py:359-360) | **No** — only fairlead-tension + shape arrays. Caller would have to compute `anchor_radius = horizontal_span + grounded_length` itself. |
| **Top angle (deg)** | Yes (line 234) | Not exposed (caller computes `atan2(V_fairlead, H)` themselves) |
| **Grounded length** | Yes — `max(0, L − s_suspended)` (line 230) | Implicit: caller infers from `touchdown_distance` if water_depth supplied |
| **Edge case: line too short** | `ValueError("Line length ... must exceed vertical span")` (line 184) | `ValueError("Length ... < straight distance")` (line 108-109) — checks against `√(X²+Y²)`, stricter than inline's check against pure vertical |
| **Edge case: w ≤ 0** | `ValueError("Submerged weight must be positive...")` (line 182) | `ValueError("Weight per length must be positive")` (line 102) |
| **Edge case: H ≤ 0** | Clamps to `H = max(1.0, H)` inside the Newton loop (line 210) — silent floor | Returns `1e10` sentinel from `system_equations` to push fsolve away (line 145-146); raises in `_solve_simplified` |
| **Edge case: line on seabed** | Reported via `grounded_length`; downstream consumers see grounded explicitly. | Reported via `touchdown_distance` only when `water_depth` supplied; otherwise silent. |
| **Convergence reporting** | None — no `converged`/`iterations` fields, no warnings on non-convergence (just stops at iter 100). | `converged: bool`, `iterations: int` returned; warns on fsolve failure before falling back. |
| **Standards citations** | API RP 2SK, DNV-OS-E301, Faltinsen (1990) Ch. 6 — module + function docstring | None in docstring (gap flagged in predecessor doc §"Recommended Deprecation Plan" item 6) |
| **Test coverage** | 4 direct tests + 1 indirect via `estimate_catenary` (`tests/orcaflex/test_mooring_design.py:23-63`) | 8 tests via `tests/test_catenary_module.py` + `tests/test_integration_phase1.py` |
| **Active src callers** | `MooringLineDesign.estimate_catenary` (same module) → consumed by `SpreadMooringConfig.generate_layout` for anchor_radius | `marine_analysis/profiling/profile_modules.py`, `validation/validate_catenary.py` (×3), `visualization/integration_charts.py`, `catenary/adapter.py`, `subsea/catenary_riser/legacy/catenaryMethods.py` |

## Functional divergence — *do they answer the same question?*

**No.** They solve different problems:

1. **Inline solver's problem:** *"Given a line of length L hanging from a fairlead h below the surface in water depth D with weight w (and optionally targeting pretension T), what is the geometry on the seabed?"* — outputs `anchor_radius` and `grounded_length`. This is a **preliminary mooring-design helper**: the engineer doesn't yet know the horizontal layout because that's what the helper computes.

2. **Canonical solver's problem:** *"Given an installed catenary with known anchor position (horizontal_span X, vertical_span Y), length L, weight w, and stiffness EA, what is the horizontal tension and line shape?"* — outputs tension + shape arrays. This is an **analysis solver** for an already-laid-out line.

The inline solver **outputs** what the canonical solver requires as **input** (horizontal_span ≈ anchor_radius). Replacing the inline call with a canonical call would create a chicken-and-egg problem for `SpreadMooringConfig.generate_layout()`: it asks for `cat.anchor_radius` to *place* the anchors (line 360); without the inline's anchor-radius output, the layout pass has nothing to consume.

### Could the canonical solver answer the inline's question?
Only by **wrapping it** in an outer Newton loop that searches over `horizontal_span` until the inline's `length` + `vertical_drop` constraints are met. That's strictly more expensive than the inline's closed-form `a = (s²−h²)/(2h)` and brings the canonical's `EA` requirement, which the design helper deliberately does without (preliminary design rarely has EA pinned).

### Numerical agreement on the canonical's question
If you reformulate the inline's outputs as canonical's inputs — i.e., feed `horizontal_span = inline.anchor_radius − inline.grounded_length`, same length, same w, `vertical_span = water_depth − fairlead_depth`, and a large EA to neutralise elongation — both should land on the same H (both implement `y = a·(cosh(x/a) − 1)`). The canonical adds elongation `H·L/EA`, which on a 76mm chain with EA=615 MN and H=1.5 MN over L=2250 m predicts ~5.5 m of stretch — non-trivial but not order-of-magnitude. I did **not** run a live numerical comparison in this audit (read-only constraint); the algorithmic structures match for the no-elongation, low-point-at-anchor sub-case.

## Recommendation: **KEEP** (matches predecessor doc; deeper rationale below)

The inline solver should **not** be deleted and **not** be migrated to the canonical:

1. **Different problem statement.** Inline = "design helper inverting for anchor_radius from line length"; canonical = "analysis solver inverting for tension from anchor position". Replacing one with the other requires either (a) a wrapper that double-iterates, or (b) restructuring `SpreadMooringConfig.generate_layout()` to accept horizontal_span as configuration instead of derived output.
2. **Different inputs.** Inline takes `pretension` (kN) directly; canonical has no pretension-target mode. Inline does **not** require EA; canonical requires EA > 0 (line 104, raises on missing).
3. **Different output surface.** Downstream (`SpreadMooringConfig.generate_layout` line 360) consumes `anchor_radius` and `top_angle` — neither exists on `CatenaryResults`. Migration would need a thin adapter computing these from the canonical's output.
4. **Different unit convention.** Inline returns **kN** to match its `pretension` input and the module's API RP 2SK convention; canonical returns **N**. The unit-discipline footgun noted in the predecessor doc §"Findings (Surprises)" item 5 still applies — aliasing them is the wrong move.
5. **Standards-citation asymmetry.** Inline carries explicit API RP 2SK / DNV-OS-E301 / Faltinsen citations in its docstring. Canonical has none. The right cleanup, per Phase 4, is to **add citations to the canonical**, not to delete the better-documented inline.

## What Phase 3 should actually close out

Rather than delete or migrate, Phase 3's deliverable is:

1. **Rename for disambiguation (optional, low priority).** Consider renaming the inline `solve_catenary` → `solve_catenary_design` or `estimate_anchor_geometry` to telegraph that it's a design helper, not the analysis solver. **Cost:** 5 LOC (1 def, 1 in `__init__.py` re-export, 1 in `__all__`, 1 import in test file, 1 test reference). **Risk:** very low — internal to digitalmodel, no external importers verified. **Benefit:** removes the "two functions with the same name" confusion that motivated this audit.
2. **Document the distinction.** Append a "When to use which" subsection to the predecessor investigation doc or to a new `docs/field-development/catenary-api-guide.md`:
   - Use **`solve_catenary` (mooring_design)** for preliminary mooring design when you have line length and want to derive anchor radius.
   - Use **`CatenarySolver` (marine_analysis)** for tension/shape analysis when anchor position is known.
3. **Phase 4 prerequisite (units).** When Phase 4 (unit-discipline review) lands, it should treat `CatenaryResult.horizontal_tension` (kN) and `CatenaryResults.horizontal_tension` (N) as a **typed boundary** — explicit `kN_force` and `N_force` types at the seams between the two solvers, not silent conversion. The footgun is real because `MooringLineDesign.target_pretension` is `kN` (mooring_design.py:266) but `MOORING_MATERIAL_LIBRARY.*.mbl` is also `kN` (line 61) — consistent inside mooring_design, but `CatenarySolver`'s outputs would need conversion if ever wired in.
4. **Calc-citation contract (Phase 4 cross-link).** Per `.claude/rules/calc-citation-contract.md` and predecessor doc item 6, the inline solver currently cites standards in *prose only* (docstring strings). It does **not** emit `Citation` instances from `digitalmodel.citations.schema`. This is the same pattern flagged at #2685 (mooring_design.py is the *intended* citation pilot, currently aspirational). Phase 4 should align "which solver carries the citations" with the #2685 pilot decision.

## Risk Analysis (for the KEEP recommendation)

| Risk | Likelihood | Severity | Mitigation |
|---|---|---|---|
| Future contributor sees two `solve_catenary` symbols and aliases one to the other | Medium | High (silent unit drift kN↔N produces 1000× wrong tension) | Rename inline to `solve_catenary_design`; add boundary unit types |
| Inline's silent `H = max(1.0, H)` floor (line 210) masks a non-converged solve | Low | Medium | Phase 4 follow-up: surface `converged` + `iterations` on `CatenaryResult` to match canonical's contract |
| Inline's closed-form initial guess `a = (s²−h²)/(2h)` fails when `h → 0` (near-horizontal taut line) | Low | Medium | Not in scope for #2686. Track as a separate hardening issue if it ever bites. |
| Canonical solver later gets a `pretension` mode added, making inline truly redundant | Low | Low | Revisit this audit in 6 months; the API surfaces would converge naturally |

## Risk Analysis (for the **rejected** DELETE alternative)

| Risk | Likelihood | Severity | Notes |
|---|---|---|---|
| `SpreadMooringConfig.generate_layout()` (mooring_design.py:359-360) breaks because `anchor_radius` is no longer computed | **Certain** | High | Would need to write an outer iterator around `CatenarySolver` to recover the design helper's behaviour |
| `MooringLineDesign.estimate_catenary()` API change breaks `test_estimate_catenary` and any downstream notebook | High | Medium | Both tests assert specific result fields |
| Pretension-target use case (mooring_design.py:190-212) has no equivalent on canonical — would need new code | Certain | Medium | This isn't migration, it's a feature addition to the canonical |
| EA required by canonical (line 104) but `MooringLineDesign` doesn't track per-line EA today | Certain | Medium | Would have to compute composite EA from segments + add to data model |

## Migration plan — **not recommended**, but documented for completeness

If a future maintainer overrules this audit and migrates anyway:

1. Add a `pretension_target_kn: Optional[float]` mode to `CatenarySolver.solve` (or new method). Estimate: ~60 LOC, ~3 new tests.
2. Add `anchor_radius`, `grounded_length`, `top_angle_deg` to `CatenaryResults` dataclass. ~15 LOC, update 8 existing test assertions if they care about field count.
3. Compute composite EA from `MooringLineDesign.segments` (already has axial_stiffness per material). ~20 LOC in `mooring_design.py`.
4. Replace inline `solve_catenary` body with a thin call into `CatenarySolver`, converting kN↔N at the boundary. ~30 LOC.
5. Update `tests/orcaflex/test_mooring_design.py` (5 test functions touch the affected paths).
6. Keep the public function name `solve_catenary` and `CatenaryResult` for backwards compat (these are in `orcaflex/__init__.py.__all__`).

**Total estimate:** ~125 LOC touched, 5 tests modified, 3 new tests, ~6 hours of focused work plus regression-test run. **Risk:** medium — kN↔N conversion at boundary is exactly the failure mode the predecessor doc flagged as a footgun.

## Verdict

**Recommendation: KEEP.** Optional cleanup: rename to `solve_catenary_design` (5 LOC) to remove the symbol-collision smell that triggered this audit. The substantive Phase 4 work is the **citation alignment** (#2685 wiring) and **unit-type boundary** between kN and N at the inline ↔ canonical seam — neither of which requires deleting code.

## Findings — surprises during this audit

1. **The two solvers don't take symmetric inputs.** The inline's *output* `anchor_radius` is the canonical's *input* `horizontal_span`. This isn't two implementations of the same equation — it's two ends of the same engineering workflow. The predecessor doc captured the "different API" intuition; this audit confirms the algorithmic asymmetry behind it.
2. **`SpreadMooringConfig.generate_layout()` depends on `anchor_radius` being a free output**, not an input (line 360). Deleting the inline would silently break the spread-mooring layout generator — exactly the kind of "we deleted the duplicate, why is everything red?" failure mode that motivates this kind of audit.
3. **Inline has standards citations; canonical does not.** The predecessor doc's recommendation item 6 ("add wiki citation to canonical") is more load-bearing than it sounded — currently the *better-documented* solver is the inline one. Deleting it would leave the project's catenary calc with zero standards provenance in the code, contradicting `.claude/rules/calc-citation-contract.md`. The right move is to forward-port citations from inline to canonical *before* (or instead of) any consolidation.

## Files referenced (absolute paths)

- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (lines 143–246 — `CatenaryResult` + `solve_catenary` body; line 295 — sole src caller via `MooringLineDesign.estimate_catenary`; line 360 — `anchor_radius` consumer)
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/orcaflex/__init__.py` (lines 43–44, 144 — re-export)
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_analysis/catenary/solver.py` (canonical)
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/orcaflex/test_mooring_design.py` (5 test functions covering inline)
- `/mnt/local-analysis/workspace-hub/docs/field-development/catenary-canonicalization-investigation.md` (predecessor)
- `/mnt/local-analysis/workspace-hub/.claude/rules/calc-citation-contract.md` (Phase 4 cross-link)
