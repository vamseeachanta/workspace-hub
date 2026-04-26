# Plan for aceengineer-strategy #5: Public Mooring Quick-Screen Calculator

> **Status:** draft v2 (post-r3 patch addressing 5 MAJOR + 4 MINOR findings)
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/aceengineer-strategy/issues/5
> **Parent epic:** https://github.com/vamseeachanta/aceengineer-strategy/issues/1
> **Review artifacts:** scripts/review/results/2026-04-26-plan-aces-5-claude.md (v1 review, MAJOR; this v2 plan patches all 5 MAJOR findings + 4 MINORs inline)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (454 lines, verified 2026-04-26 via `wc -l`). Public API:
  - **Functions:** `solve_catenary()` (line 155), `estimate_line_length()` (line 410), `calculate_pretension()` (line 433)
  - **Data models:** `MooringPattern` enum (line 27), `SegmentMaterial` enum (line 34), `MooringMaterialProperties` (line 52), `CatenaryResult` (line 143), `MooringLineSegment` (line 253), `MooringLineDesign` (line 259), `SpreadMooringConfig` (line 324), `TurretMooringConfig` (line 376)
  - Module docstring explicitly cites: "API RP 2SK: Design and Analysis of Stationkeeping Systems", "DNV-OS-E301: Position Mooring"
  - Citation hooks already present in code: API RP 2SK Table C-1 (line 55), Section 5 (lines 262, 327), Section 5.4 (line 379)
  - **NOT** dependent on OrcFxAPI — pure analytical/numerical (per docstring line 8) — clean to port to JS without licensed-binary dependency
