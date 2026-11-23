# wed #945 — Client presentation layer (remaining sub-features)

**Issue:** worldenergydata #945 (epic child of #939) — client-layer: provenance, PDF export, guided demo path.
**Status:** PDF one-pagers already shipped (#964). This plan covers the **remaining four** sub-features.
**Grounding:** shallow clone @ `origin/main` `18196e7`; all facts below COMPUTED against that tree.
**Scope discipline:** ONE PR, one lane (`lane:claude`). No external data dependency — all four are in-repo template/copy changes.

---

## Goal

Make the Explorer client-presentable: a citation footer on every panel + a page-level data-sources
footer; a visible, bookmarkable guided-demo path (GoM → Lower Tertiary → Jack/St Malo → its wells →
a well stage); the capabilities "Field atlas" hero re-pointed to describe the unified Explorer; and a
naming/branding pass on the client-facing surface.

## Current state (verified)

- Explorer shell source: `reports/field-atlas/atlas_template.html` (460 lines). `build_field_atlas.py`
  substitutes `__ROSTER_JSON__`/`__COUNTRIES_JSON__` and writes the committed
  `reports/field-atlas/index.html` (both files are gate inputs; **regenerate index.html, never hand-edit it**).
- Field panel already renders `<p class="xprov">${esc(f.provenance||"")}</p>` (L379). **`f.provenance`
  is populated 10/10** in `reports/lower_tertiary/lifecycle/_explorer.json`.
- Wells panel (`renderWells`, L382) and well-stage panel (`renderWell`, L404) render **NO** provenance line.
- There is **no page-level footer** at all (`.wrap` closes at L136, `<script>` follows).
- Capabilities hero `reports/capabilities/index.html:132`:
  `href="../field-atlas/"` … text `"Browse the field atlas — 120 GoM fields →"` — already points at the
  Explorer but the copy understates it (120 GoM only; no mention of drill-down / wells / lenses / 84 countries).
- Capabilities L173 "All-regions field atlas" card shows **"205 countries"** and links `all-regions-atlas.html`.
  Per r1, "205 countries" also appears in `capabilities/insights.html:180` and `all_regions_atlas.html:86-88`.
  205 = **countries in atlas scope** (reference-depth); 84 = **countries with offshore-field data** (feed reality,
  `1 RICH + 78 SAMPLE + 5 ROADMAP`). Both are valid, coexisting metrics — see Sub-feature 3 (r2) for the fix.
- `reports/capabilities/index.html` carries the nav-spine `MARKER` — it is the committed source
  `build_pages.py` copies; editing it directly is correct.
- **No "A&CE" branding** anywhere on the client surface (field-atlas/, capabilities/, onepagers script) — verified by grep.
- Jack/St Malo (`jack_st_malo`) has **24 producing wells**; representative slot for the demo: **`PN002`** (cum 31.8 MMbbl).

## Gate constraints (verified against `tests/integration/site/test_public_link_graph.py`)

1. **`test_atlas_shell_pins`** asserts `text.count("<h1") == 1`. Footer + guided-demo band MUST lead with
   `<h2>`/`<h3>`, never `<h1>` (nav-spine injector fails closed on a 2nd `<h1>` anywhere, incl. script strings).
2. **Fragment-only hash links are gate-invisible.** `site_nav._INTERNAL_ATTR` = `(?:href|src)=["']([^"'#]+)(?:#…)?`
   requires ≥1 non-`#` char before any `#`, so `href="#/field/jack_st_malo"` matches nothing →
   NOT flagged by `test_zero_unresolved_internal_targets_and_fragments` and NOT followed by
   `test_bfs_reachability_from_capabilities`. Guided-demo steps are therefore gate-safe **iff every href starts with `#`**.
3. **BFS reachability** starts at `capabilities/index.html` and must still reach `field-atlas/index.html`
   (kept — hero href unchanged) and `all-regions-atlas.html` (kept — card link unchanged; only copy edited).
4. **`test_hand_authored_fixes_survive_clean_build`** requires the capabilities `MARKER` to survive — preserve it.
5. **`test_atlas_shell_pins` / `test_atlas_funnel_global_pins`** pin `const ROSTER`, `const COUNTRIES`,
   funnel ids, `#/field/`, `_explorer.json`, `_atlas_feed.json`, `(unattributed)` — all preserved (additive edits only).
6. `all_regions_atlas.html` embeds `date.today()` — **do NOT regenerate it** (`git checkout --` if touched).

## Design

### Sub-feature 1 — provenance/citation footers on every panel + page-level data-sources footer

- **Wells + well-stage panels:** append `<p class="xprov">${esc(f.provenance||"")}</p>` to `renderWells`
  and `renderWell` output (reuse the field object already in scope — `renderWells(x, f)` / `renderWell(x, f, slot)`
  both hold `f`). Same class, same single-source string; identity gate unaffected (no payload change).
- **Page-level footer:** add a `<footer class="pgfoot">` block just before `.wrap` closes (L136), containing:
  - a `<h2>`-led "Data & provenance" heading (house style, sentence case);
  - a plain-language sources summary: BSEE public data (data.bsee.gov), in-repo curated field YAML,
    public operator disclosures; density-badge recap (rich/sample/roadmap) mirroring the existing note;
    a "contributions welcome" line linking the repo issues.
  - **No snake_case leaks, no literal "null"** (QA lesson) — all copy hand-written, no interpolated payload keys.
- Style: reuse existing `.xprov`/`.note` colours; footer `border-top`, muted, small — non-intrusive.

### Sub-feature 2 — guided demo default path

- Add a visible **"Guided demo"** band after the `story` line (L105), before the funnel. `<h3>`-led (or a
  styled label — non-`<h1>`), with a numbered, bookmarkable sequence, every href fragment-only:
  1. **Lower Tertiary — why start here** → `#` (the default funnel view already lands on USA·offshore·GoM;
     the LT story is the default). Rendered as step 1 context, links to top.
  2. **Jack/St Malo — a rich field** → `#/field/jack_st_malo`
  3. **Its 24 producing wells** → `#/field/jack_st_malo/wells`
  4. **A single well, stage by stage** → `#/field/jack_st_malo/wells/PN002`
- Each step is an `<a>` with a fragment-only href → gate-invisible (constraint 2). Client can bookmark any step.
- Copy frames it as a 4-click walkthrough for a first-time client visitor.

### Sub-feature 3 — capabilities repoint (r2: MAJOR-1 fix folded)

**r1 adversarial finding (MAJOR-1, verified by computation):** "205 countries" is NOT confined to the one
capabilities card. It appears in THREE published, gate-scoped surfaces — `reports/capabilities/index.html:173`,
`reports/capabilities/insights.html:180`, and `reports/field_development/all_regions_atlas.html:86-88` (KPI). And
205 ≠ 84 are two DIFFERENT valid metrics that already coexist on those pages: **205 = countries in atlas scope**
(reference-depth), **84 = countries with actual offshore-field data** (`1 RICH + 78 SAMPLE + 5 ROADMAP`, and the
feed carries 84). Editing only the one card to "84" would (a) contradict the page it links to and the sibling
`insights.html`, and (b) misframe a valid scope number as an error. The r1 verdict was MAJOR-REVISE scoped to
this sub-feature only (sub-features 1/2/4 verified sound).

**Resolution — relabel, don't swap, and do it on ALL THREE surfaces consistently:**
- **Hero (`index.html` L132):** keep `href="../field-atlas/"`; rewrite label to describe the Explorer (drill-down
  + wells + economics/underwriting/landman lenses), dropping the stale "120 GoM fields" count. Copy finalized in impl.
- **All three "205" surfaces** (`index.html:173`, `insights.html:180`, `all_regions_atlas.html:86-88`): render
  BOTH numbers with explicit labels — e.g. *"205 countries in atlas scope · 84 with offshore-field data"* — so
  scope-vs-coverage is unambiguous and the trio stays internally consistent. Do NOT delete the 205; do NOT swap
  it to 84.
- **Editing `all_regions_atlas.html`:** it embeds `date.today()` at build (constraint 6 — do NOT regenerate it).
  Hand-edit its COMMITTED HTML in-place in the same PR (the two numbers are static text in the KPI block), and
  `git checkout --` any accidental full regeneration. Verify only the number strings changed (targeted diff).
- Keep the `all-regions-atlas.html` link intact (reachability constraint 3); add a one-line pointer that the
  Explorer's Country selector is the interactive way in.
- Preserve `MARKER` on `index.html` and `insights.html` (constraint 4 — both are MARKER-checked by
  `test_hand_authored_fixes_survive_clean_build`).

**MINOR-2 (folded):** do NOT introduce "2,032" into any copy — the live surfaces render field count as **2,149**
(`COUNTRIES.reduce`, atlas note L128/L244; all-regions KPI). 2,032 is the internal deduped feed row count, shown
nowhere. Keep field-count copy either absent or "2,149" to match what renders.
**MINOR-3 (folded):** guided-demo step 1's bare `#` is "back to the top view" (clears the route via `onHash`),
not a deep-link — frame the copy that way.
**NIT-4 (folded):** after sub-feature 1, `class="xprov"` appears 3× in built `index.html` (field + wells + well
panels); a test pinning the count expects 3. The page-level footer uses `class="pgfoot"`, not `xprov`.

### Sub-feature 4 — naming/branding pass

- Grep the client surface for `A&CE` / `A&amp;CE` (currently zero) and for stray snake_case / literal "null"
  in visible copy; fix any found. Confirms house-style compliance on the newly-added copy too.

## Files touched

- `reports/field-atlas/atlas_template.html` — footer + guided-demo band + wells/well provenance lines.
- `reports/field-atlas/index.html` — **regenerated** via `build_field_atlas.py` (committed artifact).
- `reports/capabilities/index.html` — hero + all-regions-card copy (MARKER preserved).
- `tests/integration/site/test_public_link_graph.py` — new pins:
  - guided-demo sequence present in `field-atlas/index.html` (the 4 fragment hrefs incl. `#/field/jack_st_malo/wells/PN002`);
  - page-level data-sources footer present; `count("<h1")` still 1 (extend existing pin);
  - wells + well panels emit an `.xprov` line (assert `class="xprov"` count / presence in the shell template render path).
- Possibly `reports/field-atlas/onepagers/*` — **unchanged** (PDF already shipped; only re-verify no branding leak).

## Test / build / lint recipe (from handoff, verified)

- Regenerate: `python scripts/lower_tertiary/build_lifecycle_posters.py` then `python scripts/field_atlas/build_field_atlas.py`.
  (Posters need not change here — but rebuild to prove byte-identity; only the shell + capabilities change.)
- Tests: `pytest tests/test_build_pages.py tests/integration/site/ tests/unit/site/ tests/unit/field_development/ tests/unit/lower_tertiary/test_wells_facts.py -o addopts="" --noconftest -q` (~139 baseline + new pins).
- Lint mirror: `uvx black@25.9.0 --check`, `uvx isort@8.0.1 --check-only`, `uvx flake8@7.3.0 --max-line-length=100 --extend-ignore=E203,W503` on `src/ tests/` (only tests change here).
- venv-min: `pyyaml pydantic-settings pytest pandas openpyxl`; `PYTHONPATH=src:packages/worldenergydata-core/src:packages/worldenergydata-bsee/src`.

## Live verification (post-merge)

- `/field-atlas/?v=N` (cache-bust): guided-demo band visible; each step navigates + is bookmarkable;
  `#/field/jack_st_malo/wells/PN002` deep-links to the stage detail; footer renders with real source copy (no "null").
- Wells + well panels show the citation line.
- `/capabilities/`: hero copy reads as the Explorer; all three "205" surfaces show the dual
  "205 in scope · 84 with field data" labeling consistently; the all-regions card still opens.
- Verify DOM via `get_page_text`/`javascript_tool` (screenshot-after-scroll goes blank — known gotcha).

## Out of scope / deferred

- #942 architecture panel (inline-SVG + FieldConcept authoring) — separate track, MAJOR-REVISE.
- Ingest backlog #955/#959/#960/#962 — download-gated.
- Provenance *per-attribute* citations (beyond the field-level string) — not required by #945; the field
  provenance string is the client-appropriate granularity.

## Adversarial review — RESOLVED (r1 verified all by computation @ wed 18196e7)

1. **`renderWells`/`renderWell` hold the full `f`** — PASS. `const f = x.fields[fid]` (L437) is passed identically
   to all three renderers (L442-444); `.provenance` present. Impl note: put the `.xprov` line in the MAIN `show()`
   output, after the early-return guards (renderWells L385-389, renderWell L407-410).
2. **Footer / single-`<h1>`** — PASS. Template has exactly 1 `<h1` (L102); nav-spine `inject()` raises only on
   `count("<h1")>1` and is indifferent to a `<footer>`/band. `<h2>/<h3>` are uncounted (card render already emits `<h3>`).
3. **"205" is in 3 surfaces** — this was the MAJOR-1 finding; **now resolved in Sub-feature 3 (r2)** by relabeling
   all three with dual scope/coverage numbers rather than a one-card swap.
4. **No test pins the hero string** — PASS. `grep` over `tests/` for the hero copy / "120 GoM" / "205 countries" /
   "84 countries" → no matches. Copy change is test-safe.

Other r1 checks PASS: fragment-only `#/…` demo hrefs are gate-invisible (both `_INTERNAL_ATTR` and the BFS
`href_re` require ≥1 non-`#` char); `jack_st_malo` has 24 wells incl. slot `PN002`, and `ROUTE` accepts it;
`build_field_atlas.py` regeneration is deterministic (no embedded timestamp). **r1 verdict: MAJOR-REVISE scoped to
sub-feature 3 → folded above; sub-features 1/2/4 mechanically sound. This r2 is ready for owner review.**
