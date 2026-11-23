# Marine_ops Bucket Triage — workspace-hub #2609 (r2)

> **Status:** revision 2 — durable replacement after r1 was reported written but did not land on disk
> **Date:** 2026-05-03
> **Bucket:** marine_ops (77 unique FAILED in `tests/marine_ops/`)
> **Source log:** /tmp/qg-repro-60d59565.log (1.4 MB, local repro on digitalmodel main `60d59565`)
> **Sister bucket plan:** docs/plans/2026-05-03-2609-solvers-orcaflex-triage.md (in parallel)
> **Parent umbrella:** [vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609)
> **Closed parent issue:** [vamseeachanta/workspace-hub#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580)

---

## Revision history

- **r1 (2026-05-03 morning)** — written by an agent but did not land on disk; recreated as r2. Verified missing via `find /mnt/local-analysis/workspace-hub -name "*marine-ops-triage*"` returning nothing prior to this write.
- **r2 (2026-05-03)** — durable replacement; corrects three count/labelling defects from r1's reported state:
  - R3 standard mislabel: **DNV-RP-B401 → DNV-RP-F103** (verified pure F103 via 3 independent sources)
  - R3 nodeids count: **13 → 16** (re-grep against `/tmp/qg-repro-60d59565.log`)
  - R4 free-rider count: **4 → 8** (non-legacy path mirror)
  - R6 individual issue count: **9 → 10** (log ground truth)

---

## Cluster summary

| Cluster ID | Title | Count | Top error (paraphrased) | Implicated source | Sub-issue | Status |
|---|---|---|---|---|---|---|
| R1 | unified_rao_reader fixtures + unicode test bug | 5 | AQWA fixture `KeyError`/`FileNotFoundError`; `test_unicode_handling` self-defeating assert | `tests/marine_ops/marine_engineering/test_unified_rao_reader.py` (5 nodeids) | [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) (batched) | Filed |
| R2 | catenary solver bracketing + sinh overflow | ~21 | `ValueError: f(a) and f(b) must have different signs` from `brentq`; `RuntimeWarning: overflow encountered in sinh` | `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/catenary/solver.py:218` (`_solve_simplified`); `brentq` call L260; `sinh` overflows L153-154/250/285/305; adapter precondition `catenary/adapter.py:153-157` | [vamseeachanta/digitalmodel#554](https://github.com/vamseeachanta/digitalmodel/issues/554) | Filed |
| R3 | DNV-RP-F103 calibration drift | 16 | Calibration constants drift from published F103 values; AssertionError on `assert pytest.approx(...)` | `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection.py:67` (`DNV_RP_F103_2010`) | NOT YET FILED | **BLOCKED on wiki** |
| R4 | `_generate_chain_database` `diameters[:20]` excludes 76mm | ~8 | `KeyError: 76` (76mm at index 23 sliced out) | both `tests/marine_ops/marine_engineering/test_component_database.py:236` AND `legacy/test_component_database.py:236` | [vamseeachanta/digitalmodel#555](https://github.com/vamseeachanta/digitalmodel/issues/555) | Filed |
| R5 | wave spectra assertion bounds | 4 | Tolerance regression on `test_higher_moments`, `test_jonswap_vs_published_curves` | `tests/marine_ops/marine_engineering/test_wave_spectra.py` + `legacy/test_wave_spectra.py` | [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) (batched) | Filed |
| R6 | OCIMF / RAO / integration heterogeneous | 10 | Mixed: OCIMF lookup misses; RAO interpolation; integration coupling | spread across OCIMF/RAO/integration tests | [vamseeachanta/digitalmodel#556](https://github.com/vamseeachanta/digitalmodel/issues/556)–[vamseeachanta/digitalmodel#565](https://github.com/vamseeachanta/digitalmodel/issues/565) (10 individuals) | Filed |
| R7 | `np.bool_` vs `bool` API drift | 1 | `assert isinstance(causal, bool)` fails on `np.bool_` return | `tests/.../test_hydro_coefficients.py::test_validate_causal_system` | [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) (batched; co-tagged at [vamseeachanta/digitalmodel#565](https://github.com/vamseeachanta/digitalmodel/issues/565)) | Filed |
| R8 | reservoir contract drift | 1 | `test_tank_material_balance_no_production` contract assertion | `tests/.../test_modeling.py` | [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) (batched) | Filed |

---

## Cluster details

### R1 — unified_rao_reader fixtures + unicode test bug

- **Nodeids (5):** all under `tests/marine_ops/marine_engineering/test_unified_rao_reader.py::TestUnifiedRAOReader::*`
- **Top error:** AQWA fixture path resolution failures (`FileNotFoundError`) on the majority; the `test_unicode_handling` case is a self-defeating assertion (test asserts behavior the implementation is not contracted to provide).
- **Implicated source:** test fixture wiring under `tests/marine_ops/marine_engineering/test_unified_rao_reader.py`; the production RAO reader appears uninvolved for ≥4 of 5 cases.
- **Hypothesis:** Mixed cluster — fixture pathing rot vs. one bona-fide assertion bug. Two-step fix: (a) repair fixture pathing (cheap), (b) rewrite `test_unicode_handling` to assert the actual contract.
- **Sub-issue:** [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) (batched residue)
- **Fix shape (proposed):** Will consolidate fixture path resolution to a shared `conftest.py` helper; will replace `test_unicode_handling` assertion with a contract test asserting decode-fallback behavior actually implemented.

### R2 — catenary solver bracketing + sinh overflow

- **Nodeids (~21):** mirrored across `tests/marine_ops/marine_engineering/test_mooring_catenary.py` and `legacy/test_mooring_catenary.py`. Dedup-as-required per user direction.
- **Top error:** `ValueError: f(a) and f(b) must have different signs` raised by `scipy.optimize.brentq` at `solver.py:260`; concurrent `RuntimeWarning: overflow encountered in sinh` from `solver.py:153-154`, `:250`, `:285`, `:305`.
- **Implicated source:**
  - `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/catenary/solver.py:218` — `_solve_simplified`
  - `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/catenary/solver.py:260` — `brentq` invocation
  - `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/catenary/adapter.py:153-157` — adapter precondition (where bracket should be sanity-checked before solver entry)
- **Hypothesis:** Bracketing strategy expands geometrically and crosses `sinh`'s overflow domain (>≈710) before finding a sign change for stiff input regimes. Two coupled fixes: (i) cap the upper bracket below `sinh` overflow, (ii) reject inputs at the adapter that cannot be bracketed.
- **Sub-issue:** [vamseeachanta/digitalmodel#554](https://github.com/vamseeachanta/digitalmodel/issues/554)
- **Fix shape (proposed):** Will change `_solve_simplified` bracketing to use a domain-aware upper bound; will surface adapter precondition violations as a dedicated exception type rather than letting them reach `brentq`.

### R3 — DNV-RP-F103 calibration drift (BLOCKED)

> **BLOCKED:** wiki citation surface gap — fix cannot land until F103 wiki page exists, per `.claude/rules/calc-citation-contract.md`.

- **Nodeids (16):** all under `tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py` (count revised from r1's 13 via re-grep of `/tmp/qg-repro-60d59565.log`).
- **Top error:** AssertionError on `assert <result> == pytest.approx(<published value>, ...)` — calculated CP values drift from DNV-RP-F103 (2010) published constants.
- **Implicated source canonical path:** `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection.py:67` — method `DNV_RP_F103_2010`.
- **Reference standard PDF:** `/mnt/ace/O&G-Standards/DNV/DNV_RP_F103_(2010)_Cathodic_Protection_of_Submarine_Pipelines_by_Galvanic_Anodes.pdf` (verified accessible 2026-05-02).
- **Standard-label correction (r1→r2):** r1 incorrectly tagged this cluster as DNV-RP-B401. Verified pure DNV-RP-F103 via three independent sources:
  1. Test docstring line 2 explicitly cites F103.
  2. 14 calls in the test file invoke `cp_calculator.DNV_RP_F103_2010(...)`.
  3. A separate, **passing** B401 test suite exists at `tests/cathodic_protection/test_dnv_rp_b401_doc_verified.py`, proving the codebase distinguishes the two standards.
- **Wiki citation surface gap:** `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f103.md` does not exist on disk. Per `.claude/rules/calc-citation-contract.md` (item 2): "Citation target: a wiki page with #2471 frontmatter (`code_id`, `publisher`, `revision`)." No wiki page → no citation target → fix is contract-blocked.
- **Sub-issue:** NOT YET FILED. Will be filed after F103 wiki page lands.
- **Fix shape (proposed, post-unblock):** Will (a) author `dnv-rp-f103.md` with #2471-style frontmatter (`code_id: DNV-RP-F103`, `publisher: DNV`, `revision: 2010`), (b) re-derive constants in `cathodic_protection.py:67` from the published PDF and emit a `Citation` per the contract pilot, (c) re-baseline test expectations against the cited values.

### R4 — `_generate_chain_database` `diameters[:20]` excludes 76mm

- **Nodeids (~8):** mirrored across legacy and non-legacy paths (free-rider count revised from r1's 4 to 8 — both `tests/marine_ops/marine_engineering/legacy/test_component_database.py:236` AND non-legacy `tests/marine_ops/marine_engineering/test_component_database.py:236` carry the same defect path).
- **Top error:** `KeyError: 76` — 76mm is at index 23 of the diameters list; the slice `diameters[:20]` drops everything from index 20 onward.
- **Implicated source:** `_generate_chain_database()` — slice expression at the database-build site.
- **Hypothesis:** Off-by-N slice intended as a sanity-bound during early development; never widened when the diameter table grew.
- **Sub-issue:** [vamseeachanta/digitalmodel#555](https://github.com/vamseeachanta/digitalmodel/issues/555)
- **Fix shape (proposed):** Will remove the `[:20]` slice (or replace with `len(diameters)` for explicitness); will add a regression test asserting all catalogued diameters round-trip through the database.

### R5 — wave spectra assertion bounds

- **Nodeids (4 = 2 unique × 2 mirrored files):**
  - `test_higher_moments`
  - `test_jonswap_vs_published_curves`
  - mirrored across `tests/marine_ops/marine_engineering/test_wave_spectra.py` and `legacy/test_wave_spectra.py`
- **Top error:** Tolerance regression — values drift just outside the asserted relative-tolerance window.
- **Hypothesis:** Either (a) numerical regression in spectra implementation (real defect) or (b) tolerance bands set tighter than the implementation's actual numerical precision (test-side defect). Triage requires running the fix module locally with print of the residual to disambiguate.
- **Sub-issue:** [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) (batched)
- **Fix shape (proposed):** Will diagnose first; will fix at the right layer (production code if a real regression; tolerance widening with documented rationale if numerical-precision pressure).

### R6 — OCIMF / RAO / integration heterogeneous (10 individual issues)

- **Nodeids (10):** heterogeneous OCIMF / RAO / integration grab-bag. Per user direction "9 individual issues to keep gap" — count corrected to 10 from log ground truth.
- **Sub-issues (10 individuals):** [vamseeachanta/digitalmodel#556](https://github.com/vamseeachanta/digitalmodel/issues/556), [vamseeachanta/digitalmodel#557](https://github.com/vamseeachanta/digitalmodel/issues/557), [vamseeachanta/digitalmodel#558](https://github.com/vamseeachanta/digitalmodel/issues/558), [vamseeachanta/digitalmodel#559](https://github.com/vamseeachanta/digitalmodel/issues/559), [vamseeachanta/digitalmodel#560](https://github.com/vamseeachanta/digitalmodel/issues/560), [vamseeachanta/digitalmodel#561](https://github.com/vamseeachanta/digitalmodel/issues/561), [vamseeachanta/digitalmodel#562](https://github.com/vamseeachanta/digitalmodel/issues/562), [vamseeachanta/digitalmodel#563](https://github.com/vamseeachanta/digitalmodel/issues/563), [vamseeachanta/digitalmodel#564](https://github.com/vamseeachanta/digitalmodel/issues/564), [vamseeachanta/digitalmodel#565](https://github.com/vamseeachanta/digitalmodel/issues/565).
- **Hypothesis:** No common root cause. Each sub-issue is independent. Approximately 4 of 10 are "needs investigation" — depth of root-cause unknown until first triage pass.
- **Fix shape (proposed):** Will sequence by complexity. S1 lands the cheap, well-understood fixes; "needs investigation" items continue in parallel.

### R7 — `np.bool_` vs `bool` API drift

- **Nodeid (1):** `tests/.../test_hydro_coefficients.py::test_validate_causal_system`
- **Top error:** `assert isinstance(causal, bool)` fails because the production code returns `numpy.bool_`, which is NOT a subclass of Python `bool` under recent NumPy versions.
- **Hypothesis:** API drift — NumPy ≥1.20 hardened the `np.bool_` ↔ `bool` distinction. Either coerce at the boundary (production fix) or relax the test (`isinstance(causal, (bool, np.bool_))`).
- **Sub-issue:** [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) (batched). Co-tagged at [vamseeachanta/digitalmodel#565](https://github.com/vamseeachanta/digitalmodel/issues/565) since R6 already filed an individual issue covering the same test file.
- **Fix shape (proposed):** Will coerce at the production-code boundary (`return bool(causal)`) so the API contract is "Python bool" and downstream consumers don't need NumPy-aware type checks.

### R8 — reservoir contract drift

- **Nodeid (1):** `tests/.../test_modeling.py::test_tank_material_balance_no_production`
- **Top error:** Contract drift — test asserts a behavior the production code no longer provides under the no-production code path.
- **Hypothesis:** Reservoir module refactored without updating the contract test. Either restore the contract or update the test to match the intentional new behavior — depends on intent of the refactor.
- **Sub-issue:** [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) (batched)
- **Fix shape (proposed):** Will inspect the `git log` of the reservoir module to determine whether the contract change was intentional, then resolve at the right layer.

---

## Tally

- **Tracked:** R2 (~21) + R4 (~8) + R6 (10) + R1 (5) + R5 (4) + R7 (1) + R8 (1) = **50 of 77** marine_ops failures
- **BLOCKED:** R3 (16) — pending F103 wiki page creation
- **Unallocated residue:** **11** (= 77 − 50 − 16) — not assigned to any cluster yet; require a re-grep pass against `/tmp/qg-repro-60d59565.log` to assign or batch-file.

---

## Open questions for user

1. **F103 wiki page creation** — file the wiki-creation task as a digitalmodel issue (lives near the calc that needs it) or a workspace-hub issue (lives near the wiki tree)? Recommendation: workspace-hub, since the wiki repo and citation contract both live under workspace-hub governance.
2. **R6 4-of-10 "needs investigation" issues** — drill down after S1 lands (sequential, lower context-switch cost) or in parallel (faster wall-clock)? Recommendation: parallel for the cheap ones, sequential after S1 for the deep ones.
3. **The 11 residue failures** — file as another batched issue (mirror of [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566)), absorb into existing sub-issues by re-grep, or leave for the next triage pass? Recommendation: re-grep first; if ≥3 cluster cleanly into an existing sub-issue, absorb. Otherwise file a single batched issue.

---

## Calc-citation-contract gap

`knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f103.md` does not exist. Per `.claude/rules/calc-citation-contract.md`:

> "Citation target: a wiki page with #2471 frontmatter (`code_id`, `publisher`, `revision`). Forward-adopt these fields if the specific page you need doesn't yet carry them."
> "Validation is **fail-closed at calc time** per #2481 D2: a missing wiki page or frontmatter mismatch raises `CitationResolutionError` with the `code_id` in the message so operators can retarget."

Therefore R3's fix is contract-blocked: the calc cannot emit a valid `Citation` until the wiki page lands. The fix sequence will be:

1. Author `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f103.md` with frontmatter:
   - `code_id: DNV-RP-F103`
   - `publisher: DNV`
   - `revision: 2010`
2. Re-derive constants in `cathodic_protection.py:67` from the published PDF (`/mnt/ace/O&G-Standards/DNV/DNV_RP_F103_(2010)_Cathodic_Protection_of_Submarine_Pipelines_by_Galvanic_Anodes.pdf`).
3. Emit a `Citation` (per the pilot at `digitalmodel/src/digitalmodel/citations/schema.py`) targeting the new wiki page.
4. Re-baseline `test_cathodic_protection_dnv.py` expectations against the cited values; all 16 R3 nodeids should pass.
5. File the R3 sub-issue (digitalmodel side) after the wiki page exists, so the issue can reference the citation target on creation.