- Found: `digitalmodel/src/digitalmodel/citations/` infrastructure with `registry.py` and `schema.py` (per workspace-hub #2481 calc-citation contract — completed) — the `code_id` resolver lives here. Calculator's citation panel can use this contract directly.
- Found: `digitalmodel/src/digitalmodel/orcaflex/viv_screening.py` provides the established screening-pattern (`*_screening()` function returning `screening_pass: bool` + structured result). Mooring calculator follows same pattern.
- Gap: no existing mooring-specific screening function yet wraps `solve_catenary` + `calculate_pretension` for "single-shot screening with pass/fail and citations."

### Existing aceengineer-website calculator patterns

- Found: `aceengineer-website/calculators/` directory with 4 prior calculators (verified 2026-04-26 via `ls`):
  - `fatigue-life-calculator.html`
  - `fatigue-sn-curve.html`
  - `npv-field-development.html`
  - `index.html` (collection index)
- Found: `aceengineer-website/assets/js/` JS-engine pattern (verified 2026-04-26):
  - `npv-calculator-engine.js`
  - `obs-calculator-engine.js`
  - `wall-thickness-engine.js`
  - Pattern: pure-JS port of the Python module; HTML page imports the engine + uses Plotly for viz
- Found: `plotly-2.32.0.min.js` (vendored locally, plus SHA256 + LICENSE) — visualization pattern is locked
- Found: `aceengineer-website/build.js` is a posthtml-based static-site build (verified head -30); calculators are static HTML pages, NOT SPA / NOT backend-served. JavaScript runs client-side; no server-side compute needed for the public tier.
- Found: existing calculators use JSON-LD `WebApplication` structured-data schema for SEO + Google Analytics + shared `styles.min.css` + `navbar-toggle.js`. New calculator must inherit all four for consistency.

### Standards

| Standard | Status | Source |
|---|---|---|
| DNV-OS-E301 (Position Mooring) | gap (Phase 2 of [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4)) | Will be cited via `code_id` placeholders that resolve once Phase 2 populates the canonical home; SKIP-mode citation panel until then |
| API RP 2SK (Stationkeeping Systems) | gap (Phase 2 of [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4)) | Same |
| `digitalmodel.orcaflex.mooring_design` line-level citations | present in source | Source-code text references will populate calculator's citation block as fallback when `code_id` not yet resolvable |

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/wiki/standards/` does not yet exist (verified — Phase 2 of [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) creates it). Calculator's `code_id` references resolve to fallback text until Phase 2 lands.
- `knowledge/wikis/marine-engineering/CLAUDE.md` is the schema authority — `code_id` format `<publisher>-<code>-<clause>` is locked there per [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) §3.

### Documents consulted

- aceengineer-strategy issue [#5](https://github.com/vamseeachanta/aceengineer-strategy/issues/5) (this issue's body) — public-by-default policy, lead-capture CTA, branding question (AceEngineer vs research-brand subsidiary).
- [`docs/governance/flywheel-wedge-decision.md`](../governance/flywheel-wedge-decision.md) — locks mooring as the wedge.
- [`docs/governance/flywheel-icp-decision.md`](../governance/flywheel-icp-decision.md) — Operators ICP; calculator's CTA framing should target operator-team workflow.
- [`docs/governance/offshore-marine-standards-canonical-home.md`](../governance/offshore-marine-standards-canonical-home.md) §3 — `code_id` schema this calculator uses.
- aceengineer-strategy [#1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1) epic — public-by-default policy, "free-by-client-preference" model.
- SemiAnalysis Die Yield Calculator (semianalysis.com, fetched earlier in session) — comparable lead-magnet pattern.

### Gaps identified

- No existing `mooring_quick_screen()` wrapper function — must be created in `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (or a sibling file) to provide a single-shot entry point composing `solve_catenary` + `calculate_pretension` + screening pass/fail.
- No JS port of the catenary equation — must be written. The catenary function is closed-form; JS port is straightforward (no scipy dependency).
- No citation-display component pattern in existing calculators — must be added (this calculator is the first to cite via `code_id`; subsequent calculators inherit the pattern).
- No lead-capture form integration on existing aceengineer-website — must be added (existing calculators don't lead-capture; we're introducing the pattern). Specifically: where does form submission go? Mailchimp, HubSpot, custom backend, mailto:?
- Branding: open question per issue body — AceEngineer-branded or separate research-brand subdomain?

### Evidence (embedded verification)

**Issue states** (verified 2026-04-26 via `gh issue view`):
- aceengineer-strategy `#5` — OPEN — "[P1] Public mooring quick-screen calculator"
- aceengineer-strategy `#1` — OPEN (epic, public-by-default policy locked)
- aceengineer-strategy `#4` — OPEN, `status:plan-approved` — Phase 1 LOCKED, Phase 2 PENDING (relevant: standards `code_id` resolution depends on Phase 2)

**File existence** (`ls` 2026-04-26):
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (454 lines)
- EXISTS: `digitalmodel/src/digitalmodel/citations/{registry.py,schema.py}`
- EXISTS: `aceengineer-website/calculators/{fatigue-life-calculator.html,fatigue-sn-curve.html,npv-field-development.html,index.html}`
- EXISTS: `aceengineer-website/assets/js/{npv-calculator-engine.js,obs-calculator-engine.js,wall-thickness-engine.js,plotly-2.32.0.min.js}`
- EXISTS: `aceengineer-website/build.js` (posthtml-based static build)
- MISSING (this plan creates): `aceengineer-website/calculators/mooring-quick-screen.html`
- MISSING (this plan creates): `aceengineer-website/assets/js/mooring-calculator-engine.js`
- MISSING (this plan creates): `digitalmodel/src/digitalmodel/orcaflex/mooring_quick_screen.py` (Python wrapper for parity / future server-side option)

**Source count:** 7 distinct sources above.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-26-aces-5-flywheel-mooring-quick-screen-calculator.md` |
| Calculator HTML page | `aceengineer-website/calculators/mooring-quick-screen.html` |
| Calculator JS engine | `aceengineer-website/assets/js/mooring-calculator-engine.js` |
| Python wrapper (parity, optional server-side) | `digitalmodel/src/digitalmodel/orcaflex/mooring_quick_screen.py` (cross-repo per #2481 cherry-pick precedent) |
| JS engine unit tests | `aceengineer-website/assets/js/mooring-calculator-engine.test.js` (or equivalent test runner per existing convention — audit during execution) |
| Python wrapper unit tests | `digitalmodel/tests/orcaflex/test_mooring_quick_screen.py` (cross-repo) |
| Updated calculators index | `aceengineer-website/calculators/index.html` (add mooring screening to collection) |
| Plan review — Claude | `scripts/review/results/2026-04-26-plan-aces-5-claude.md` |
| Plan review — Codex | DEFERRED (codex-cli 0.124.0 upstream regression) |
| Plan review — Gemini | RECOMMENDED — calculator is a real implementation (not strategy doc); Gemini cross-review adds value especially on JS-port arithmetic correctness |

---

## Deliverable

A public mooring quick-screen calculator at `https://aceengineer.com/calculators/mooring-quick-screen.html` that: (a) takes vessel class + water depth + environmental severity + line configuration as inputs, **for SPREAD MOORING ONLY in v1** (per F4 patch — TURRET and CALM out of scope for v1; UI explicitly indicates "Spread mooring screening — see follow-on calculators for turret / CALM"), (b) computes indicative line tensions, anchor radius, factor of safety **for INTACT condition only in v1** (per F5 patch — damaged-condition analysis requires line-redistribution simulation which is integration-tier scope per [aces-#7](https://github.com/vamseeachanta/aceengineer-strategy/issues/7); UI explicitly indicates "Quick screen: intact condition. For damaged-condition analysis, see institutional tier") per API RP 2SK / DNV-OS-E301 client-side via JS port of `digitalmodel.orcaflex.mooring_design`, (c) renders results with Plotly v2.32.0 (vendored — per F6 patch) visualization (catenary profile + tension vs offset), (d) cites relevant standards clauses with `code_id` resolving via build-time inlining (per F3 patch — see §Citation Resolution Mechanism below), (e) captures leads via `mailto:tools@aceengineer.com?subject=Mooring%20Calculator%20Institutional%20Tier%20Inquiry` CTA stub (per F7 patch). Numerical parity with the Python module enforced by a 10-case reference fixture committed to the repo (per F2 patch — see §Files to Change).

---

## Pseudocode (v2 — INTACT-ONLY screening, damaged-condition deferred to integration tier per F5 patch)

```
# Phase-1 execution preflight (per F9 patch): read actual Python signatures
function preflight():
    inspect digitalmodel.orcaflex.mooring_design.solve_catenary signature
    inspect digitalmodel.orcaflex.mooring_design.calculate_pretension signature
    document any deviation between Python signature and JS port in code comment block

# JS engine (mooring-calculator-engine.js) — INTACT-only quick screen
function solveCatenary(input):
    # Closed-form catenary equation; mirrors digitalmodel.orcaflex.mooring_design.solve_catenary
    # JS signature MUST match Python wrapper input model (per F9). If Python uses a pydantic
    # model `CatenaryInput`, JS receives an equivalent object; deviations are documented inline.
    a = input.horizontalForce / input.lineWeight  # catenary parameter
    suspended_length = sqrt(2 * a * input.waterDepth + input.waterDepth^2)
    horizontal_distance = a * acosh(1 + input.waterDepth / a)
    top_tension = input.horizontalForce + input.lineWeight * input.waterDepth
    return { suspended_length, horizontal_distance, top_tension, catenary_a: a }

function calculatePretension(input):
    # INTACT only in v1; damaged-condition deferred to integration tier per F5 patch
    pretension_intact = input.designTensionMBL / input.safetyFactorIntact
    return { pretension_intact }

function mooringQuickScreen(inputs):
    # SPREAD MOORING + INTACT CONDITION ONLY (v1 scope per F4, F5 patches)
    if inputs.pattern !== "spread":
        return { error: "v1 supports spread mooring only; turret/CALM coming in follow-on calculators", screening_pass: null }
    catenary = solveCatenary(inputs)
    pretension = calculatePretension(inputs)
    fos_intact = inputs.lineMBL / catenary.top_tension
    pass_intact = fos_intact >= 1.67  # API RP 2SK Section 5 intact-condition floor
    return {
        screening_pass: pass_intact,
        condition: "intact",  # v1 scope marker
        catenary, pretension, fos_intact,
        damaged_condition: {
            available: false,
            reason: "Damaged-condition analysis requires line-redistribution simulation; available in integration tier — see https://github.com/vamseeachanta/aceengineer-strategy/issues/7"
        },
        citations: [
            { code_id: "api-rp-2sk-5.0", clause: "Factor of Safety — Intact Condition (1.67 floor)", value: fos_intact },
            { code_id: "dnv-os-e301-3.5.2", clause: "Position Mooring ULS" }
        ]
    }

# Build-time citation resolver (per F3 patch — locked mechanism)
# Implemented as a posthtml plugin invoked by aceengineer-website/build.js.
# At build time, the resolver scans `data-code-id="..."` attributes in the HTML
# and looks them up in workspace-hub knowledge/wikis/marine-engineering/wiki/standards/.
# If aces-#4 Phase 2 has landed: inline resolved URL `https://aceengineer.com/wiki/standards/<publisher>/<code-id>/`
# If Phase 2 has NOT landed: inline fallback text "(citation pending — see plan aces-#4 Phase 2)"
# This avoids runtime fetch, no client-side latency, no CORS, no live llm-wiki dependency.
function buildTimeResolveCodeId(codeId):
    page_path = lookup_in_wiki_standards_tree(codeId)
    if page_path exists:
        return { resolved: true, url: `/wiki/standards/${publisher}/${codeId}/` }
    else:
        return { resolved: false, fallback_text: `${codeId} (citation pending — see plan aces-#4 Phase 2)` }
```

```
# Python wrapper (mooring_quick_screen.py — parity surface)
def mooring_quick_screen(inputs: MooringQuickScreenInput) -> MooringQuickScreenResult:
    # SPREAD + INTACT only (parity with JS v1 scope)
    if inputs.pattern != MooringPattern.SPREAD:
        raise NotImplementedError(
            "v1 supports spread mooring only; turret/CALM in follow-on. "
            "See aceengineer-strategy issue #5 plan v2."
        )
    catenary = solve_catenary(...)
    pretension = calculate_pretension(...)  # intact only
    # ... same logic as JS engine, returning pydantic model with citation registry refs
    return MooringQuickScreenResult(
        screening_pass=...,
        condition="intact",
        catenary=catenary,
        pretension=pretension,
        citations=[CitationRef(code_id="api-rp-2sk-5.0", ...)],
        damaged_condition=DamagedConditionRef(available=False, reason="integration tier scope — aces-#7"),
    )
```

---

## Citation Resolution Mechanism (NEW — F3 patch, locked)

The calculator uses **build-time inlining** of `code_id` references, NOT runtime fetch. Implementation:

1. HTML page uses `data-code-id="api-rp-2sk-5.0"` attributes on citation spans (and matching attribute on JS-emitted citation panel entries).
2. `aceengineer-website/build.js` is extended with a new posthtml plugin (`posthtml-resolve-code-id`) that runs during the static-site build. The plugin:
   - For each `data-code-id` attribute, looks up the matching page in `knowledge/wikis/marine-engineering/wiki/standards/<publisher>/<code-id>/` (workspace-hub repo, sibling to aceengineer-website checkout).
   - If found (i.e., [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) Phase 2 has populated): replaces the span with an `<a href="/wiki/standards/<publisher>/<code-id>/">` link.
   - If not found (Phase 2 not yet landed): replaces with a `<span class="citation-pending">` with fallback text "(citation pending — see plan aces-#4 Phase 2)".
3. The JS engine emits citation entries with `data-code-id` attributes that are resolved at the same build step (build.js processes engine output too, OR engine emits placeholders that posthtml resolves on next build).
4. SKIP semantics (per acceptance): build succeeds either way; if Phase 2 not landed, calculator ships with all citations in fallback-text mode and upgrades automatically when Phase 2 lands and aceengineer-website rebuilds.

**Rationale:** runtime fetch would introduce CORS, latency, cache-staleness, offline-fail. Build-time inlining is deterministic, fast (build-once), and unaffected by user network conditions.

---

## JS Test Runner (NEW — F1 patch, locked)

**Phase-1 execution preflight:** audit `aceengineer-website/` for any existing `*.test.js`, `package.json` test config, or vitest/jest/mocha references.

**If existing convention is found:** use it for the new `mooring-calculator-engine.test.js`. Plan executor records the discovered runner in a comment block at the top of the test file.

**If no existing convention is found** (likely outcome — the existing JS engines have no co-located test files): **introduce Vitest** (v1.x). Rationale: smallest-footprint modern JS test runner; no transformer/Babel setup required; supports ES modules natively; test files run via `npx vitest run` with no global install. Add to `aceengineer-website/package.json` (or create one if it doesn't exist):

```json
{
  "devDependencies": { "vitest": "^1.0.0" },
  "scripts": { "test": "vitest run" }
}
```

Lock-in: this calculator establishes the JS-testing convention for aceengineer-website. Subsequent calculators inherit Vitest unless explicitly overridden.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `aceengineer-website/calculators/mooring-quick-screen.html` | Calculator HTML page (follows pattern of fatigue-life-calculator.html); spread+intact only per F4/F5 patches; uses `data-code-id` attributes for build-time citation resolution (F3) |
| Create | `aceengineer-website/assets/js/mooring-calculator-engine.js` | JS engine (port of Python module; closed-form catenary needs no external deps; spread+intact only); **imports `../assets/js/plotly-2.32.0.min.js` (the vendored copy, NOT CDN — per F6 patch)** |
| Create | `aceengineer-website/assets/js/mooring-calculator-engine.test.js` | Unit tests for JS engine (parity vs reference Python outputs); **runs via Vitest per F1 patch** |
| Create | `aceengineer-website/calculators/test-fixtures/mooring-quick-screen-reference.json` | **NEW per F2 patch.** 10 input/output reference cases generated by Python wrapper (water_depth ∈ {500, 1000, 1500, 2500, 3000} × line_count ∈ {8, 12} × material ∈ {chain_R4, polyester} = 20 combinations; pick 10 covering the ranges; plus 1 edge case at minimum FoS). Generated via `python -m digitalmodel.orcaflex.mooring_quick_screen --emit-fixture > <path>` (CLI hook to be added in the wrapper); committed alongside fixture-generation script. |
| Create | `aceengineer-website/scripts/posthtml-resolve-code-id.js` | **NEW per F3 patch.** Build-time citation-resolver posthtml plugin; scans `data-code-id` attributes, looks up in workspace-hub `knowledge/wikis/marine-engineering/wiki/standards/`, inlines resolved URL or fallback text. |
| Modify | `aceengineer-website/build.js` | **NEW per F3 patch.** Add `posthtml-resolve-code-id` to the posthtml plugin chain. |
| Create or Modify | `aceengineer-website/package.json` | **NEW per F1 patch.** Add Vitest as devDependency + `test` script if package.json doesn't exist; if it does, add only the missing entries. |
| Modify | `aceengineer-website/calculators/index.html` | Add mooring quick-screen to calculators collection — **append as next position after the highest existing item per F8 patch** (read existing JSON-LD itemListElement array, increment, do NOT hardcode position). |
| Create | `digitalmodel/src/digitalmodel/orcaflex/mooring_quick_screen.py` | Python wrapper (parity surface; future server-side / batch option) — **cross-repo per #2481 precedent** (separate digitalmodel branch + cherry-pick to digitalmodel/main). Includes `--emit-fixture` CLI hook for generating the 10-case reference fixture (F2). Spread + intact only (F4/F5). |
| Create | `digitalmodel/tests/orcaflex/test_mooring_quick_screen.py` | TDD test suite for Python wrapper |
| Create | `aceengineer-website/assets/img/calculators/mooring-calculator-screenshot.png` | Screenshot for JSON-LD `WebApplication.screenshot` field (post-implementation) |
| Update | `docs/plans/README.md` | Add row for this plan |

---

## TDD Test List

### Python wrapper tests (`digitalmodel/tests/orcaflex/test_mooring_quick_screen.py`)

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_quick_screen_passes_nominal_design | screening passes for typical FPSO design | 1500m water depth, 12 lines, 76mm R4 chain, 110t pretension | screening_pass=True, fos_intact ≥ 1.67 |
| test_quick_screen_fails_under_designed | screening fails when MBL too low | as above with 50mm chain | screening_pass=False, fos_intact < 1.67 |
| test_turret_pattern_rejected_in_v1 | per F4 patch, turret pattern rejected in v1 wrapper | pattern=TURRET | raises NotImplementedError with cross-ref to follow-on |
| test_calm_pattern_rejected_in_v1 | per F4 patch, CALM pattern rejected in v1 | pattern=CALM | raises NotImplementedError |
| test_damaged_condition_marked_unavailable | per F5 patch, damaged-condition not computed in v1 | nominal design | result.damaged_condition.available=False, reason cites aces-#7 |
| test_catenary_parity_with_solve_catenary | wrapper output matches direct solve_catenary call | known horizontal_force, line_weight, water_depth | top_tension matches within 1e-6 relative |
| test_pretension_parity_with_calculate_pretension | wrapper output matches direct calculate_pretension call (intact only in v1) | MBL=1500t, FoS=1.67 | pretension_intact matches within 1e-6 relative |
| test_citation_refs_present | result includes API RP 2SK + DNV-OS-E301 code_ids | any input | citations list ≥ 2 with `api-rp-2sk-*` and `dnv-os-e301-*` prefixes |
| test_input_validation_rejects_negative_depth | rejects invalid input | water_depth=-100 | raises ValidationError |
| test_input_validation_rejects_zero_lines | rejects invalid input | num_lines=0 | raises ValidationError |
| test_emit_fixture_cli_produces_valid_json | `python -m digitalmodel.orcaflex.mooring_quick_screen --emit-fixture` produces valid JSON | run CLI | output is parseable, has ≥ 10 cases, each case has input + expected_output keys |

### JS engine tests (`aceengineer-website/assets/js/mooring-calculator-engine.test.js`)

| Test name | What it verifies | Expected behavior |
|---|---|---|
| test_js_python_numerical_parity | JS output matches Python output for ≥10 reference cases | each case: relative error ≤ 1e-4 |
| test_js_input_bounds_checking | UI inputs are bounded | invalid inputs surface error to UI, not silent NaN |
| test_js_screening_pass_fail | screening_pass boolean matches Python | parity for all reference cases |
| test_js_citation_resolver_fallback | when `code_id` lookup fails (Phase 2 of #4 not yet landed), fallback text shown | citation block displays "(citation pending)" suffix |

### HTML page tests (manual UAT)

| Check | Verification |
|---|---|
| Page renders with no console errors | Open in Chrome DevTools, no red errors |
| All JSON-LD valid per Google Rich Results test | https://search.google.com/test/rich-results |
| Plotly visualization renders | Catenary + tension plots visible after Calculate |
| Lead-capture form submits | Email submission works (or surfaces "coming soon" stub if backend not yet wired) |
| Mobile-responsive | Renders on viewport widths 320px to 1920px |

---

## Acceptance Criteria

- [ ] All Python wrapper tests pass: `uv run pytest digitalmodel/tests/orcaflex/test_mooring_quick_screen.py -v` (v1 scope: spread + intact only per F4/F5)
- [ ] All JS engine tests pass: `cd aceengineer-website && npm test` (Vitest per F1 patch)
- [ ] Numerical parity: JS output matches Python output within 1e-4 relative error for the 10 reference cases at `aceengineer-website/calculators/test-fixtures/mooring-quick-screen-reference.json` (F2 patch — fixture committed to repo)
- [ ] No regression: full digitalmodel test suite passes (`uv run pytest digitalmodel/`)
- [ ] No regression: aceengineer-website build completes (`cd aceengineer-website && node build.js`); posthtml-resolve-code-id plugin runs without errors (F3 patch)
- [ ] HTML page passes JSON-LD Rich Results test (https://search.google.com/test/rich-results)
- [ ] Citation panel resolves `code_id` → llm-wiki URL when [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) Phase 2 has landed via build-time inlining (F3); SKIPs cleanly with fallback text otherwise
- [ ] Lead-capture form: ships as mailto: `tools@aceengineer.com` stub per F7 patch; follow-up issue tracks Mailchimp/HubSpot integration
- [ ] **v1 scope guards** (F4/F5): UI explicitly indicates "Spread mooring screening — see follow-on calculators for turret / CALM" AND "Quick screen: intact condition. For damaged-condition analysis, see institutional tier"
- [ ] Plotly imported from `../assets/js/plotly-2.32.0.min.js` (the vendored copy — not CDN per F6 patch); SHA256 hash matches `aceengineer-website/assets/js/plotly-2.32.0.min.js.sha256`
- [ ] Calculator appended to `aceengineer-website/calculators/index.html` JSON-LD `itemListElement` array at next available position (F8 patch — do not hardcode)
- [ ] `docs/plans/README.md` updated
- [ ] aceengineer-strategy issue [#5](https://github.com/vamseeachanta/aceengineer-strategy/issues/5) closure comment cites the deployed URL

---

## Adversarial Review Summary

| Wave | Provider | Verdict | Key findings |
|---|---|---|---|
| v1 | Claude (self-r3) | MAJOR | F1 (JS test runner unspecified), F2 (reference fixture file missing from Files to Change), F3 (citation `resolveCodeId` mechanism hand-waved), F4 (mooring pattern coverage scope not stated for v1), F5 (damaged-condition factor 0.75 fabricated — would publish wrong numbers). 5 MAJOR + 4 MINOR (F6 Plotly version, F7 mailto address, F8 JSON-LD position, F9 signature alignment). See `scripts/review/results/2026-04-26-plan-aces-5-claude.md`. |
| v2 | Claude (self-r3) | MINOR | All 5 MAJOR findings resolved inline; all 4 MINORs addressed. Plan structurally approval-ready pending user review. Independent r3 verdict on the v2 patch: every blocking finding has concrete remediation cited in §Files to Change, §Pseudocode, §Citation Resolution Mechanism, §JS Test Runner, §Acceptance Criteria. |
| — | Codex | UNAVAILABLE | codex-cli 0.124.0 upstream regression #2479 |
| — | Gemini | RECOMMENDED-DEFERRED | T2 implementation; Gemini cross-review adds value on JS-Python numerical-parity arithmetic specifically; deferred until codex-cli regression resolves OR user requests |

**Overall result:** PASS (v2 Claude MINOR; ready for `status:plan-review` label and user review).

## Patch Summary (v1 MAJOR → v2)

| Finding | Severity | Resolution |
|---|---|---|
| F1 — JS test runner unspecified | MAJOR | New §JS Test Runner section locks Vitest with package.json devDependency entry; preflight audit pattern documented |
| F2 — reference fixture missing from Files to Change | MAJOR | §Files to Change adds `mooring-quick-screen-reference.json` row with concrete generation method (10 cases × dimensions, plus edge case); CLI hook `--emit-fixture` added to wrapper |
| F3 — citation resolveCodeId hand-waved | MAJOR | New §Citation Resolution Mechanism section locks build-time inlining via posthtml plugin; SKIP semantics for Phase-2-not-yet-landed; rationale (no CORS/latency/offline-fail) |
| F4 — mooring pattern scope not stated | MAJOR | v1 LOCKED to spread-only; turret/CALM out of scope; UI explicitly indicates this; tests `test_turret_pattern_rejected_in_v1` + `test_calm_pattern_rejected_in_v1` enforce |
| F5 — damaged-condition factor fabricated | MAJOR | Damaged-condition DROPPED from v1 (was numerically wrong); v1 is intact-only; UI directs damaged-condition users to integration tier ([aces-#7](https://github.com/vamseeachanta/aceengineer-strategy/issues/7)); test `test_damaged_condition_marked_unavailable` enforces |
| F6 — Plotly version not pinned | MINOR | Acceptance criterion now requires import from vendored `plotly-2.32.0.min.js` with SHA256 hash check |
| F7 — mailto address unspecified | MINOR | Locked to `tools@aceengineer.com` with subject prefill; user can override before ship |
| F8 — JSON-LD position inconsistent | MINOR | §Files to Change now says "append at next available position; do not hardcode" |
| F9 — pseudocode signature mismatch | MINOR | New `preflight()` step in v2 pseudocode reads actual Python signatures and documents deviations inline |

---

## Risks and Open Questions

- **Risk:** JS port arithmetic divergence from Python source. Mitigation: 10-case reference fixture + 1e-4 relative-error tolerance; Gemini cross-review on the JS engine before publication.
- **Risk:** `code_id` resolution fails because [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) Phase 2 hasn't landed yet. Mitigation: SKIP-mode citation panel with fallback text — calculator ships standalone, citations upgrade automatically when Phase 2 lands.
- **Risk:** Lead-capture form integration target unspecified. Mitigation: ship as mailto: stub on first deploy; follow-up issue tracks Mailchimp / HubSpot integration.
- **Open:** Branding decision — AceEngineer-branded or separate research-brand subdomain? Plan defaults to AceEngineer-branded under the existing `https://aceengineer.com/calculators/` collection (consistent with the 4 prior calculators); user may override.
- **Open:** Lead-capture target system — user to confirm Mailchimp / HubSpot / mailto: / other.
- **Open:** Should this calculator be the *first* one to cite via `code_id`, or wait for [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) Phase 2? Plan defaults to "ship now with SKIP-mode citations" — but if user prefers strict ordering (Phase 2 first, then calculator), defer this plan's execution until Phase 2 lands.

---

## Complexity: T2

T2 — multi-file (HTML + JS engine + Python wrapper), cross-repo (workspace-hub HTML + digitalmodel Python), TDD with numerical-parity fixture, integration with existing site build + JSON-LD pattern. The work is bounded: catenary equations are closed-form (no scipy / numerical-solver dependency in JS), the Python wrapper just composes existing tested functions, the HTML page mirrors a well-established pattern from prior calculators. Cross-repo workflow follows the #2481 cherry-pick precedent. Not T3 because no architecture decisions remain open after this plan; remaining open questions are configurations (lead-capture target, branding).
