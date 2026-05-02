# Adversarial Plan Review — aceengineer-strategy #5 (Public Mooring Quick-Screen Calculator)

**Reviewer:** Claude (single-author r3, fallback per `feedback_permission_gate_blocks_cross_review.md`)
**Plan file:** `docs/plans/2026-04-26-aces-5-flywheel-mooring-quick-screen-calculator.md`
**Date:** 2026-04-26
**Stance:** Adversarial — assume defects until proven otherwise. T2 with real implementation; defect bar is high. No praise. No restatement.

---

## What I checked

1. Resource Intelligence Summary — source-count, factual accuracy of file-existence claims
2. JS test-runner specification — is it concrete enough for an executor?
3. Citation `code_id` resolution mechanism — is it spec'd, or hand-waved?
4. Mooring pattern coverage scope — does the plan say which patterns (spread/turret/CALM) v1 supports?
5. Numerical correctness — are constants from the source or fabricated?
6. Cross-repo workflow handling for digitalmodel
7. File-list completeness — does every file mentioned elsewhere appear in Files to Change?
8. Pseudocode signature vs. actual `mooring_design.py` API (line refs verified earlier)
9. Lead-capture, branding, JSON-LD positioning — config items vs blocking gaps

---

## Verdict: MAJOR

5 substantive findings (F1–F5) that materially affect implementability + 4 minors. Plan needs a v2 patch before `status:plan-review`.

---

## Findings

### F1 — MAJOR: JS test runner unspecified
**Plan §Artifact Map / §TDD:** says "test runner per existing convention — audit during execution." This is exactly the kind of TBD that produces inconsistent execution. Existing aceengineer-website calculators (`npv-calculator-engine.js`, `obs-calculator-engine.js`, `wall-thickness-engine.js`) — does any of them have associated `.test.js`? If yes, name the runner. If no, this calculator introduces the JS-testing pattern and needs to lock the choice (Vitest? Mocha+Chai? Jest? Tape? Browser-native via `<script type="module">`?).

**Recommendation:** Phase 1 of execution (preflight) audits `aceengineer-website/` for any `*.test.js` or `package.json` test config; if none, plan must propose Vitest (smallest-footprint, modern, no transformer needed) and add to `package.json` devDependencies. Lock the runner choice in the plan, not at execution time.

### F2 — MAJOR: Reference fixture file missing from Files to Change
**Plan §Acceptance Criteria:** mentions `aceengineer-website/calculators/test-fixtures/mooring-quick-screen-reference.json` (10 input/output pairs at 1e-4 tolerance) but this file is NOT listed in §Files to Change. An executor reading §Files to Change would not create the fixture file at all, then numerical-parity test fails because the fixture doesn't exist.

**Recommendation:** add to §Files to Change:
- `Create | aceengineer-website/calculators/test-fixtures/mooring-quick-screen-reference.json | 10 input/output reference cases generated from Python wrapper for JS-parity validation`
- Specify generation method: "Python wrapper called with 10 representative cases (varying water_depth ∈ {500m, 1000m, 1500m, 2500m, 3000m} × line_count ∈ {8, 12} × material ∈ {chain_R4, polyester}, plus 1 edge case at minimum FoS), output dumped via `model_dump_json()` and committed."

### F3 — MAJOR: Citation `resolveCodeId` resolution mechanism is hand-waved
**Plan §Pseudocode:** `url = resolveCodeId(cite.code_id)` is the entire spec. The actual mechanism could be: (a) HTTP fetch from `https://aceengineer.com/wiki/standards/<publisher>/<code-id>/` at calculator load time, (b) build-time inlining into the static HTML via `build.js` posthtml plugin, (c) hardcoded JS object mapping, (d) async fetch on result render. Each has different failure modes, latency, and cache behavior. Unspecified means executor invents one and we get accidental architecture.

**Recommendation:** lock the resolution mechanism. Suggest (b) build-time inlining via posthtml plugin: at build time, the resolver scans the `code_id` references in the HTML, looks them up in the workspace-hub `knowledge/wikis/marine-engineering/wiki/standards/` tree (if Phase 2 of [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) has landed), and inlines the URL or fallback text. This avoids runtime fetch, no client-side latency, no CORS concern, no live llm-wiki dependency in production. SKIP semantics: if Phase 2 hasn't landed, build-time resolver inlines fallback text. Lock this in the plan.

### F4 — MAJOR: Mooring pattern coverage scope not stated for v1
**Plan §Pseudocode + §Resource Intelligence:** lists `MooringPattern` enum values (SPREAD, TURRET, CALM) but never says which patterns the v1 calculator handles. SPREAD is the default assumption, but TURRET differs in line distribution and CALM differs in geometry entirely. Building all three for v1 quadruples the surface area; building only one but UI-implying all three creates user confusion.

**Recommendation:** lock v1 scope to **SPREAD MOORING ONLY** (most common for FPSO; widest applicability for mooring-screening use case). Add explicit "out of scope" for v1: TURRET and CALM. Defer to follow-on issue. UI must clearly indicate "Spread mooring screening — see follow-on calculators for turret / CALM."

