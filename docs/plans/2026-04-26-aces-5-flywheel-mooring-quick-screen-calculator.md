# Plan for aceengineer-strategy #5: Public Mooring Quick-Screen Calculator

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-26
> **Issue:** https://github.com/vamseeachanta/aceengineer-strategy/issues/5
> **Parent epic:** https://github.com/vamseeachanta/aceengineer-strategy/issues/1
> **Review artifacts:** scripts/review/results/2026-04-26-plan-aces-5-claude.md (pending)

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

A public mooring quick-screen calculator at `https://aceengineer.com/calculators/mooring-quick-screen.html` that: (a) takes vessel class + water depth + environmental severity + line configuration as inputs, (b) computes indicative line tensions, anchor radius, factor of safety per API RP 2SK / DNV-OS-E301 client-side via JS port of `digitalmodel.orcaflex.mooring_design`, (c) renders results with Plotly visualization (catenary profile + tension vs offset), (d) cites relevant standards clauses with `code_id` resolving to public llm-wiki pages once aces-#4 Phase 2 lands (fallback text otherwise), (e) captures leads via a "Get the institutional version" CTA. Numerical parity with the Python module enforced by a fixed reference test set (≥10 input/output pairs).

---

## Pseudocode

```
# JS engine (mooring-calculator-engine.js)
function solveCatenary(horizontalForce, lineWeight, lineLength, waterDepth):
    # Closed-form catenary equation; mirrors digitalmodel.orcaflex.mooring_design.solve_catenary
    a = horizontalForce / lineWeight  # catenary parameter
    suspended_length = sqrt(2 * a * waterDepth + waterDepth^2)
    horizontal_distance = a * acosh(1 + waterDepth / a)
    top_tension = horizontalForce + lineWeight * waterDepth
    return { suspended_length, horizontal_distance, top_tension, catenary_a: a }

function calculatePretension(designTensionMBL, safetyFactorIntact, safetyFactorDamaged):
    # Mirrors digitalmodel.orcaflex.mooring_design.calculate_pretension
    pretension_intact = designTensionMBL / safetyFactorIntact
    pretension_damaged = designTensionMBL / safetyFactorDamaged
    return { pretension_intact, pretension_damaged }

function mooringQuickScreen(inputs):
    # Composes catenary + pretension + standards-citation lookup
    catenary = solveCatenary(...)
    pretension = calculatePretension(...)
    fos_intact = inputs.lineMBL / catenary.top_tension
    fos_damaged = inputs.lineMBL / catenary.top_tension * 0.75  # damaged condition factor
    pass_intact = fos_intact >= 1.67  # API RP 2SK Section 5
    pass_damaged = fos_damaged >= 1.25  # API RP 2SK Section 5
    return {
        screening_pass: pass_intact && pass_damaged,
        catenary, pretension, fos_intact, fos_damaged,
        citations: [
            { code_id: "api-rp-2sk-5.0", clause: "Factor of Safety", value: fos_intact },
            { code_id: "dnv-os-e301-3.5.2", clause: "Position Mooring ULS" }
        ]
    }

function renderCitationPanel(citations):
    # Resolves code_id to llm-wiki URL if standards Phase 2 has populated; else fallback text
    for cite in citations:
        url = resolveCodeId(cite.code_id)  # fetches from llm-wiki standards subtree
        if url:
            display(`<a href="${url}">${cite.code_id}</a>: ${cite.clause}`)
        else:
            display(`${cite.code_id} (citation pending — see plan aces-#4 Phase 2): ${cite.clause}`)
```

```
# Python wrapper (mooring_quick_screen.py — parity surface)
def mooring_quick_screen(inputs: MooringQuickScreenInput) -> MooringQuickScreenResult:
    catenary = solve_catenary(...)
    pretension = calculate_pretension(...)
    # ... same logic as JS engine, returning pydantic model with citation registry refs
    return MooringQuickScreenResult(
        screening_pass=...,
        catenary=catenary,
        pretension=pretension,
        citations=[CitationRef(code_id="api-rp-2sk-5.0", ...)]
    )
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `aceengineer-website/calculators/mooring-quick-screen.html` | Calculator HTML page (follows pattern of fatigue-life-calculator.html) |
| Create | `aceengineer-website/assets/js/mooring-calculator-engine.js` | JS engine (port of Python module; closed-form catenary needs no external deps) |
| Create | `aceengineer-website/assets/js/mooring-calculator-engine.test.js` | Unit tests for JS engine (parity vs reference Python outputs) |
| Modify | `aceengineer-website/calculators/index.html` | Add mooring quick-screen to calculators collection (item 4 → item 5 in JSON-LD `itemListElement` array) |
| Create | `digitalmodel/src/digitalmodel/orcaflex/mooring_quick_screen.py` | Python wrapper (parity surface; future server-side / batch option) — **cross-repo per #2481 precedent** (separate digitalmodel branch + cherry-pick to digitalmodel/main) |
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
| test_quick_screen_damaged_condition_check | damaged-condition factor of safety enforced separately | nominal design | fos_damaged ≥ 1.25 |
| test_catenary_parity_with_solve_catenary | wrapper output matches direct solve_catenary call | known horizontal_force, line_weight, water_depth | top_tension matches within 1e-6 relative |
| test_pretension_parity_with_calculate_pretension | wrapper output matches direct calculate_pretension call | MBL=1500t, FoS=1.67/1.25 | pretensions match within 1e-6 relative |
| test_citation_refs_present | result includes API RP 2SK + DNV-OS-E301 code_ids | any input | citations list ≥ 2 with `api-rp-2sk-*` and `dnv-os-e301-*` prefixes |
| test_input_validation_rejects_negative_depth | rejects invalid input | water_depth=-100 | raises ValidationError |
| test_input_validation_rejects_zero_lines | rejects invalid input | num_lines=0 | raises ValidationError |

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

- [ ] All Python wrapper tests pass: `uv run pytest digitalmodel/tests/orcaflex/test_mooring_quick_screen.py -v`
- [ ] All JS engine tests pass (test runner per existing convention — audit during execution)
- [ ] Numerical parity: JS output matches Python output within 1e-4 relative error for 10 reference cases stored in `aceengineer-website/calculators/test-fixtures/mooring-quick-screen-reference.json`
- [ ] No regression: full digitalmodel test suite passes (`uv run pytest digitalmodel/`)
- [ ] No regression: aceengineer-website build completes (`cd aceengineer-website && node build.js` or equivalent)
- [ ] HTML page passes JSON-LD Rich Results test
- [ ] Citation panel resolves `code_id` → llm-wiki URL when `aces-#4` Phase 2 has landed; SKIPs cleanly with fallback text otherwise
- [ ] Lead-capture form: integration target locked (Mailchimp / HubSpot / mailto: stub) — if not user-configured, ships as mailto: stub with TODO follow-up issue
- [ ] Calculator linked from `aceengineer-website/calculators/index.html` collection
- [ ] `docs/plans/README.md` updated
- [ ] aceengineer-strategy issue [#5](https://github.com/vamseeachanta/aceengineer-strategy/issues/5) closure comment cites the deployed URL

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self-r3) | PENDING | review at `scripts/review/results/2026-04-26-plan-aces-5-claude.md` |
| Codex | UNAVAILABLE | codex-cli 0.124.0 upstream regression #2479 |
| Gemini | RECOMMENDED-DEFERRED | T2 implementation; Gemini cross-review adds value on JS-Python numerical-parity arithmetic; deferred until codex-cli regression resolves OR user requests |

**Overall result:** PENDING (post-review)

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
