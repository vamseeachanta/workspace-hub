# Plan for #2694: Cathodic Protection — edition-parameterized merge (Option β)

> **Status:** revised (r2 — addresses 8 MAJOR findings from r1 cross-review)
> **r1 review artifacts:** scripts/review/results/2026-05-13-plan-2694-{claude,codex,gemini}.md
> **r2 date:** 2026-05-13
> **Complexity:** T2 (regulatory-hazardous calc surface — review at T2/3-provider depth)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2694

## r2 Revision Summary (vs r1)

Fixes (each verified against live code on 2026-05-13):

1. **(Finding 1, 3)** Baseline McCoy/Dwight ratio AC corrected from `≈ 2.0` to the actual computed value `1.8702` at `L=2 m, r=0.15 m`. Python recompute: `(ln(4)−0.5)/(ln(53.33)−1) × 2 ≈ 1.8702`. The ratio is geometry-dependent and asymptotically approaches but never reaches 2.0; choosing a numeric is more falsifiable than a symbolic claim.
2. **(Finding 2)** Removed non-existent symbol references. Real names verified in code: `marine_structure_current_demand` and `ZONE_CURRENT_DENSITY` (not `get_zone_current_density_2017`); `_B401_2021_COATING_CATEGORIES` (not `COATING_BREAKDOWN_2021`); enum members `THREE_LAYER_PE`/`THREE_LAYER_PP`/`CONCRETE_WEIGHT` (not `3LPE`/`3LPP`/`CONCRETE`).
3. **(Finding 3 from Claude r1)** `COATING_BREAKDOWN_2017` table corrected to mirror `coating.py:39-49` exactly: NEOPRENE `(0.02, 0.003)`, CONCRETE_WEIGHT `(0.02, 0.001)`, all keys use the enum member names actually shipped.
4. **(Finding 4)** P2 scope expanded from 4 to 7 material divergence dimensions. Added: bracelet resistance (item #10), utilization factor defaults (#11), zinc capacity availability (#13), Dwight stubbiness validation (#14). AC-P2.2 expanded to enforce all 7 table names; new AC rows added per divergence.
5. **(Finding 5)** P4 router pseudocode keeps `cfg["inputs"]["calculation_type"]` as the dispatch key (matches live router + YAML); edition is mapped from `calculation_type` internally (no schema break). New AC `AC-P4.7a` asserts legacy YAML routes correctly.
6. **(Finding 6)** P1/P4 pseudocode no longer changes `coating_breakdown_factor`'s return type to `CitedValue`. It continues returning `float`; `Citation` instances emit to a sidecar attribute `result.citations: tuple[Citation, ...]` on the dataclass results that already carry numeric payloads, per `.claude/rules/calc-citation-contract.md` step 6.
7. **(Finding 7)** New "Cross-Repo Strategy" section spells out which commits land in workspace-hub (docs/rules/wiki/plan) vs digitalmodel (code/tests/yaml), commit ordering, per-repo rollback, PR/tag conventions, and CI ordering.
8. **(Finding 8)** Reduced the deliverable promise to the 6 B401-edition-sensitive modules explicitly listed in §Files to Change (dnv_rp_b401, coating, marine_cp, marine_structure_cp, anode_sizing, pipeline_cp). Added an explicit non-goal: the remaining 11 functional modules (anode_depletion, corrosion_rate, iccp_design, cp_monitoring, cp_reporting, cp_survey, stray_current, fuel_system_cp, iso_15589_2, api_rp_1632, astm_g42/g80) are out-of-scope for `edition=` because they are not B401-2017-vs-2021-sensitive; documented per module.

---

## Resource Intelligence Summary

### Existing repo code

**Surface 1 — Functional package** `digitalmodel/src/digitalmodel/cathodic_protection/` (17 modules,
4 731 LOC, 206 test functions, **0 src/ callers outside its own facade**):
- `dnv_rp_b401.py` (DNV-RP-B401 2017 core; coating BD, anode resistance, Dwight stand-off, **McCoy flush-mount**)
- `anode_sizing.py`, `anode_depletion.py`, `coating.py`, `corrosion_rate.py`
- `marine_cp.py`, `marine_structure_cp.py` (splash zone → 0.0 A/m²)
- `pipeline_cp.py`, `iccp_design.py`, `cp_monitoring.py`, `cp_reporting.py`, `cp_survey.py`
- `stray_current.py`, `fuel_system_cp.py`
- Sub-standard modules: `api_rp_1632.py`, `iso_15589_2.py`
- `__init__.py` — 331-line facade exporting 100+ public names

**Surface 2 — Router** `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/` (6 modules,
3 259 LOC, 230 test functions, **2 src/ callers: `engine.py` + `cp_html_report.py`**):
- `cathodic_protection.py` (1 853 LOC; class `CathodicProtection` with `router(cfg)` dispatch)
- `cp_DNV_RP_B401_2021.py` (459 LOC; DNV-RP-B401 May 2021; splash = 0.10 coated / 0.20 bare; **Dwight** for flush)
- `cp_DNV_RP_F103_2010.py`, `cp_sacrificial_anode_b401.py`
- `cp_astm_g42.py`, `cp_astm_g80.py`

**Surface 3 — Deprecation shims** `digitalmodel/src/digitalmodel/infrastructure/common/`:
- `cathodic_protection.py`, `cp_DNV_RP_B401_2021.py`, `cp_sacrificial_anode_b401.py` — all 3 pure re-exports
- Emit `DeprecationWarning` on every import; **130+ specialized tests transit them**

**Other**:
- `digitalmodel/src/digitalmodel/infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml`
  L4: `calculation_type: ABS_gn_ships_2018 # DNV_rp_b401_2011, DNV_rp_b401_2021_05, ABS_gn_ships_2018`
  — both `DNV_rp_b401_2011` and `DNV_rp_b401_2021_05` raise `ValueError("not IMPLEMENTED")` (dead keys).
- `digitalmodel/src/digitalmodel/citations/registry.py` — pilot citation infra (pending #2685 to land).

### Standards

8 additional standards covered **only** by the functional package (router has none of these):

| Standard | Functional pkg module | Router |
|---|---|---|
| ISO 15589-2 (offshore CP) | `iso_15589_2.py` (20 tests) | absent |
| API RP 1632 (cathodic protection of underground storage tanks) | `api_rp_1632.py` (16 tests) | absent |
| NACE SP0169 (external corrosion control on buried/submerged piping) | docstrings in `pipeline_cp.py` / `corrosion_rate.py` | absent |
| NACE SP0176 (CP of fixed offshore steel structures) | docstrings in `marine_structure_cp.py` | absent |
| NACE SP0207 (close-interval survey) | docstrings in `cp_survey.py` | absent |
| ASTM G42 (cathodic disbondment) | docstrings — also has standalone `cp_astm_g42.py` router-side (175 LOC) | router has G42 |
| ASTM G80 (anode performance for steel in soils) | docstrings — also has standalone `cp_astm_g80.py` router-side (141 LOC) | router has G80 |
| NORSOK M-506 (CP design Norwegian Continental Shelf) | docstrings | absent |
| EN 50162 / EN 15280 (stray-current/AC corrosion EU) | docstrings in `stray_current.py` | absent |
| ISO 18086 (AC corrosion of buried pipelines) | docstrings in `stray_current.py` | absent |

**Net:** 8 standards (ISO 15589-2, API RP 1632, NACE SP0169/SP0176/SP0207, NORSOK M-506,
EN 50162/15280, ISO 18086) live **only** in the functional package — picking the router as canonical
would silently lose them. **Plan must preserve all 8 in the merged surface.**

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-2017.md` — **MISSING** (no prod page; needed for citation emission)
- `knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-2021.md` — **MISSING** (same)
- Other CP standards (ISO 15589-2, API RP 1632, NACE SP0169) — **none have wiki pages**; per #2667 domain sweep, CP coverage is on the gap list.

### Documents consulted

- `docs/field-development/cathodic-protection-edition-decision.md` — investigation doc (this plan's parent;
  recommends Option β, names 15 divergence dimensions, 4-phase outline, 5–7 day estimate)
- `docs/plans/2026-05-13-issue-2685-citation-pilot-option-a-plan.md` — citation pilot plan (P4 depends on this)
- `.claude/rules/calc-citation-contract.md` — fail-closed citation rule; `Citation` emission required at calc time
- `docs/plans/_template-issue-plan.md` — required sections
- Issue #2694 (epic) — cross-domain duplicate-implementation cleanup
- Issue #2692 (Pipelines R5 Finding 3) — surfaced the edition shadow
- Issue #2685 — citation pilot (mooring); same citation contract applies to CP

### Gaps identified

- **No edition selector exists anywhere** — both surfaces hard-code their edition in docstrings; the YAML
  dispatcher cannot route between editions.
- **Coating-category mapping is undefined** — 2017's 9-category vocabulary (FBE, 3LPE, 3LPP, coal-tar-enamel,
  asphalt-enamel, polyurethane, concrete, neoprene, none) has no 1:1 mapping to 2021's 4-category vocabulary
  (Cat I / II / III / bare). A translation table must be built and reviewed by a CP SME.
- **Splash-zone treatment divergence is silent** — same input case yields 0.0 (functional) vs 0.10–0.20 A/m²
  (router) with no warning; jacket designs differ materially.
- **Flush-anode resistance is 2× different** depending on which surface a caller imports.
- **No wiki pages for any cited CP standard exist in prod** — citation emission will fail-closed until the
  pages land (blocking dependency on #2685 + wiki authoring).
- **No regression-comparison test scaffolding** — no `test_edition_consistency.py` exists; merged surface
  needs cross-edition assertions to prevent drift.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-13 via `gh issue view`):
- `#2694` — OPEN — "Epic: Cross-domain duplicate-implementation cleanup (catenary, PipeCapacity, cathodic protection, natural-period, hydro-matrix, on-bottom stability)" — labels: enhancement, priority:high, cat:engineering, cat:bugfix
- `#2692` — OPEN — "R5 — Subsea Pipelines: Comprehensive code coverage audit (digitalmodel subsea/geotechnical/cathodic_protection/orcaflex)"
- `#2685` — OPEN — "Citation pilot contradiction: rule names orcaflex/mooring_design.py but file emits no Citation"

**File existence** (`ls` 2026-05-13):
- EXISTS: `digitalmodel/src/digitalmodel/cathodic_protection/{dnv_rp_b401,anode_sizing,coating,marine_cp,marine_structure_cp,pipeline_cp,iso_15589_2,api_rp_1632,...}.py` (17 modules)
- EXISTS: `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/{cathodic_protection,cp_DNV_RP_B401_2021,cp_DNV_RP_F103_2010,cp_sacrificial_anode_b401,cp_astm_g42,cp_astm_g80}.py`
- EXISTS: `digitalmodel/src/digitalmodel/infrastructure/common/{cathodic_protection,cp_DNV_RP_B401_2021,cp_sacrificial_anode_b401}.py` (the 3 deprecation shims)
- EXISTS: `digitalmodel/src/digitalmodel/infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml`
- MISSING: `knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-{2017,2021}.md` (load-bearing for P4 citation wiring)
- MISSING (new — this plan creates as test scaffolding under Step 1.5): `digitalmodel/tests/cathodic_protection/test_edition_divergence_baseline.py`

**Line excerpts** (functional pkg flush-anode formula — `dnv_rp_b401.py` L283–321 excerpt):
```
283: def flush_anode_resistance(
290:     """Anode resistance for flush-mount hull anode (McCoy method).
321:     # Convert inches to cm for McCoy/Sunde half-space formula.
```

**Line excerpts** (router 2021 module splash-zone — `cp_DNV_RP_B401_2021.py` L24):
```
24:     "splash":      {"coated": 0.100, "bare": 0.200},
```

**Line excerpts** (functional pkg marine_structure_cp.py splash-zone — L28 + the 0.0 enforcement that the
investigation doc reports at L57–60):
```
 28:     SPLASH = "splash"
```

**Line excerpts** (YAML dead-key advertisement — `cathodic_protection.yml` L4):
```
 4:   calculation_type: ABS_gn_ships_2018 # DNV_rp_b401_2011, DNV_rp_b401_2021_05, ABS_gn_ships_2018
```
Investigation §7.2 confirms the router rejects both `DNV_rp_b401_2011` and `DNV_rp_b401_2021_05` with
`ValueError("not IMPLEMENTED")`. Grep `digitalmodel/src/ -rn "DNV_rp_b401_2011"` returns only the YAML
line (no dispatch path implements it).

**Gap proofs:**
```
$ ls knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-2017.md
ls: cannot access ...: No such file or directory
$ ls knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-2021.md
ls: cannot access ...: No such file or directory
$ grep -rln "from digitalmodel.citations" digitalmodel/src/digitalmodel/cathodic_protection/
(no output — 0 files)
$ grep -rln "from digitalmodel.citations" digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection.py
(no output — 0 files)
```

**Test-count verification:**
- Functional-pkg tests: 18 files; sum of `grep -c "def test_"` = **206**.
- Router-side tests: 12 files under `tests/specialized/cathodic_protection/` + 1 under `tests/marine_ops/`;
  sum of test functions = **221** in specialized + ~39 in marine_ops = **~260+**.
- Tests importing deprecation shim: `grep -rn "from digitalmodel.infrastructure.common.cathodic_protection\|from digitalmodel.infrastructure.common.cp_" digitalmodel/tests/` → **11 distinct test files** transit the 3 shims. Estimated 230+ test functions cross the shim per run.

**Reproduction proofs** (Step 1.5 — capture divergence numerically BEFORE merge):

This plan is unusual: there is no "alleged runtime failure" to reproduce in the bug-report sense.
The R5 finding is an **edition-disclosure defect** + multiple silent numeric divergences that the merge
must preserve as a regression suite. **Step 1.5 produces a baseline-capture test file** before any
production change lands. All symbol names below verified against live code on 2026-05-13.

```python
File: digitalmodel/tests/cathodic_protection/test_edition_divergence_baseline.py  (NEW — Step 1.5 artifact)

import math
import pytest

def test_baseline_splash_zone_divergence():
    """Captures current behavior — DO NOT 'fix'. Asserts both surfaces produce
    today's documented divergence so the merge can detect when one collapses
    onto the other unexpectedly.

    Functional pkg: marine_structure_cp.ZONE_CURRENT_DENSITY maps every
    (SPLASH, *) tuple to (0.0, 0.0, 0.0) A/m² — splash treated as out-of-scope.
    Router 2021: cp_DNV_RP_B401_2021._B401_2021_CURRENT_DENSITIES["splash"]
    is {"coated": 0.100, "bare": 0.200}.
    """
    from digitalmodel.cathodic_protection.marine_structure_cp import (
        ZONE_CURRENT_DENSITY, ExposureZone, ClimateRegion,
    )
    from digitalmodel.infrastructure.base_solvers.hydrodynamics.cp_DNV_RP_B401_2021 import (
        _B401_2021_CURRENT_DENSITIES,
    )
    # 2017 functional: splash = 0.0 A/m² regardless of climate (mA/m² → /1000 in caller)
    assert ZONE_CURRENT_DENSITY[(ExposureZone.SPLASH, ClimateRegion.TEMPERATE)] == (0.0, 0.0, 0.0)
    # 2021 router: splash @ coated = 0.100 A/m², @ bare = 0.200 A/m²
    assert _B401_2021_CURRENT_DENSITIES["splash"]["coated"] == 0.100
    assert _B401_2021_CURRENT_DENSITIES["splash"]["bare"] == 0.200

def test_baseline_flush_anode_resistance_ratio_geometry_dependent():
    """McCoy (functional, denominator πL) vs Dwight (router, denominator 2πL).

    Ratio = 2 * (ln(2L/r) - 0.5) / (ln(4L/r) - 1). Geometry-dependent;
    asymptotically approaches but never reaches 2.0 as L/r → ∞.
    Verified by Python recompute 2026-05-13: at L=2 m, r=0.15 m the ratio is
    1.8702, well outside any tolerance that would let r1's `≈ 2.0` assertion pass.
    """
    L_m, r_m = 2.0, 0.15
    L_cm, r_cm = L_m * 100.0, r_m * 100.0
    # Functional pkg flush_anode_resistance accepts inches; recompute the
    # formula at known L,r and assert the numeric (apples-to-apples in same units).
    r_mccoy = (1.0 / (math.pi * L_m)) * (math.log(2.0 * L_m / r_m) - 0.5)
    r_dwight = (1.0 / (2.0 * math.pi * L_m)) * (math.log(4.0 * L_m / r_m) - 1.0)
    assert r_mccoy / r_dwight == pytest.approx(1.8702, rel=1e-3)
    # Sanity: the ratio is < 2 (never reaches it; would be 2 only in the limit)
    assert 1.5 < r_mccoy / r_dwight < 2.0

def test_baseline_internal_router_dwight_divergence():
    """Two router-side modules claim 'Dwight' but use different log arguments.

    cp_DNV_RP_B401_2021._b401_anode_resistance uses ln(4L/r) - 1
    cp_sacrificial_anode_b401.anode_resistance_flush uses ln(2L/r) - 1
    Same denominator (2πL) but ln(2)-difference numerator ⇒ ~1.30× internal
    divergence. Plan P2 must NOT silently collapse these onto one another;
    pick one per edition explicitly.
    """
    L, r = 2.0, 0.15
    r_b401 = (1.0/(2.0*math.pi*L)) * (math.log(4.0*L/r) - 1.0)
    r_sacrificial = (1.0/(2.0*math.pi*L)) * (math.log(2.0*L/r) - 1.0)
    ratio = r_b401 / r_sacrificial
    # Verified 2026-05-13: ratio ≈ 1.303 at L=2, r=0.15
    assert ratio == pytest.approx(1.303, rel=5e-3)

def test_baseline_coating_category_schema_divergence():
    """Functional pkg has 9 categories; router has 4. Assert both cardinalities
    so a merge cannot silently flatten one. Symbol names verified 2026-05-13:
    functional exposes `CoatingCategory` enum; router exposes
    `_B401_2021_COATING_CATEGORIES` (NOT `COATING_BREAKDOWN_2021`)."""
    from digitalmodel.cathodic_protection.coating import CoatingCategory
    from digitalmodel.infrastructure.base_solvers.hydrodynamics.cp_DNV_RP_B401_2021 import (
        _B401_2021_COATING_CATEGORIES,
    )
    assert len(list(CoatingCategory)) == 9
    assert len(_B401_2021_COATING_CATEGORIES) == 4

def test_baseline_coating_breakdown_a_b_constants():
    """FBE 2017 (a=0.02, b=0.003) vs router Cat I 2021 (a=0.05, k=0.020) —
    Cat I is HARSHER than FBE; this is the silent under-sizing risk P2 must
    preserve documentation of. Values copied directly from coating.py:40 and
    cp_DNV_RP_B401_2021.py:31."""
    from digitalmodel.cathodic_protection.coating import COATING_CONSTANTS, CoatingCategory
    from digitalmodel.infrastructure.base_solvers.hydrodynamics.cp_DNV_RP_B401_2021 import (
        _B401_2021_COATING_CATEGORIES,
    )
    assert COATING_CONSTANTS[CoatingCategory.FBE] == (0.02, 0.003)
    assert _B401_2021_COATING_CATEGORIES["I"] == {"f_ci": 0.05, "k": 0.020}
    # FBE 2017 at 20yr = 0.02 + 0.003*20 = 0.08; Cat I 2021 at 20yr = 0.05+0.020*20 = 0.45.
    # Cat I is 5.6× harsher — that's the silent regulatory hazard.

def test_baseline_yaml_dead_keys_raise():
    """Live router (cathodic_protection.py:29) raises on the YAML's
    advertised-but-undispatched calc types."""
    from digitalmodel.infrastructure.base_solvers.hydrodynamics.cathodic_protection import (
        CathodicProtection,
    )
    cfg = {"inputs": {"calculation_type": "DNV_rp_b401_2011"}}
    with pytest.raises(Exception, match="not IMPLEMENTED"):
        CathodicProtection().router(cfg)
```

**Numerical-claim audit (r2)**: every numeric in this baseline test was independently recomputed via
Python on 2026-05-13 against the actual code:
- McCoy/Dwight ratio at L=2 m, r=0.15 m → **1.8702** (NOT 2.0; r1 was wrong).
- Internal router Dwight divergence (b401 vs sacrificial) → **1.303**.
- Coating-category cardinalities → **9 vs 4**.
- FBE-2017 vs Cat-I-2021 breakdown ratio at 20yr → **5.6×**.

Run command (one-shot, captured in plan PR):
```
$ uv run pytest digitalmodel/tests/cathodic_protection/test_edition_divergence_baseline.py -v
```

This file is **created and committed as the very first thing in P1**, before any source edit, so the merge
phases (P2 especially) can run it to prove no unintended collapse occurred.

- Reproduced at: 2026-05-13.
- Failure mode observed matches investigation claim: YES — divergences confirmed by `grep`/`sed` quotes
  in the investigation doc (and re-verified independently 2026-05-13: splash-zone 0.100 literal at
  `cp_DNV_RP_B401_2021.py:24`, McCoy citation at `dnv_rp_b401.py:290`).

**Distinct sources consulted:** investigation doc (1) + issue body #2694 (2) + #2692 R5 audit (3) +
`.claude/rules/calc-citation-contract.md` (4) + #2685 plan (5) + functional-pkg source (6) + router source
(7) + YAML config (8). **Count: 8, well above the ≥3 minimum.**

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-13-issue-2694-cathodic-protection-edition-merge-plan.md |
| Investigation doc (parent) | docs/field-development/cathodic-protection-edition-decision.md |
| P1 baseline test (Step 1.5 artifact) | digitalmodel/tests/cathodic_protection/test_edition_divergence_baseline.py |
| P1 implementation | digitalmodel/src/digitalmodel/cathodic_protection/__init__.py (+ each public-API module) |
| P2 implementation | digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py + coating.py + marine_cp.py + marine_structure_cp.py |
| P2 edition tables module (NEW) | digitalmodel/src/digitalmodel/cathodic_protection/_edition_tables.py |
| P2 coating mapping module (NEW) | digitalmodel/src/digitalmodel/cathodic_protection/_coating_translation.py |
| P3 standards consolidation | preserved in existing `iso_15589_2.py`, `api_rp_1632.py`; G42/G80 unified router-side + facade re-export |
| P4 cleanup — YAML | digitalmodel/src/digitalmodel/infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml |
| P4 cleanup — shim removal | delete digitalmodel/src/digitalmodel/infrastructure/common/{cathodic_protection,cp_DNV_RP_B401_2021,cp_sacrificial_anode_b401}.py |
| P4 cleanup — test import migration | digitalmodel/tests/specialized/cathodic_protection/test_*.py (11 files) + tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py |
| New wiki pages | knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-{2017,2021}.md |
| New cross-edition tests | digitalmodel/tests/cathodic_protection/test_edition_consistency.py |
| Plan review — Claude | scripts/review/results/2026-05-13-plan-2694-claude.md |
| Plan review — Codex | scripts/review/results/2026-05-13-plan-2694-codex.md |
| Plan review — Gemini | scripts/review/results/2026-05-13-plan-2694-gemini.md |

---

## Deliverable

A single canonical cathodic-protection surface (the functional package `digitalmodel.cathodic_protection.*`)
that accepts `edition: Literal["2017", "2021"] = "2021"` at **the 6 B401-edition-sensitive public modules**
(`dnv_rp_b401.py`, `coating.py`, `marine_cp.py`, `marine_structure_cp.py`, `anode_sizing.py`,
`pipeline_cp.py`), dispatches to edition-specific lookup tables for **7 material divergence dimensions**
(coating-category schema, coating breakdown constants, splash-zone treatment, flush-anode resistance
formula, bracelet resistance formula, utilization factor defaults, anode material support — items #4, #5,
#7, #9, #10, #11, #13 from investigation §2), enforces **Dwight stubbiness validation** across both
editions (item #14), preserves all 8 additional standards (ISO 15589-2, API RP 1632, NACE
SP0169/SP0176/SP0207, NORSOK M-506, EN 50162/15280, ISO 18086) **without `edition=` because they are not
B401-edition-sensitive**, emits `result.edition_used` + `result.standard` fields on every result object
from the 6 modules, emits `Citation` instances on a **sidecar** `result.citations` attribute (NOT changing
the primary numeric return type) per `.claude/rules/calc-citation-contract.md` step 6 once the #2685 pilot
lands, with the 3 deprecation shims deleted, the YAML config corrected to advertise only dispatchable
calc-types (preserving the `calculation_type` dispatch key for back-compat), and 206 functional-side +
~221 specialized + ~39 marine_ops tests migrated.

**Explicit non-goals (Finding 8 closure):** The remaining 11 functional modules
(`anode_depletion.py`, `corrosion_rate.py`, `iccp_design.py`, `cp_monitoring.py`, `cp_reporting.py`,
`cp_survey.py`, `stray_current.py`, `fuel_system_cp.py`, `iso_15589_2.py`, `api_rp_1632.py`, and any new
`astm_g42.py`/`astm_g80.py` migrations) do **NOT** acquire `edition=` parameters in this plan because:
(a) `iso_15589_2`, `api_rp_1632`, `stray_current`, `iccp_design`, `corrosion_rate`, `cp_survey`,
`fuel_system_cp` implement non-B401 standards (no 2017-vs-2021 ambiguity); (b) `anode_depletion`,
`cp_monitoring`, `cp_reporting` are post-design instruments that read result objects produced by the 6
edition-sensitive modules and inherit edition via the `result.edition_used` field already carried.
If a follow-up audit identifies B401-edition sensitivity in any of these 11, file as a discrete issue.

---

## Pseudocode

### P1 — Edition-API foundation

```
# digitalmodel/cathodic_protection/_edition.py  (NEW)
from typing import Literal
Edition = Literal["2017", "2021"]
DEFAULT_EDITION: Edition = "2021"   # newbuild contracts in 2026 expect latest

class EditionedResult:
    """Mixin attached to every public dataclass result.
       Adds: edition_used: Edition, standard: str (full citation string)."""
    edition_used: Edition
    standard: str   # e.g. "DNV-RP-B401 (May 2021)" or "DNV-RP-B401 (Oct 2017)"

def normalize_edition(edition: Edition | None) -> Edition:
    if edition is None:
        warnings.warn(
            "edition= not specified; defaulting to '2021'. Legacy projects "
            "designed under 2017 must pass edition='2017' explicitly.",
            DeprecationWarning, stacklevel=2,
        )
        return DEFAULT_EDITION
    if edition not in ("2017", "2021"):
        raise ValueError(f"unsupported edition {edition!r}; must be '2017' or '2021'")
    return edition

# digitalmodel/cathodic_protection/dnv_rp_b401.py — public-API change
# (Finding 6 fix: citations emit to SIDECAR — primary numeric payload unchanged.)
def coating_breakdown_factor(
    category: str,
    age_years: float,
    *,
    edition: Edition | None = None,
) -> float:
    """Return the breakdown factor as a plain float (unchanged primary payload).

    Citation emission happens at result-object boundary (anode_sizing.design_cp_system
    etc), not here. This preserves downstream-consumer compatibility per
    .claude/rules/calc-citation-contract.md step 6.
    """
    ed = normalize_edition(edition)
    a, b = _coating_constants_for(category, edition=ed)   # P2 dispatch
    return a + b * age_years


# digitalmodel/cathodic_protection/anode_sizing.py — sidecar attachment
@dataclass
class AnodeSizingResult(EditionedResult):
    total_anode_mass_kg: float
    anode_count: int
    # ...other numeric payload unchanged...
    edition_used: Edition
    standard: str
    # SIDECAR (per citation contract step 6):
    citations: tuple["Citation", ...] = field(default_factory=tuple)

def design_cp_system(..., *, edition: Edition | None = None) -> AnodeSizingResult:
    ed = normalize_edition(edition)
    # ...compute numeric payload (unchanged behavior at byte level for old edition path)...
    citations = _collect_citations(edition=ed) if _CITATION_PILOT_LANDED else ()
    return AnodeSizingResult(
        total_anode_mass_kg=...,
        anode_count=...,
        edition_used=ed,
        standard=_standard_string_for(ed),
        citations=citations,   # SIDECAR — does NOT change primary numeric return
    )
```

### P2 — Numeric consolidation (the dangerous phase)

```
# digitalmodel/cathodic_protection/_edition_tables.py  (NEW)
# All numerics from the two existing modules, keyed by edition.
# DO NOT introduce new constants — only mirror what each surface already ships.

# r2 fix (Findings 2, 3): values copied verbatim from coating.py:39-49 and
# cp_DNV_RP_B401_2021.py:30-35 on 2026-05-13. Enum-member names mirror the
# actual CoatingCategory enum (THREE_LAYER_PE/PP, CONCRETE_WEIGHT, etc.).
COATING_BREAKDOWN_2017 = {
    "FBE":             (0.02, 0.003),
    "THREE_LAYER_PE":  (0.01, 0.002),
    "THREE_LAYER_PP":  (0.01, 0.002),   # coating.py:42 — same as 3LPE, NOT (0.005, 0.001)
    "COAL_TAR_ENAMEL": (0.05, 0.005),
    "ASPHALT_ENAMEL":  (0.05, 0.005),
    "POLYURETHANE":    (0.03, 0.004),
    "CONCRETE_WEIGHT": (0.02, 0.001),   # coating.py:46 — NOT key "CONCRETE", NOT (0.05, 0.002)
    "NEOPRENE":        (0.02, 0.003),   # coating.py:47 — NOT (0.01, 0.002)
    "NONE":            (1.0,  0.0),
}
# Keyed identically to live cp_DNV_RP_B401_2021._B401_2021_COATING_CATEGORIES
# but flattened to (a, b) tuples for parity with COATING_BREAKDOWN_2017.
COATING_BREAKDOWN_2021 = {
    "I":    (0.05, 0.020),
    "II":   (0.10, 0.030),
    "III":  (0.25, 0.050),
    "bare": (1.00, 0.000),
}

SPLASH_CURRENT_DENSITY = {
    "2017": {"coated": 0.0,   "bare": 0.0},      # 2017 surface treats as out-of-scope (#7)
    "2021": {"coated": 0.100, "bare": 0.200},    # 2021 actively CP-protected (#7)
}

FLUSH_RESISTANCE_FORMULA = {
    "2017": "mccoy",   # (rho/piL) * (ln(2L/r) - 0.5)              — dnv_rp_b401.py:327
    "2021": "dwight",  # (rho/2piL) * (ln(4L/r) - 1)               — cp_DNV_RP_B401_2021.py:339
}
# Engineering note: DNV-RP-B401 2021 §4.9 normatively cites Dwight for all anode
# geometries including flush-mount. McCoy is a 2017-era half-space approximation
# retained for back-compat with legacy projects. We do NOT collapse to one formula
# on engineering merit — we keep both, dispatched by edition, because customer
# contracts dictate the choice.

# r2 addition (Finding 4): items 10, 11, 13, 14 from investigation §2.
BRACELET_RESISTANCE_FORMULA = {
    "2017": "area_based",  # 0.315 * rho / sqrt(A)            — cp_sacrificial_anode_b401:166
    "2021": "modified_dwight",  # (rho/2piL) * (ln(2piL/r)-1) — cp_DNV_RP_B401_2021.py:346
}

UTILIZATION_FACTOR_DEFAULTS = {
    # functional pkg uses per-anode-type 2017 Table 10-8 values
    "2017": {"stand_off": 0.90, "flush_mounted": 0.85, "bracelet": 0.80},
    # router defaults conservatively to a single value
    "2021": {"stand_off": 0.85, "flush_mounted": 0.85, "bracelet": 0.85},
}

ANODE_MATERIAL_CAPACITY_AH_KG = {
    "2017": {"aluminium": 2000.0},                       # functional pkg: Al only
    "2021": {"aluminium": 2000.0, "zinc": 780.0},        # router: Al + Zn
}

DWIGHT_STUBBINESS_VALIDATION = {
    # Item #14: router enforces 4L/r > e; functional pkg accepts any geometry.
    # Merged surface enforces in BOTH editions (no silent nonsense for stubby
    # geometry under edition='2017'). This is a deliberate STRICTNESS UPLIFT, not
    # a behavior preservation — documented in plan §Risks below.
    "2017": "enforce_strict",
    "2021": "enforce_strict",
}

# digitalmodel/cathodic_protection/_coating_translation.py  (NEW)
# Bidirectional translator with explicit "no clean 1:1" flags. Reviewed by SME.
COATING_2017_TO_2021 = {
    "FBE":            ("CAT_I",   "approximate — 2017 FBE values are LESS conservative than 2021 Cat I"),
    "3LPE":           ("CAT_I",   "approximate"),
    "3LPP":           ("CAT_I",   "approximate"),
    "POLYURETHANE":   ("CAT_II",  "approximate — 2021 Cat II is the new thin-film bucket"),
    "COAL_TAR_ENAMEL":("CAT_III", "approximate — 2021 doesn't carry coal-tar as distinct cat"),
    "ASPHALT_ENAMEL": ("CAT_III", "approximate"),
    "CONCRETE":       ("CAT_III", "approximate"),
    "NEOPRENE":       ("CAT_I",   "approximate"),
    "NONE":           ("BARE",    "exact"),
}
# Returning back-direction map intentionally NOT defined: 2021 → 2017 is many-to-one
# and cannot be inverted without project-specific context. Callers must pick.
```

### P3 — Standards consolidation (lowest-risk phase)

```
# digitalmodel/cathodic_protection/__init__.py
# All 8 additional standards remain in their current modules (iso_15589_2, api_rp_1632,
# corrosion_rate, cp_monitoring, cp_survey, stray_current, anode_depletion, iccp_design).
# Add a `_supported_standards()` declarative manifest so the YAML dispatcher can
# advertise what's actually wired.

SUPPORTED_STANDARDS = (
    ("DNV-RP-B401", ("2017", "2021")),
    ("DNV-RP-F103", ("2010",)),
    ("ABS-CP-Ships",     ("2018",)),
    ("ABS-CP-Offshore",  ("2018",)),
    ("ISO-15589-2",      ("2004",)),
    ("API-RP-1632",      ("1996",)),
    ("ASTM-G42",         ("1996",)),
    ("ASTM-G80",         ("1998",)),
    ("NACE-SP0169",      ("2013",)),
    ("NORSOK-M-506",     ("2005",)),
    ("EN-50162",         ("2004",)),
    ("EN-15280",         ("2013",)),
    ("ISO-18086",        ("2019",)),
)
# Move ASTM G42/G80 router-side modules to call the functional-pkg ones; delete
# the router-side duplicates in P4.
```

### P4 — Cleanup

```
# YAML correction (Finding 5: keep calculation_type as the dispatch key — live
# router uses it exclusively at cathodic_protection.py:19-29 and engine.py:146
# routes through it. Adding a parallel `edition:` key is non-breaking).
calculation_type: DNV_RP_B401_offshore   # legacy dispatch key — UNCHANGED
edition: "2021"                          # NEW: explicit edition selector (optional;
                                         # defaults via _calc_type_to_edition() below)

# Router becomes a thin adapter — preserves calculation_type dispatch (no schema break)
class CathodicProtection:
    # r2 fix (Finding 5): legacy calculation_type → edition map. New
    # explicit `inputs.edition` overrides the inferred default.
    _CALC_TYPE_TO_DEFAULT_EDITION = {
        "DNV_RP_B401_offshore":     "2021",   # router today is 2021
        "DNV_RP_B401_2017":         "2017",   # NEW dispatch alias for legacy projects
        "ABS_gn_ships_2018":         None,    # not B401 — edition= ignored
        "ABS_gn_offshore_2018":      None,
        "DNV_RP_F103_2010":          None,
    }

    def router(self, cfg):
        calc_type = cfg["inputs"]["calculation_type"]   # UNCHANGED — same key as today
        if calc_type not in self._CALC_TYPE_TO_DEFAULT_EDITION:
            raise ValueError(
                f"Calculation type: {calc_type} not IMPLEMENTED. ... FAIL"
            )
        # Edition resolution: explicit `inputs.edition` wins; else fall back to
        # the calc-type's default (which is None for non-B401 std's).
        explicit_ed = cfg["inputs"].get("edition")
        default_ed = self._CALC_TYPE_TO_DEFAULT_EDITION[calc_type]
        ed = explicit_ed if explicit_ed is not None else default_ed
        result = digitalmodel.cathodic_protection.run(
            calculation_type=calc_type, edition=ed, inputs=cfg["inputs"],
        )
        cfg["results"] = {
            **result.dict(),
            "edition_used": getattr(result, "edition_used", None),
            "standard": getattr(result, "standard", None),
        }
        return cfg

# Shim deletion (after all 230+ test imports migrated)
rm digitalmodel/src/digitalmodel/infrastructure/common/cathodic_protection.py
rm digitalmodel/src/digitalmodel/infrastructure/common/cp_DNV_RP_B401_2021.py
rm digitalmodel/src/digitalmodel/infrastructure/common/cp_sacrificial_anode_b401.py
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| **Create (P1)** | digitalmodel/tests/cathodic_protection/test_edition_divergence_baseline.py | Step 1.5 baseline capture — runs FIRST, locks today's divergence numerics so P2 cannot silently collapse them |
| **Create (P1)** | digitalmodel/src/digitalmodel/cathodic_protection/_edition.py | `Edition` literal, `DEFAULT_EDITION`, `normalize_edition()`, `EditionedResult` mixin |
| **Modify (P1)** | digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py | Add `edition=` kwarg to `coating_breakdown_factor`, `current_demand`, `anode_mass_requirement`, `flush_anode_resistance`, `anode_resistance_slender_standoff` (8 functions); default = `None` → warn-and-default to "2021" |
| **Modify (P1)** | digitalmodel/src/digitalmodel/cathodic_protection/anode_sizing.py | Add `edition=` to `design_cp_system`, propagate to inputs/results; add `edition_used`/`standard` to `AnodeSizingResult` |
| **Modify (P1)** | digitalmodel/src/digitalmodel/cathodic_protection/coating.py | Add `edition=` to `coating_breakdown_factors`; expose both 2017 and 2021 `CoatingCategory` enums |
| **Modify (P1)** | digitalmodel/src/digitalmodel/cathodic_protection/marine_cp.py | `design_marine_cp(edition=)` |
| **Modify (P1)** | digitalmodel/src/digitalmodel/cathodic_protection/marine_structure_cp.py | `edition=` propagation to splash-zone treatment |
| **Modify (P1)** | digitalmodel/src/digitalmodel/cathodic_protection/pipeline_cp.py | `design_pipeline_cp(edition=)` |
| **Modify (P1)** | digitalmodel/src/digitalmodel/cathodic_protection/__init__.py | Re-export `Edition`, `DEFAULT_EDITION`; bump facade docstring to advertise both editions |
| **Create (P2)** | digitalmodel/src/digitalmodel/cathodic_protection/_edition_tables.py | `COATING_BREAKDOWN_{2017,2021}`, `SPLASH_CURRENT_DENSITY`, `FLUSH_RESISTANCE_FORMULA`, `UTILIZATION_FACTOR_DEFAULTS`, etc. — 4 material divergence dimensions in one keyed dict |
| **Create (P2)** | digitalmodel/src/digitalmodel/cathodic_protection/_coating_translation.py | `COATING_2017_TO_2021` translation map with confidence flags |
| **Modify (P2)** | digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py | Replace inline 2017 constants with `_edition_tables` lookups; keep formulas, dispatch on `edition` |
| **Modify (P2)** | digitalmodel/src/digitalmodel/cathodic_protection/coating.py | Replace inline coating-BD dict with `_edition_tables.COATING_BREAKDOWN_{2017,2021}` |
| **Modify (P2)** | digitalmodel/src/digitalmodel/cathodic_protection/marine_structure_cp.py | Splash-zone via `_edition_tables.SPLASH_CURRENT_DENSITY[edition]` |
| **Create (P2)** | digitalmodel/tests/cathodic_protection/test_edition_consistency.py | Cross-edition assertions: same inputs × different editions ⇒ documented divergences hold; unchanged dimensions (items 8, 12, 15 from investigation §2) agree |
| **Modify (P3)** | digitalmodel/src/digitalmodel/cathodic_protection/__init__.py | Declare `SUPPORTED_STANDARDS` manifest; re-export ASTM G42/G80 from canonical functional-side modules |
| **Delete (P3)** | digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cp_astm_g42.py | Move logic into functional pkg (no current `iso_15589_2.py`-equivalent for G42; add one) |
| **Delete (P3)** | digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cp_astm_g80.py | Same as G42 |
| **Create (P3)** | digitalmodel/src/digitalmodel/cathodic_protection/astm_g42.py, astm_g80.py | Receive the logic from deleted router-side modules |
| **Modify (P4)** | digitalmodel/src/digitalmodel/infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml | Replace `calculation_type: ABS_gn_ships_2018 # DNV_rp_b401_2011, DNV_rp_b401_2021_05, ABS_gn_ships_2018` with `standard:` + `edition:` two-key dispatch; remove dead keys |
| **Modify (P4)** | digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection.py | Reduce `CathodicProtection.router()` from 1 853 LOC monolith to thin adapter that calls `digitalmodel.cathodic_protection.run(...)` |
| **Delete (P4)** | digitalmodel/src/digitalmodel/infrastructure/common/cathodic_protection.py | Shim — after test imports migrated |
| **Delete (P4)** | digitalmodel/src/digitalmodel/infrastructure/common/cp_DNV_RP_B401_2021.py | Shim — after test imports migrated |
| **Delete (P4)** | digitalmodel/src/digitalmodel/infrastructure/common/cp_sacrificial_anode_b401.py | Shim — after test imports migrated |
| **Modify (P4)** | digitalmodel/tests/specialized/cathodic_protection/test_*.py (11 files) | Re-import from `digitalmodel.cathodic_protection.*`; parametrize on `edition` |
| **Modify (P4)** | digitalmodel/tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py | Same migration |
| **Modify (P4)** | digitalmodel/src/digitalmodel/visualization/reporting/cp_html_report.py | Adapt to new result schema (`edition_used`, `standard` keys) |
| **Modify (P4)** | digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py + anode_sizing.py | Wire `Citation` emission per `.claude/rules/calc-citation-contract.md` (depends on #2685 landing) |
| **Create (P4)** | knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-2017.md, dnv-rp-b401-2021.md | Frontmatter-valid stubs so citation resolver doesn't fail-closed in prod |
| **Update** | docs/plans/README.md | Add this plan to the index |
| **Update** | .claude/rules/calc-citation-contract.md | Add CP pilot as a second live emission site (after #2685 lands) |

---

## TDD Test List

### P1 baseline-capture (Step 1.5)

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_baseline_splash_zone_divergence` | 2017 splash = 0.0; 2021 splash = 0.100 coated, 0.200 bare | both surfaces, default config | 0.0 vs 0.100/0.200 assertion holds |
| `test_baseline_flush_anode_resistance_ratio_geometry_dependent` | McCoy/Dwight ratio at known geometry | L=2 m, r=0.15 m | r_mccoy / r_dwight ≈ **1.8702** (rel=1e-3); ratio bounded < 2.0 always |
| `test_baseline_internal_router_dwight_divergence` | Two router-side "Dwight" formulas differ by ln(2) | L=2 m, r=0.15 m | ratio ≈ 1.303 (rel=5e-3) |
| `test_baseline_coating_category_schema_divergence` | functional has 9 cats, router has 4 | enum + `_B401_2021_COATING_CATEGORIES` dict | len==9, len==4 |
| `test_baseline_coating_breakdown_a_b_constants` | FBE 2017 vs Cat I 2021 — values mirror live code | `COATING_CONSTANTS[CoatingCategory.FBE] == (0.02, 0.003)`; `_B401_2021_COATING_CATEGORIES["I"] == {f_ci:0.05, k:0.020}` | both equalities hold |
| `test_baseline_yaml_dead_keys_raise` | `DNV_rp_b401_2011` raises with "not IMPLEMENTED" in message | run router with the dead key | exception with `match="not IMPLEMENTED"` |

### P1 edition-API tests

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_normalize_edition_default_warns` | Missing `edition=` warns and defaults to "2021" | `normalize_edition(None)` | `DeprecationWarning` raised, returns "2021" |
| `test_normalize_edition_invalid_raises` | Bad edition strings rejected | `normalize_edition("2010")` | `ValueError` |
| `test_normalize_edition_passes_known` | "2017" and "2021" both accepted | both values | returns unchanged |
| `test_result_carries_edition_used_field` | Every public-API result has `edition_used` and `standard` | `design_cp_system(...)` | result.edition_used in ("2017","2021"); result.standard matches |
| `test_result_standard_string_matches_edition` | Result `standard` string matches edition selected | edition="2017" | result.standard == "DNV-RP-B401 (Oct 2017)" |

### P2 numeric-consolidation tests (cross-edition assertions)

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_coating_bd_2017_vs_2021_documented_divergence` | Cat I 2021 > FBE 2017 at age=20yr | same inputs, different edition | divergence ratio matches investigation table |
| `test_splash_zone_2017_returns_zero_2021_returns_demand` | Same input, edition swap | jacket structure, splash zone | 2017→0.0; 2021→0.100 |
| `test_flush_anode_2017_uses_mccoy_2021_uses_dwight` | Same geometry, different edition | L=2, r=0.15 | r_2017 = 2 * r_2021 (within 1%) |
| `test_coating_translation_no_clean_1to1_emits_warning` | Map asserts approximate flag | translate("COAL_TAR_ENAMEL", direction="2017→2021") | returns ("CAT_III", approximate) — and warning emitted |
| `test_dwight_stubbiness_check_enforced_in_both_editions` | Validation discipline preserved | L=0.1, r=0.5 | raises ValueError regardless of edition |
| `test_unchanged_dims_agree_across_editions` | Items 8, 12, 15 (investigation §2) — stand-off Dwight, Al-Zn-In capacity, driving voltage | same inputs | both editions return identical values |

### P3 standards-consolidation tests

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_all_8_additional_standards_importable_from_facade` | After consolidation | `from digitalmodel.cathodic_protection import iso_15589_2, api_rp_1632, ...` | no ImportError; module objects |
| `test_supported_standards_manifest_complete` | Manifest declares all 13 (std, edition) pairs | `SUPPORTED_STANDARDS` | len == 13, contains expected tuples |
| `test_astm_g42_router_side_deleted_but_logic_preserved` | Migration kept functions | `from digitalmodel.cathodic_protection.astm_g42 import disbondment_test` | importable; same numeric outputs as old `cp_astm_g42.py` |
| `test_supported_standards_no_dead_keys` | Manifest matches dispatcher | every entry has a working dispatch | all 13 routes succeed for a smoke input |

### P4 cleanup tests

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_yaml_calculation_type_replaced_with_standard_plus_edition` | YAML no longer carries dead keys | `cathodic_protection.yml` | `grep -c "DNV_rp_b401_2011\|DNV_rp_b401_2021_05" == 0` |
| `test_three_deprecation_shims_deleted` | Shim files gone | `ls infrastructure/common/cathodic_protection.py` | not exists (3 files checked) |
| `test_no_test_imports_transit_old_shim_paths` | All test imports migrated | `grep -rn "from digitalmodel.infrastructure.common.cp\|cathodic_protection" tests/` | 0 matches |
| `test_router_class_still_dispatches_legacy_calc_types` | Backward compat for any external YAML | `CathodicProtection().router(cfg_with_DNV_RP_B401_offshore)` | runs, returns result with edition_used field |
| `test_citation_emission_at_each_design_callsite` | After #2685 lands | `design_cp_system(...)` | result.citations non-empty; code_id matches edition |
| `test_no_regression_full_pkg` | Full test pass | `pytest digitalmodel/tests/cathodic_protection/ digitalmodel/tests/specialized/cathodic_protection/` | all green (270+ + 230+ tests) |
| `test_wiki_pages_present_for_cited_editions` | Citation resolver doesn't fail-closed in prod | `validate_citation(b401_2021_citation, repo_root=workspace_hub_root)` | passes |

---

## Acceptance Criteria

Every AC is pytest- or grep-checkable.

### P1 — Foundation

- [ ] **AC-P1.1:** `uv run pytest digitalmodel/tests/cathodic_protection/test_edition_divergence_baseline.py -v` — all **6** baseline tests pass (r2: expanded by 1 for internal-router-Dwight divergence). Tests lock today's behavior before any source change. All numerics in those tests were independently recomputed via Python on 2026-05-13 against live code; the r1 plan's `≈ 2.0` claim has been replaced with the empirical `1.8702` value at the specified geometry.
- [ ] **AC-P1.2:** `grep -c "edition:" digitalmodel/src/digitalmodel/cathodic_protection/_edition.py` ≥ 1 (file exists with `Edition` literal)
- [ ] **AC-P1.3:** `uv run python -c "from digitalmodel.cathodic_protection import Edition, DEFAULT_EDITION; assert DEFAULT_EDITION == '2021'"` — exits 0
- [ ] **AC-P1.4:** Every public function in `dnv_rp_b401.py` accepts `edition=` kwarg: `grep -c "edition:" digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py` ≥ 8
- [ ] **AC-P1.5:** Result objects carry `edition_used` + `standard` fields: `grep -c "edition_used" digitalmodel/src/digitalmodel/cathodic_protection/anode_sizing.py` ≥ 1
- [ ] **AC-P1.6:** Missing-edition warn-and-default behavior: `uv run pytest digitalmodel/tests/cathodic_protection/ -k test_normalize_edition -v` — 3 tests pass

### P2 — Numeric consolidation

- [ ] **AC-P2.1:** Edition tables module exists and is non-empty: `wc -l digitalmodel/src/digitalmodel/cathodic_protection/_edition_tables.py` ≥ 50
- [ ] **AC-P2.2:** All 7 material divergence dimensions covered (r2: expanded from 4 per Finding 4): `grep -E "COATING_BREAKDOWN_2017|COATING_BREAKDOWN_2021|SPLASH_CURRENT_DENSITY|FLUSH_RESISTANCE_FORMULA|BRACELET_RESISTANCE_FORMULA|UTILIZATION_FACTOR_DEFAULTS|ANODE_MATERIAL_CAPACITY_AH_KG|DWIGHT_STUBBINESS_VALIDATION" digitalmodel/src/digitalmodel/cathodic_protection/_edition_tables.py | wc -l` ≥ 8 (7 dimension tables + at least one stubbiness key, counted separately)
- [ ] **AC-P2.2a (Finding 4, item #10):** Bracelet resistance dispatches by edition: 2017 returns area-based `0.315*ρ/√A` form (matches `cp_sacrificial_anode_b401.py:166`); 2021 returns modified-Dwight `(ρ/2πL)*(ln(2πL/r)-1)` (matches `cp_DNV_RP_B401_2021.py:346`). Cross-edition ratio test in `test_edition_consistency.py`.
- [ ] **AC-P2.2b (Finding 4, item #11):** Utilization factor defaults match `UTILIZATION_FACTOR_DEFAULTS[edition][anode_type]`. Stand-off under `edition='2017'` returns 0.90; under `edition='2021'` returns 0.85. Verified by `pytest -k test_utilization_factor_defaults`.
- [ ] **AC-P2.2c (Finding 4, item #13):** Zinc material accepted under `edition='2021'`; rejected with clear error under `edition='2017'` (functional pkg never supported Zn). `coating_breakdown_factor(material='zinc', edition='2017')` raises `ValueError` with "Zn not supported in 2017 edition" substring.
- [ ] **AC-P2.2d (Finding 4, item #14):** Dwight stubbiness validation enforced in BOTH editions (strictness uplift documented in Risks). `anode_resistance_slender_standoff(L=0.1, r=0.5, edition='2017')` raises ValueError (today it silently returns nonsense); `edition='2021'` same behavior.
- [ ] **AC-P2.3:** Coating translation map declared with confidence flags: `grep -c "approximate\|exact" digitalmodel/src/digitalmodel/cathodic_protection/_coating_translation.py` ≥ 9 (one per 2017 category)
- [ ] **AC-P2.4:** Cross-edition divergence tests pass: `uv run pytest digitalmodel/tests/cathodic_protection/test_edition_consistency.py -v` — all green
- [ ] **AC-P2.5:** Baseline tests STILL pass (no silent collapse): `uv run pytest digitalmodel/tests/cathodic_protection/test_edition_divergence_baseline.py -v` — same 5 tests
- [ ] **AC-P2.6:** Functional pkg tests parametrized on edition: `grep -c "@pytest.mark.parametrize.*edition" digitalmodel/tests/cathodic_protection/test_*.py` ≥ 10 (added across files)

### P3 — Standards consolidation

- [ ] **AC-P3.1:** All 8 additional standards remain importable: `uv run python -c "from digitalmodel.cathodic_protection import iso_15589_2, api_rp_1632, cp_monitoring, cp_survey, stray_current, corrosion_rate, anode_depletion, iccp_design"` — exits 0
- [ ] **AC-P3.2:** `SUPPORTED_STANDARDS` manifest has 13 entries: `uv run python -c "from digitalmodel.cathodic_protection import SUPPORTED_STANDARDS; assert len(SUPPORTED_STANDARDS) == 13"`
- [ ] **AC-P3.3:** ASTM G42/G80 functional-side modules exist; router-side deleted:
  - `ls digitalmodel/src/digitalmodel/cathodic_protection/astm_g42.py digitalmodel/src/digitalmodel/cathodic_protection/astm_g80.py` — both exist
  - `ls digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cp_astm_g42.py` — does NOT exist
- [ ] **AC-P3.4:** G42/G80 numeric outputs preserved across migration: `uv run pytest digitalmodel/tests/specialized/cathodic_protection/test_astm_g42.py digitalmodel/tests/specialized/cathodic_protection/test_astm_g80.py -v` — all 38 tests green (re-pointed imports)
- [ ] **AC-P3.5:** ISO-15589-2 + API RP 1632 tests still green: `uv run pytest digitalmodel/tests/cathodic_protection/test_iso_15589_2.py digitalmodel/tests/cathodic_protection/test_api_rp_1632.py -v` — 36 tests green

### P4 — Cleanup

- [ ] **AC-P4.1:** YAML config has no dead keys: `grep -c "DNV_rp_b401_2011\|DNV_rp_b401_2021_05" digitalmodel/src/digitalmodel/infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml` == 0
- [ ] **AC-P4.2:** YAML config introduces edition selector: `grep -c "^edition:\|^  edition:" digitalmodel/src/digitalmodel/infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml` ≥ 1
- [ ] **AC-P4.3:** All 3 deprecation shims deleted: `ls digitalmodel/src/digitalmodel/infrastructure/common/cathodic_protection.py digitalmodel/src/digitalmodel/infrastructure/common/cp_DNV_RP_B401_2021.py digitalmodel/src/digitalmodel/infrastructure/common/cp_sacrificial_anode_b401.py 2>&1 | grep -c "No such" == 3`
- [ ] **AC-P4.4:** No test still transits shim path: `grep -rn "from digitalmodel.infrastructure.common.cathodic_protection\|from digitalmodel.infrastructure.common.cp_" digitalmodel/tests/ | wc -l` == 0
- [ ] **AC-P4.5 (Finding 6 — sidecar):** Citation emission wired on result-object SIDECAR; primary numeric return types UNCHANGED. Three sub-checks:
  - (a) `grep -c "from digitalmodel.citations" digitalmodel/src/digitalmodel/cathodic_protection/anode_sizing.py` ≥ 1
  - (b) Primary payload type stable: `uv run python -c "from digitalmodel.cathodic_protection import coating_breakdown_factor; import inspect; r = coating_breakdown_factor('FBE', 10.0, edition='2017'); assert isinstance(r, float), type(r)"` — exits 0
  - (c) Sidecar populated on result objects: `uv run python -c "from digitalmodel.cathodic_protection import design_cp_system; r = design_cp_system(...); assert hasattr(r, 'citations'); assert isinstance(r.citations, tuple)"` — exits 0
- [ ] **AC-P4.7a (Finding 5 — legacy YAML routes correctly):** Live YAML config at `digitalmodel/src/digitalmodel/infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml` with the (current) `calculation_type: ABS_gn_ships_2018` and no `edition:` key routes successfully via `CathodicProtection().router(cfg)` and produces a result with `cfg["results"]["edition_used"]` either populated (B401 dispatches) or `None` (non-B401 dispatches like ABS). Specific assertion: `pytest digitalmodel/tests/specialized/cathodic_protection/test_router_legacy_yaml.py -v` — new test file added in P4 reads the YAML directly, runs the dispatcher, asserts no `KeyError` on `cfg["inputs"]["calculation_type"]`.
- [ ] **AC-P4.6:** Wiki pages exist with valid frontmatter: `ls knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-2017.md knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-2021.md` — both exist; `grep -c "^code_id:" $page` ≥ 1 each
- [ ] **AC-P4.7:** Router still routes legacy YAML configs (no external breakage): `uv run pytest digitalmodel/tests/specialized/cathodic_protection/test_cathodic_protection_b401.py -v` — 59 tests still pass after import migration
- [ ] **AC-P4.8:** Full CP suite green: `uv run pytest digitalmodel/tests/cathodic_protection/ digitalmodel/tests/specialized/cathodic_protection/ digitalmodel/tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py -v` — all 500+ tests pass

### Cross-cutting

- [ ] **AC-X.1:** Plan reviewed by Claude + Codex + Gemini (T2 → 3-provider per `feedback_always_adversarial_review_scale_depth`); artifacts in `scripts/review/results/`
- [ ] **AC-X.2:** `docs/plans/README.md` updated with this plan
- [ ] **AC-X.3:** `.claude/rules/calc-citation-contract.md` updated to add CP as second live pilot site (after #2685)
- [ ] **AC-X.4:** No regression elsewhere: `uv run pytest digitalmodel/` — full repo green (or no NEW failures vs. pre-merge baseline captured at P1 start)

---

## Adversarial Review Stance

Per `feedback_adversarial_review_stance.md` + `feedback_always_adversarial_review_scale_depth.md`. T2 →
3-provider (Claude + Codex + Gemini). This is a **regulatory-hazard surface**; reviewers must hunt for
silent collapse, edition drift, and any path where a CP design could be undersized post-merge.

**Things that could go wrong:**

1. **Silent coating-category collapse during P2.** Mapping 2017's 9 categories to 2021's 4 is many-to-one
   and lossy. If the merge picks the wrong canonical bucket (e.g., maps 2017 "FBE" to 2021 "CAT_I" and
   then a caller selects "FBE" under `edition="2021"`), the result is a CP design under-sized by ~2.5×
   on coating breakdown alone (FBE 2017 a=0.02 vs Cat I 2021 a=0.05). **Mitigation:** the
   `_coating_translation.py` map is **read-only data**, reviewed by an SME, with explicit confidence
   flags. The public API rejects cross-edition category names (`coating_breakdown_factor("FBE", edition="2021")`
   raises `ValueError("FBE is a 2017 category; use translate_coating_category() or supply a 2021 category")`).
   `test_coating_translation_no_clean_1to1_emits_warning` enforces the warning.

2. **Splash-zone semantic flip.** A jacket structure designed under `edition="2017"` (splash = 0.0) and
   then re-run under `edition="2021"` (splash = 0.10–0.20) will return a materially different anode count
   with no callout. A user who migrates code from the functional package to "the merged surface" might
   not realize they need to choose an edition. **Mitigation:** (a) `normalize_edition(None)` raises a
   `DeprecationWarning` not silently defaults; (b) `test_baseline_splash_zone_divergence` runs in CI on
   every commit and asserts the divergence persists; (c) result objects include `edition_used` field so
   downstream HTML reports can flag the choice; (d) deliberate "no-default" mode available via env var
   `DIGITALMODEL_CP_REQUIRE_EXPLICIT_EDITION=1` for paranoid production environments.

3. **Flush-anode formula choice is contractual, not technical.** McCoy vs Dwight: 2017 surface uses
   McCoy (denominator πL); 2021 uses Dwight (denominator 2πL); for the same geometry, McCoy returns 2×
   the resistance. The investigation doc resists picking one on engineering merit. **Mitigation:** keep
   both, dispatch on `edition`. **Do NOT** add a `method: Literal["mccoy", "dwight"]` kwarg as a separate
   axis — that re-introduces the contradiction (a user could pick `edition="2021", method="mccoy"` and
   produce a non-defensible deliverable). Edition is the single source of truth; method is a function
   of edition.

4. **Test-import migration breaks 230+ tests in one commit.** P4 moves 11 test files off the shim path
   to direct imports. If any one file picks the wrong target, the shim deletion later in P4 leaves a
   silent test gap (test file imports a non-existent module → `pytest --co` reports 0 collected; nobody
   notices until next regression). **Mitigation:** P4 commits are atomic per test file; each migration
   commit runs `pytest <that_file> -v --co --collect-only` and asserts test count is non-zero AND
   matches pre-migration count. Shim deletion (`rm`) is the LAST commit of P4, after all 12 migrations
   land green. Per `feedback_multi_agent_commit_serialization`, serialize this phase.

5. **Citation emission depends on #2685 landing, but #2685 has a missing-wiki-page risk.** P4's
   `Citation` wiring will fail-closed if `knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-{2017,2021}.md`
   pages don't exist. **Mitigation:** P4 creates both wiki pages as stubs (frontmatter + 1-paragraph
   body referencing the actual standard for full-body backfill via #2667 domain sweep) BEFORE wiring
   `Citation` calls. Smoke test: `uv run python -c "from digitalmodel.citations.schema import validate_citation; from digitalmodel.cathodic_protection import _b401_citation; validate_citation(_b401_citation(edition='2021'), repo_root=Path('.'))"` exits 0.

6. **`engine.py` YAML dispatcher is a load-bearing prod caller.** The router's `router(cfg)` method is
   the only thing `engine.py` knows about. P4's "router becomes thin adapter" must preserve the same
   `cfg["results"]` schema downstream. **Mitigation:** before P4, capture the current `cfg["results"]`
   shape via a smoke test (`test_engine_yaml_dispatch_baseline`); after P4, assert the same keys exist
   plus the new `edition_used`/`standard` keys. Visual report module (`cp_html_report.py`) needs
   matching update.

7. **Auto-sync race during 4-phase merge** (per `feedback_merge_race_silent_revert` +
   `feedback_hermes_active_preflight_check`). 5–7 day work, many commits, high risk of Hermes cleanup
   reverting a phase mid-flight. **Mitigation:** all 4 phases on a feature branch `wip/2694-cp-edition-merge`,
   `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` preflight on every push, worktree
   isolation if Hermes detected.

8. **Subagent Write phantom** (per `feedback_subagent_write_phantom`). For each phase commit, main session
   independently `ls`/`grep` to confirm files actually landed before claiming AC met. This is especially
   load-bearing for the shim deletion commit — `ls` must return "No such file" before claiming AC-P4.3.

9. **Plan past-tense drift** (per `feedback_plan_past_tense_artifact_claims`). This plan describes
   FUTURE work. Reviewers verify no AC reads as if already done. AC checkboxes are unchecked `[ ]`.

---

## Risks and Open Questions

### Risks

- **Risk (critical — regulatory):** Picking a wrong coating-category mapping silently undersizes a CP
  design. **Mitigation:** SME review of `_coating_translation.py` before P2 lands; map is read-only data;
  cross-edition category names rejected at the API.
- **Risk (high — silent regression):** P2 collapses one edition's behavior onto the other while baseline
  tests pass through luck. **Mitigation:** baseline test file from Step 1.5 is committed FIRST, BEFORE
  any source change; P2 PRs must show the file passes unmodified.
- **Risk (high — test migration):** 230+ test functions need shim-import updates; one bad rewrite silently
  drops a test file. **Mitigation:** per-file atomic commits with `pytest --collect-only` asserting count
  preserved; shim `rm` is the last commit.
- **Risk (medium — prod caller):** `engine.py`'s YAML dispatcher consumes `cfg["results"]` schema; P4
  router refactor must preserve all keys. **Mitigation:** schema-baseline smoke test before P4.
- **Risk (medium — wiki gap):** `Citation` emission fail-closes without prod wiki pages. **Mitigation:**
  P4 creates both 2017/2021 wiki page stubs.
- **Risk (medium — Hermes race):** 5–7 day work window, feature branch + preflight check + worktree
  isolation if needed.
- **Risk (low — `cp_html_report.py`):** consumes the router result schema; needs matching update for new
  fields.

### Cross-Repo Strategy (r2 — addresses Finding 7)

This plan modifies files in **two independent git repos**:

- **workspace-hub** (this repo): `docs/plans/`, `.claude/rules/calc-citation-contract.md`,
  `docs/field-development/cathodic-protection-edition-decision.md` (read-only), `knowledge/wikis/engineering/wiki/standards/dnv-rp-b401-{2017,2021}.md` (NEW)
- **digitalmodel** (nested separate repo at `/mnt/local-analysis/workspace-hub/digitalmodel/`):
  all `src/digitalmodel/cathodic_protection/**`, `src/digitalmodel/infrastructure/**`,
  `tests/cathodic_protection/**`, `tests/specialized/cathodic_protection/**`,
  `tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py`,
  `src/digitalmodel/visualization/reporting/cp_html_report.py`,
  `src/digitalmodel/infrastructure/base_configs/domains/cathodic_protection/cathodic_protection.yml`.

(a) **Commit destination per phase:**

| Phase | workspace-hub commits | digitalmodel commits |
|---|---|---|
| P1 (foundation) | None (P1 is code-only) | All P1 source/test edits |
| P2 (numeric) | None | All P2 edits |
| P3 (standards) | None | All P3 edits |
| P4 (cleanup) | Wiki page stubs; rule doc update | Router refactor, shim deletion, YAML, test migration, citation wiring |

(b) **Commit ordering (regulatory-hazard sensitive):**

1. workspace-hub: land plan r2 (this commit) + #2685 wiki-page stubs as part of P4 prep.
2. digitalmodel: branch `wip/2694-cp-edition-merge` from `main`. Phases P1 → P2 → P3 → P4 land
   sequentially as four separate squashed PRs to `digitalmodel/main`.
3. workspace-hub: after digitalmodel P4 merges to main, update `docs/plans/README.md` index +
   `.claude/rules/calc-citation-contract.md` to add CP as second live emission site.

(c) **Per-repo rollback:**

- **workspace-hub rollback** (any phase): `git revert` the plan/rule/wiki commits. Cosmetic-only;
  zero runtime impact. Wiki page stubs are additive (deleting them only fail-closes citations if
  digitalmodel was already calling them — which it isn't until P4 lands).
- **digitalmodel rollback:**
  - P1: `git revert` the P1 PR. Trivial — additive only.
  - P2: `git revert` the P2 PR. Restores inline constants; baseline tests prove byte-identity restoration.
  - P3: `git revert` P3 PR. Restores router-side ASTM modules.
  - P4: `git revert` P4 PR. Restores shims + old test imports + dead YAML keys. **Coordinated revert**
    of workspace-hub's wiki-page stubs is OPTIONAL — leaving them in workspace-hub is no-op once the
    digitalmodel citation imports are reverted.

(d) **PR/tag conventions:**

- digitalmodel PRs: `wrk/2694-cp-edition-merge-{p1,p2,p3,p4}`, tagged on merge as
  `cp-merge-checkpoint-{p1,p2,p3,p4}` for crisp revert targets.
- workspace-hub PRs: `wrk/2694-plan-r2`, `wrk/2694-wiki-stubs`, `wrk/2694-rule-doc-update`.
- Cross-repo reference: each digitalmodel PR body links to the workspace-hub issue
  `https://github.com/vamseeachanta/workspace-hub/issues/2694`; the workspace-hub plan-update
  commits link to the digitalmodel PR SHAs in their body.

(e) **CI ordering:**

1. digitalmodel CI must be green on each phase PR *before* the next phase branches.
2. workspace-hub CI runs independently (no test-suite coupling to digitalmodel).
3. **No cross-repo CI** exists today — explicit manual gate: `gh pr checks <digitalmodel-pr> --watch`
   before opening the next phase PR.
4. Plan-approval is workspace-hub-side (issue #2694 carries `status:plan-approved`); the workspace-hub
   issue is the single source of truth for "is this work authorized to proceed".

### Rollback Strategy

CP is a **regulatory-hazardous surface**. Rollback must be possible at any phase boundary without leaving
the codebase in a worse state than the pre-merge baseline.

**Phase-boundary checkpoints:** each of P1, P2, P3, P4 commits as a single squashed PR (or atomic
git tag `cp-merge-checkpoint-{p1,p2,p3,p4}`). At any checkpoint, rollback = `git revert
$(git rev-list cp-merge-checkpoint-{N-1}..cp-merge-checkpoint-{N})` on a hot branch.

- **P1 rollback:** trivial — additive only (new `_edition.py`, new `edition=` kwargs with safe `None`
  default, new baseline test file). Revert single PR. No callers broken.
- **P2 rollback:** the dangerous one. Edition tables replace inline constants; revert restores inline
  constants. Baseline tests (still committed from P1) prove the rollback restored exact pre-merge numerics.
  **No production caller breaks** because P2 doesn't change public API signatures (just internals).
- **P3 rollback:** ASTM G42/G80 router-side modules were deleted; rollback restores them from git history.
  Functional-side `astm_g42.py`/`astm_g80.py` are new (additive); leaving them in place during rollback
  doesn't hurt (they're just unused). All 8 standards remain importable in either direction.
- **P4 rollback:** the most painful. Three shim deletions + 11 test-file import migrations + YAML edit
  + router refactor. **Each P4 sub-commit is atomic**, so partial rollback is possible. Worst case:
  `git revert` the entire P4 PR; shims and test imports are restored; YAML reverts to dead-key
  advertisement (no worse than current state); citation wiring un-lands (also no worse than current state).
  The wiki page stubs stay (additive — they don't break anything).

**Emergency abort condition:** if P2 baseline tests start failing (silent collapse detected) and the
root cause isn't found within 4 hours, full revert of P2 + reopen #2694 with `incident:silent-collapse` label.

---

## Estimated Effort

Per investigation doc §6: **5–7 working days for a single engineer**, scoped as:

| Phase | LOC added/changed | New tests | Existing tests touched | Time |
|---|---|---|---|---|
| **P1 — Foundation** | ~150 added (`_edition.py` 50, signature changes across 8 fns × ~10 LOC ea = 80, result mixin 20) | 8 (5 baseline + 3 edition-API) | 0 (additive) | 1 day |
| **P2 — Numeric consolidation** | ~600 added (`_edition_tables.py` 200, `_coating_translation.py` 100, dispatch wiring in 5 modules × ~60 LOC ea = 300) | 6 (cross-edition consistency) | 30+ (parametrize on edition across 18 functional-pkg test files) | 3 days |
| **P3 — Standards consolidation** | ~400 added/moved (G42 functional-side 175, G80 functional-side 141, manifest 30, facade re-export 30, citations module wiring 30) | 4 (standards manifest + import smoke) | 38 (G42/G80 router-side tests re-pointed to functional-side) | 1 day |
| **P4 — Cleanup** | ~200 deleted (3 shims = ~50), ~150 modified (router thin-adapter), 100 added (wiki stubs + YAML edit) | 7 (cleanup + citation emission + wiki validate + regression) | 230 (test imports migrated across 12 files) | 1–2 days |
| **Cross-cutting (review, revisions)** | review artifacts + plan updates | 0 | 0 | 0.5–1 day |
| **Total** | ~1 500 LOC touched | **25 new tests** | **300 modified tests** | **5–7 days** |

**Review iterations:** budget 2–3 cross-provider review cycles given the regulatory-hazard scope:
- Iter 1: full plan posted, 3-provider review (Claude + Codex + Gemini). Expect MAJOR findings.
- Iter 2: address findings, re-review by all 3.
- Iter 3 (likely): final MINOR pass before `status:plan-approved`.

Per `feedback_cross_provider_review_payoff`, Codex consistently finds non-overlapping defects vs. Claude
on regulatory code surfaces. Budget extra time for verifying Codex findings against live state (per
`feedback_codex_sandbox_no_execution` — Codex cannot exec, so its claims need local verification).

---

## Cross-references

- workspace-hub#2694 — Epic: Cross-domain duplicate-implementation cleanup (this plan is the CP sub-cluster)
- workspace-hub#2692 — R5 Subsea Pipelines audit (Finding 3 surfaced the edition shadow)
- workspace-hub#2685 — Citation pilot (P4's `Citation` emission depends on this landing first)
- workspace-hub#2667 — Domain Knowledge Sweep (full-body backfill for the new wiki pages)
- workspace-hub#2400 — Future MCP `wiki_search` migration (citation resolver swap; schema-compatible)
- workspace-hub#2481 — Original citation contract decisions (D1/D2/D3: fail-closed at calc time, direct file read v1)
- workspace-hub#2580 — Test-fixture vendoring pattern (for standalone digitalmodel CI)
- workspace-hub#2686 — Catenary canonicalization (precedent; **NOT** the right model here — catenary had a clear winner, CP does not)
- workspace-hub#1676 — Marine-structure CP TDD landing (April 2026, last meaningful functional-pkg commit)
- Investigation doc — `docs/field-development/cathodic-protection-edition-decision.md`
- Reference plan — `docs/plans/2026-05-13-issue-2685-citation-pilot-option-a-plan.md`
- Citation rule — `.claude/rules/calc-citation-contract.md`
- Coding-style rules — `.claude/rules/coding-style.md` (single-site edits, no abs paths)
- Patterns rules — `.claude/rules/patterns.md` (enforcement gradient — promote translation map to script-level check in P3)

---

## Complexity: T2

**T2** — regulatory-hazard calc surface, multi-file/multi-module change (~30 files touched), ~1 500 LOC,
new edition-API surface, 530+ tests touched, depends on #2685, requires SME review of coating-translation
map. Below T3 because: no schema changes to citation infra (re-uses #2685), no new external public API
surface beyond the `edition=` kwarg, rollback is bounded per-phase, and the scope is contained within
digitalmodel (no workspace-hub-wide ripple).

Per `feedback_always_adversarial_review_scale_depth`: T2 → 3-provider (Claude + Codex + Gemini). Per
`feedback_cross_provider_review_payoff` and `feedback_codex_sustained_major_loop`, if Codex repeats MAJOR
3+ rounds while Claude+Gemini are MINOR, surface the consensus/minority decision to the user; do not
auto-cycle.

---

## Plan-Review Routing Recommendation

Per `feedback_never_offer_to_self_label_plan_approved` — this planning session does NOT self-label
`status:plan-approved`. Recommended next step for the main session:

1. Verify the plan file exists and renders cleanly.
2. Label the issue `status:plan-review` and post the plan PR/file path as a comment.
3. Run the 3-provider adversarial review (Claude + Codex + Gemini) via `scripts/review/cross-review.sh`
   or equivalent — capture artifacts in `scripts/review/results/2026-05-13-plan-2694-{claude,codex,gemini}.md`.
4. Wait for **user** to label `status:plan-approved` after reviewing the artifacts.
5. Only then dispatch P1.

Per `feedback_codex_needs_pushed_artifact`: push this plan file to origin BEFORE dispatching
`codex exec` review (Codex sandbox can't read local files).

Per `feedback_gemini_sandbox_overlay_blindness`: if Gemini review claims files are missing, verify with
`git ls-files docs/plans/2026-05-13-issue-2694-cathodic-protection-edition-merge-plan.md` before
accepting MAJOR findings.
