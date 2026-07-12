# Plan — Field architecture-drawing panel (wed epic #942, child #969)

- **Repo:** vamseeachanta/worldenergydata — clone on local disk `/tmp/wed-942` (HEAD `d3647d9`, origin/main).
- **Parent epic:** #942 (field detail planes). **Tracer child:** #969.
- **Cross-links:** dm#1519 (block-diagram concept — produces no consumable drawing), dm#1523 (solver/output contract).
- **Status:** `status:needs-plan` → adversarial review of THIS doc → user approval. No implementation yet.

This document is written in future tense: it describes work **to be done**, not work already done.

---

## 1. Goal

The architecture-drawing panel is the last remaining plane of #942. It will add a per-field
**plan-view (map) architecture drawing** to the Explorer field view, reusing the wed renderer
`worldenergydata.field_development.layout.render_layout(concept)` rather than waiting on the
digitalmodel solver (dm#1519), whose block-diagram output the 2026-07-10 parallel-agent wave
judged non-consumable ("MAJOR-REVISE: dm#1519 produces no consumable drawing; wed already has a
plan-view SVG renderer").

The drawing will appear in all three consumers of the field payload: the Explorer shell
(`renderField`), the lifecycle poster template, and the PDF one-pager — because those three
single-source the same per-field dict.

## 2. Verified current state (grounded by computation on `/tmp/wed-942`)

Numbers below were measured, not assumed.

### 2.1 The renderer already exists and is PDF-portable
`src/worldenergydata/field_development/layout.py:158` — `render_layout(concept, graph=None,
scale_px_per_km=40.0) -> str` emits a complete SVG document string (manifold at origin, subsea
trees on a ring, host offset north by `tieback_distance_km`, north arrow + scale bar). It has **no
third-party dependency** and is deterministic.

Ran `render_layout` on real concepts (heredoc under `/tmp/venv-942`):

| Concept | Source | SVG bytes | wells drawn | PDF-portability bad tokens | `<h1>`? | NaN/inf? |
|---|---|---:|---:|---|---|---|
| Julia | authored full concept (`build_julia_fdp.py`) | 6689 | 5 | none | no | no |
| Stones | `_research.json` via `to_concept` (fpso, 8 wells) | 7634 | 8 | none | no | no |
| Chinook | `_research.json` via `to_concept` (tieback, 2 wells, 24 km) | 3682 | 2 | none | no | no |
| Big Foot (facts-only, degenerate) | name + water_depth only | 2689 | 1 | none | no | no |

"bad tokens" = any of `<pattern` / `clip-path` / `clipPath` / `<filter` / `<mask` / `url(#` — **zero
found** in every output. This satisfies `.claude/rules/svg-pdf-portability.md`. The SVG contains no
`<h1>` and no `nan`/`inf` literals.

### 2.2 The decision-critical concept count: **3 of 10**
The Explorer's 10 LT field ids (`reports/lower_tertiary/lifecycle/_explorer.json` → `fields`):
`big_foot, anchor, cascade_chinook, jack_st_malo, julia, kaskida, north_platte, shenandoah, stones,
tiber`.

Only **3** have a usable authored `FieldConcept` with real geometry (well count / concept type /
tieback distance): **cascade_chinook, julia, stones** — exactly the 3 with committed FDP portfolio
pages. Corroborated three ways:
- `src/worldenergydata/field_development/concept.py` docstring: *"Only 3 of the 10 Lower Tertiary
  fields have a committed FDP page … cascade_chinook/julia/stones; the other 7 carry an fdp_slug but
  no page yet."*
- `_explorer.json`: only cascade_chinook / julia / stones have `concept.fdp_href` set; the other 7
  have `fdp_href=None` and `fdp_issue=962`.
- Authored concept sources exist for exactly those 3: `scripts/field_development/build_julia_fdp.py`
  (Julia: `num_wells=5, num_manifolds=2, SUBSEA_TIEBACK, tieback_distance_km=30`) and
  `reports/field_development/portfolio/_research.json` → `to_concept()` in
  `scripts/field_development/build_fdp_portfolio.py` (Stones: fpso/8 wells; Chinook: tieback/2 wells/24 km).

The other 7 fields have only `_facts.json` records (host_type text, water_depth_ft, play, gates) with
**no** `num_wells`, `concept_type`, `num_manifolds`, or `tieback_distance_km`. `concept_to_graph`
degrades gracefully (`_tree_count` → 1 when `num_wells` is None; defaults to wet trees / 1 manifold /
1.5 km host offset), so `render_layout` would still return a *valid* SVG for them — but a degenerate
single-tree drawing that misrepresents the field, not a real architecture. Those 7 will therefore get
a **visible placeholder**, not a fake drawing.

### 2.3 Payload size impact is acceptable
`_explorer.json` is currently **100,354 bytes**. Inlining the 3 real SVGs (~6.7 + 7.6 + 3.7 = ~18 KB)
plus 7 small placeholder objects (~0.2 KB each) projects to **~120 KB** (a ~20% increase). Even the
worst case (a real SVG inlined for all 10, ~5 KB avg) would be ~150 KB. Both are well within reason
for a static sidecar JSON. (The identity gate requires the same bytes be embedded per poster; that is
a duplication already inherent to the design, not new bloat introduced here.)

### 2.4 The gates that must stay green
- `tests/integration/site/test_public_link_graph.py::test_explorer_identity_with_posters` — asserts,
  per field, `poster-embedded FIELD dict == _explorer.json["fields"][id]` (byte-for-byte). Inlining
  the SVG **string** into the shared payload keeps this satisfied; a file href would not participate.
- `…::test_atlas_shell_pins` — asserts `field-atlas/index.html` has exactly **one** `<h1`
  (`atlas_template.html` currently has exactly 1, verified). The panel heading must be `<h2>`/`<h3>`.
- `render_layout` output must remain free of `<pattern>`/clipPath/filter/mask for the PDF one-pager.

### 2.5 The three render sites (payload single-sourcing)
- **Explorer shell** — `reports/field-atlas/atlas_template.html`, `renderField()` (concept card built
  at ~lines 388-403, injected in the `xcols` block ~415).
- **Poster template** — `reports/lower_tertiary/lifecycle/lifecycle_template.html`, the
  `if (FIELD.concept){…}` block (~lines 440-455), target slot `<div id="f-concept">` (line 285).
- **PDF one-pager** — `scripts/capabilities/build_field_onepagers.py`, which reads `_explorer.json`
  via `load_explorer()` and renders per-field HTML with helpers `_chips`/`_metrics`/`_perf`; a new
  `_architecture(field)` helper will inline the SVG string into the one-pager HTML body (inline
  `<svg>` in the DOM renders in Chrome print-to-pdf; the file://-image gotcha does not apply to
  inline markup).

## 3. Design

### 3.1 Payload shape
`facts_to_field(f)` in `scripts/lower_tertiary/build_lifecycle_posters.py` will add one new key,
`architecture`, for every field. Two shapes:

- **Authored field (cascade_chinook / julia / stones):**
  ```
  "architecture": {"svg": "<svg …>…</svg>", "source": "render_layout"}
  ```
  where `svg` is the string returned by `render_layout(concept)`.
- **Concept-less field (the other 7):**
  ```
  "architecture": {"svg": null, "pending_issue": 962}
  ```

Rationale for a small object (not a bare string): it lets every consumer branch on
`architecture.svg` vs a placeholder without a second lookup, and it keeps the placeholder's issue
number in the payload (so the identity gate covers it too).

### 3.2 Where the concept comes from
A single authored-concept source per field, chosen for determinism:
- **julia** → the `FieldConcept` in `build_julia_fdp.py` (richest: 2 manifolds).
- **stones**, **cascade_chinook** → `to_concept()` applied to the matching `_research.json` entry
  ("Stones", "Chinook").

To avoid importing build scripts, the plan will extract a small helper — e.g.
`worldenergydata.field_development.portfolio_concepts.concept_for(field_id) -> FieldConcept | None` —
that returns the authored concept for the 3 ids and `None` otherwise. `facts_to_field` calls it; on
`None` it emits the placeholder. This keeps the mapping in one reviewable module rather than in the
poster script. (Open question 4 asks the reviewer to confirm this is preferable to reading
`_research.json` directly.)

### 3.3 Rendering per consumer
- **Explorer `renderField`** — after the concept card, add an "Architecture" cardlet: if
  `f.architecture.svg`, inject the SVG string directly; else a muted placeholder
  `<a href="…/issues/962">— field architecture pending</a>`. Heading `<div class="xh">` (no `<h1>`).
- **Poster template** — mirror the same branch into a new slot (e.g. `<div id="f-arch">`), heading
  `<h3>`.
- **PDF one-pager** — `_architecture(field)` returns an SVG block or the placeholder; inserted in the
  one-pager body.

**(r2 finding #1 — DECISION, was open-question 1) cascade_chinook renders WITH a relabel.** The authored
concept is `_research.json["Chinook"]` (`num_wells=2`, tieback, 24 km); the Explorer field
`cascade_chinook` states `name="Cascade/Chinook"` with `wellsCount=3`. Drawing 2 trees for a 3-well field
is a visible 2-vs-3 inconsistency, but the tieback is directionally correct and matches the existing
`fdp_href → chinook.html` wiring. Resolution: **render it**, and caption the cardlet
**"Chinook subsea tieback"** (not "Cascade/Chinook") so the drawing's scope is honest — do NOT downgrade
to a placeholder, and do NOT fabricate a 3rd well. The caption string is set in the render sites (3.3)
and covered by `test_architecture_svg_for_authored_three`.

### 3.4 Placeholder-issue target — recommendation
Link the **existing FDP-authoring backlog issue #962** (the same issue the current
`— concept detail pending` placeholder already links). Reasons: (a) the missing input is exactly a
per-field authored concept, which #962 already tracks; (b) it keeps ONE grabbable worklist rather
than splitting attention; (c) dm#1523 is the wrong target — it is a digitalmodel solver/output
contract, not a place a wed reader can grab per-field concept authoring. A new `cat:data` wed child is
the second-best option only if architecture-specific tracking is later wanted; reuse of #962 is
recommended for now.

### 3.5 NaN/inf safety
`render_layout` produced no `nan`/`inf` on the tested concepts, and geometry is pure trig on authored
floats. As defense-in-depth, the extraction helper will reject any concept whose numeric inputs are
NaN/inf (falling back to the placeholder), and a test will assert no `NaN`/`Infinity` token appears in
`_explorer.json` (invalid JSON would dark-screen the Explorer).

## 4. Files to be touched
- `src/worldenergydata/field_development/portfolio_concepts.py` — **new** small helper mapping the 3
  ids → authored `FieldConcept`.
- `scripts/lower_tertiary/build_lifecycle_posters.py` — `facts_to_field` emits the `architecture` key.
- `reports/field-atlas/atlas_template.html` — `renderField` renders the architecture cardlet.
- `reports/lower_tertiary/lifecycle/lifecycle_template.html` — poster renders the architecture slot.
- `scripts/capabilities/build_field_onepagers.py` — `_architecture` helper + insertion.
- **Regenerated artifacts** (by running the build scripts, never hand-edited): all
  `reports/lower_tertiary/lifecycle/*_lifecycle.html`, `_explorer.json`, and
  `reports/field-atlas/index.html` (via `scripts/field_atlas/build_field_atlas.py`).
- **NOT regenerated:** `all_regions_atlas.html` (embeds `date.today()` — would churn).
- New tests under `tests/unit/…` and/or `tests/integration/site/` (see §6).

## 5. Gate constraints (must all hold)
1. **Single `<h1>`** — panel headings are `<h2>`/`<h3>`/cardlet; `test_atlas_shell_pins` stays green.
2. **SVG-PDF portability** — panel SVG stays free of `<pattern>`/clipPath/filter/mask (cite
   `.claude/rules/svg-pdf-portability.md`); verify the one-pager PDF with `pdftocairo`, not Chrome.
3. **Identity gate** — the SVG is inlined as a **string** into the shared payload so sidecar == poster
   (`test_explorer_identity_with_posters`); never a file href.
4. **Regenerate, don't hand-edit** — `field-atlas/index.html` via `build_field_atlas.py`; do NOT
   regenerate `all_regions_atlas.html`.
5. **venv needs pandas + openpyxl** — the economics import pulls pandas via a package `__init__`;
   the build/test venv installs `pyyaml pydantic-settings pytest pandas openpyxl`.
6. **NaN/inf sanitized** before any number reaches the SVG/JSON.
7. If `render_layout` needs inputs beyond the authored concept: it does **not** — it takes a single
   `FieldConcept` and (optionally) a prebuilt graph; no external files, no network.

## 6. TDD test list (write first, watch fail, then implement)
1. `test_architecture_key_present_all_fields` — every field in `_explorer.json` has an `architecture`
   key.
2. `test_architecture_svg_for_authored_three` — cascade_chinook/julia/stones carry a non-empty
   `architecture.svg` starting with `<svg`.
3. `test_architecture_placeholder_for_seven` — the other 7 have `svg is None` and
   `pending_issue == 962`.
4. `test_architecture_svg_pdf_portable` — no `<pattern`/`clip-path`/`clipPath`/`<filter`/`<mask`/
   `url(#` in any embedded architecture SVG.
5. `test_explorer_json_no_nan_inf` — the raw `_explorer.json` text contains no `NaN`/`Infinity`.
6. `test_explorer_identity_with_posters` — (existing) stays green after regeneration.
7. `test_atlas_shell_pins` — (existing) single `<h1>` stays green.
8. `test_portfolio_concepts_helper` — `concept_for()` returns a `FieldConcept` for the 3 ids and
   `None` for the other 7 and for an unknown id.
9. **(r2 finding #2)** `test_architecture_svg_no_script_terminator` — every embedded `architecture.svg`
   contains NONE of `</script`, a backtick, or `${`. This is the invariant that makes the raw-SVG-in-a-
   `<script>const FIELD=…` embed safe; the r2 review proved it holds today (json.dumps escapes newlines
   so the SVG can't forge the `</script>` terminator), but a future `render_layout` change (templated
   labels, an embedded `<style>`/`<script>`) could regress it silently. Cheap, high-value guard.

## 7. Build / test / lint recipe
```
python3 -m venv /tmp/venv-942
/tmp/venv-942/bin/pip install pyyaml pydantic-settings pytest pandas openpyxl
export PYTHONPATH="/tmp/wed-942/src:/tmp/wed-942/packages/worldenergydata-core/src:/tmp/wed-942/packages/worldenergydata-bsee/src"
# regenerate:
/tmp/venv-942/bin/python scripts/lower_tertiary/build_lifecycle_posters.py
/tmp/venv-942/bin/python scripts/field_atlas/build_field_atlas.py
/tmp/venv-942/bin/python scripts/capabilities/build_field_onepagers.py   # PDF one-pagers
# test:
/tmp/venv-942/bin/pytest tests/test_build_pages.py tests/integration/site/ tests/unit/site/ \
  tests/unit/field_development/ tests/unit/lower_tertiary/test_wells_facts.py \
  -o addopts="" --noconftest -q
# lint mirror (exact CI toolchain):
uvx black@25.9.0 <changed .py>
uvx isort@8.0.1 <changed .py>
uvx flake8@7.3.0 --max-line-length=100 --extend-ignore=E203,W503 <changed .py>
```
`python3 -c` is DENIED in this environment → use `python3 - <<'EOF'` heredocs.

## 8. Live-verification steps (after implementation)
1. Open a regenerated `*_lifecycle.html` poster in a browser; confirm the architecture drawing renders
   for julia/stones/cascade_chinook and the placeholder link for the other 7.
2. Serve the site root; open `field-atlas/index.html#/field/julia`; confirm the Explorer architecture
   cardlet renders (no dark screen → JSON is valid).
3. Render a one-pager PDF and open it with `pdftocairo` (NOT Chrome) to confirm the SVG paints with no
   spurious band/artifact (SVG-PDF portability rule).
4. Confirm the browser console is clean (no JSON parse error).

## 9. Adversarial review — RESOLVED (r2 verified every claim by execution)

**r2 verdict: APPROVE-WITH-NITS.** All computational claims reproduced against `/tmp/wed-942` @ `d3647d9`
(SVG byte counts 6689/7634/3682/2689 matched exactly). Resolutions:

1. **cascade_chinook / Chinook (MINOR, product) → RESOLVED as a DECISION in §3.3:** render the Chinook
   tieback (2 trees), captioned **"Chinook subsea tieback"** — honest scope, not "Cascade/Chinook", no
   fabricated 3rd well. (Pre-existing mislabel; `fdp_href` already → `chinook.html`.)
2. **Identity gate — PASS (proven).** Not byte-for-byte; the gate asserts PARSED-object equality
   (`json.loads(FIELD) == explorer["fields"][id]`). Both paths use the SAME
   `json.dumps(indent=2, ensure_ascii=False)` on the SAME shared `fields[id]` dict; neither HTML-escapes.
   With the SVG embedded, `FIELD_JSON_RE` still matches (non-greedy, nested `};` followed by `,`/newline),
   and `parsed poster == parsed sidecar` = True. Survives with NO extra escaping.
3. **Inline `<svg>` injection — PASS (proven).** Every `render_layout` SVG is free of `</script`, backtick,
   `${`, `<!--`. `json.dumps` escapes real newlines (`\n`→`\\n`) so the SVG value sits on one physical line
   and cannot forge the `</script>` regex terminator; `"</script" in html` = False on the built embed. NO
   escaping needed → identity preserved. **A regression guard for this invariant is now TDD test #9** (§6).
4. **Helper module (`portfolio_concepts.py`) — confirmed the right seam** (single reviewable mapping;
   no import cycle — `build_lifecycle_posters` already imports `field_development` modules). NIT: julia's
   concept source (`build_julia_fdp.JULIA`, `num_wells=5/2 manifolds`) disagrees with `_research.json`
   (`num_wells=6`); deliberate ("richest"), documented so a later reviewer won't treat it as a bug.
5. **7 concept-less fields → placeholder (confirmed).** `_facts.json` has ZERO geometry keys for all 10
   fields, so `render_layout` on the 7 would emit a degenerate/misleading 1-tree drawing. Placeholder →
   #962 (OPEN, `docs(fdp)`, on-topic — verified) is correct: honest gap over fake precision.

**Other r2-cleared items:** the new `architecture` key is invisible to `_data_driven_edges` (fixed-key
extractor) and BFS `href_re` (no href in the SVG); `_explorer.json` ~120 KB is 2.4% of the 5 MB
`Check File Sizes` limit (`pr-validation.yml:52`); no test pins the per-field payload key set. r2 NITs #3
(inject `architecture` in `facts_to_field` only — single-source, never per render site) and #4 (julia)
folded above. **Plan is ready for owner review.**