### F5 — MAJOR: Damaged-condition factor 0.75 is fabricated, not from source
**Plan §Pseudocode:** `fos_damaged = inputs.lineMBL / catenary.top_tension * 0.75` — the 0.75 multiplier on the top tension to model "damaged condition" is not from `digitalmodel.orcaflex.mooring_design`. The actual API RP 2SK damaged-condition methodology requires re-running the catenary with one line removed (load redistribution), not multiplying intact tension by a fudge factor. This pseudocode would produce wrong numbers AND the wrong calculation entirely — line redistribution after damage is the whole point of API RP 2SK Section 5 damaged-condition analysis.

**Recommendation:** either (a) drop damaged-condition from v1 scope (intact-condition screening only — clearly communicate "Quick screen: intact condition. For damaged-condition analysis, see institutional tier"), or (b) implement the proper damaged-condition methodology (remove one line, recompute catenary with redistributed load on remaining lines). Option (a) is the right choice for a "quick screen" — option (b) is the integration-tier ([aces-#7](https://github.com/vamseeachanta/aceengineer-strategy/issues/7)) scope. **The lazy-multiplier approach in the current pseudocode would publish numerically wrong results under our brand and is unacceptable.**

### F6 — MINOR: Plotly version not pinned in plan
**Plan:** mentions Plotly for visualization but doesn't pin version. The repo has `aceengineer-website/assets/js/plotly-2.32.0.min.js` vendored (verified earlier). New calculator must reuse this exact file (not link to CDN, not bundle a different version) for SHA-checksum hygiene and offline functionality.

**Recommendation:** add to acceptance: "Plotly imported from `../assets/js/plotly-2.32.0.min.js` (the vendored copy — not CDN); version match enforced by build-step SHA check."

### F7 — MINOR: Lead-capture mailto: stub address unspecified
**Plan §Risks:** "ship as mailto: stub on first deploy" — but to whom? No email address. Without it, executor either invents one or leaves a placeholder.

**Recommendation:** specify `mailto:tools@aceengineer.com?subject=Mooring%20Calculator%20Institutional%20Tier%20Inquiry` or similar; user can override before ship if address is wrong.

### F8 — MINOR: JSON-LD position in calculators index inconsistent
**Plan §Files to Change:** "item 4 → item 5 in JSON-LD `itemListElement` array." But existing `index.html` shows position 1 = "S-N Curve Fatigue Calculator"; there are at minimum 3 calculator HTML files in `calculators/` (fatigue-life, fatigue-sn-curve, npv) plus the index itself — actual existing array length should be verified at execution.

**Recommendation:** "append as next position after the highest existing item; do NOT hardcode position 5 — read existing index, append, increment."

### F9 — MINOR: Pseudocode catenary signature doesn't match Python source
**Plan §Pseudocode:** `solveCatenary(horizontalForce, lineWeight, lineLength, waterDepth)` — but the actual `digitalmodel.orcaflex.mooring_design.solve_catenary()` function (line 155 of source) likely takes a `CatenaryInput` pydantic model based on the surrounding code structure. JS port should mirror the Python signature, or explicitly note that JS uses positional args while Python uses model — and document why.

**Recommendation:** read the actual Python signature during Phase 1 of execution and update the JS port to match (or document the deviation). Add a verification step: "JS engine signature matches Python wrapper signature; deviation requires explicit comment block citing reason."

---

## Empty-review check

9 findings (5 MAJOR, 4 MINOR). Specific file paths cited (plan §, source-code line refs, file paths). Not empty.

---

## Cross-provider context

- **Codex:** UNAVAILABLE — codex-cli 0.124.0 upstream regression workspace-hub #2479.
- **Gemini:** RECOMMENDED. T2 with substantive implementation; Gemini cross-review on JS arithmetic correctness adds non-trivial value. Recommend running once codex-cli regression resolves OR via `submit-to-gemini.sh` with `GEMINI_CLI_TRUST_WORKSPACE=true` per `feedback_gemini_trust_env_blocks_reviews.md`.

---

## Recommended action

1. **REQUIRED before status:plan-review:** patch plan to address F1, F2, F3, F4, F5 (the 5 MAJOR findings).
2. **Recommended in the patch:** F6, F7, F8, F9 (concrete linkages and signature alignment).
3. After patch, re-review (this same single-author r3 fallback).
4. Once MINOR-or-better, apply `status:plan-review` label.
5. Phase 2 of #4 (standards canonical home population) should land before this plan executes if `code_id` build-time resolver chooses "live wiki" — otherwise, SKIP-mode build-time resolver allows this calculator to ship first.

The pattern this plan should follow for cross-repo digitalmodel handling: workspace-hub plan `2026-04-24-issue-2481-calc-output-citation-contract.md` (cherry-pick to `digitalmodel/main` as `c3be1472`). Adopt or document deviation.

The pattern for damaged-condition arithmetic (F5): drop from v1 scope; defer to integration-tier ([aces-#7](https://github.com/vamseeachanta/aceengineer-strategy/issues/7)) where line-redistribution simulation is appropriate scope.
