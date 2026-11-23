# Plan for worldenergydata#946: Explorer-shell tracer — Jack/St Malo + Big Foot end-to-end in the one-page shell

> **Status:** adversarial-reviewed (r1 Fable subagent MAJOR/5 + MINOR/5, repo-verified @ wed faf1de1f → r2 this revision, all findings folded)
> **Complexity:** T2 — one new sidecar + one page template rework; no data/methodology surface; stdlib-only build code.
> **Date:** 2026-07-10
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/946 (parent epic #940, program #939)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** r1 findings summarized in the #946 evidence comment (subagent, all G-facts + code paths independently verified against origin/main @ faf1de1f); local-only by convention.

---

## Resource Intelligence Summary

### Sources consulted (grounded on a shallow LOCAL clone of origin/main @ `faf1de1f` — never the FUSE working copy)
- **Issue #946 + program epic #939 / E0 epic #940** — acceptance criteria and locked owner decisions (rebuild `/field-atlas/` in place; page functional at every merge).
- **`scripts/field_atlas/build_field_atlas.py` (185 lines)** — atlas page generator: template inline in the script, roster embedded via `__ROSTER_JSON__`, `lifecycle_id` computed at build time via `fields_registry.resolve()` (L34–37) and embedded in the page; published as `public/field-atlas/index.html` ONLY (`build_pages.py:817-822`).
- **`scripts/lower_tertiary/build_lifecycle_posters.py`** — enriched per-field payload built by `facts_to_field()` (L113, return L283–318: `wellsHref`, `wellsCount`, `assetsHref`, `economics_href`, `benchmark_href`, `metrics`, `gates`, `spans`, `hostFacts`, `reservoir`, `provenance`, …); **`main()` then attaches `field["norms"]` (L433) and `field["performance"]` (L434) BEFORE `render()` embeds it** as `const FIELD` via `__FIELD_JSON__`. The full enriched payload exists ONLY page-embedded today.
- **`scripts/build_pages.py` publish surface (L429–469)** — lifecycle publishes posters + gallery + `_norms.json` + `_performance.json`; `_facts.json` skipped deliberately (L431); `wells/*_well.html` + wells index only, `_wells.json` never copied. Live probes agree: `_performance.json`/`_norms.json` HTTP 200; `_roster.json`/`_facts.json`/`wells/_wells.json` 404.
- **`scripts/site_nav.py` + `config/nav_spine.json`** — stdlib fail-closed nav spine; atlas page key `atlas`, anchor `<h1` mode `before`; `inject()` raises `AmbiguousAnchorError` when the anchor substring occurs more than once **anywhere in the page string, including inside `<script>`** (L110–114). `internal_targets()` skips `${…}` template literals and pure-`#` hrefs (L139–141).
- **`tests/integration/site/test_public_link_graph.py`** — link-graph gate: BFS from capabilities (L193), `test_data_driven_edges_resolve` parses poster `const FIELD` and resolves hrefs relative to the POSTER's directory (L114–116, 180–190); `test_roster_poster_targets_exist` (L237–246) reads on-disk `_roster.json`, which contains **zero `lifecycle_id` keys → the check is vacuous today** (r1 f3).
- **`config/repo_structure.yml` + `scripts/maintenance/verify_repo_structure.py` (pre-commit)** — reports exceptions are an exact-path `allowed_paths` list; precedents: `lifecycle_template.html` (L365), `_performance.json` (L352), `wells/_wells.json` (L440).
- **CI:** `ci.yml:158-168` Lint = black+isort on `src/ tests/`, flake8 `src/` only (`--max-line-length=100 --extend-ignore=E203,W503`); `pr-validation.yml` conventional PR type + subject ≤80 chars; `pages.yml` deploy = bare python3.11, **no dependency install** → all build code stdlib-only.
- **Prior plans/patterns:** #850 nav-spine (manifest + fail-closed inject + monkeypatch test seam), #756 `_performance.json` single-sourcing byte-identity (`test_performance_contract.py:132-137`).
- Drive-file search: not applicable — pure site-shell slice over in-repo artifacts; no external documents in scope.

### Gaps identified
No fetchable enriched field payload (page-embedded only); no wells data published; no shell/router; JS-built-link gate coverage is a hollow precedent that must be made real (r1 f3); no rebase rule for lifecycle-relative hrefs consumed outside `lifecycle/`.

### Parallel-work check
Codex lane #757 touches the poster economics link-card (payload keys `economics_href`/`benchmark_href` already on main and gate-tested — this plan only ADDS a sidecar writer, no key changes). Subsea7 lanes (wed #931/#932) touch other files. Re-verify open PRs at implementation start; work in a fresh worktree/clone off origin/main.

## Goal

Prove the one-page Explorer architecture on one vertical slice: `/field-atlas/` (rebuilt in place, zero feature loss) lets a client select **Big Foot** and flow high-level → detail **without leaving the page** — field panel (lifecycle summary + performance + reservoir + economics/benchmark links) → wells panel → **A004 stage detail** — every state deep-linkable via URL hash. **Jack/St Malo** proves honest degradation (no wells yet).

## Non-goals (tracer discipline)

- NO new data ingest, NO play backfill (#947), NO wells beyond Big Foot (#948), NO architecture drawing (E2), NO lens panels (E3).
- The shell does NOT re-implement the full poster or well-timeline rendering: panels are **summary altitude**; static pages remain the deep-dive and are linked prominently (two-altitude contract, #754).
- No framework, no build-tooling change: static HTML+JS; stdlib-only Python build (deploy-parity contract, #850).

## Artifact Map

| Artifact | Kind | Path |
|---|---|---|
| Explorer sidecar | new generated JSON (committed) | `reports/lower_tertiary/lifecycle/_explorer.json` |
| Sidecar writer | edit | `scripts/lower_tertiary/build_lifecycle_posters.py` (serialize the **post-enrichment** field dicts in `main()`) |
| Sidecar publish | edit | `scripts/build_pages.py::build_lower_tertiary` (next to `_performance.json`) |
| Atlas template | new file (extracted) | `reports/field-atlas/atlas_template.html` |
| Atlas generator | edit (shrinks to data-prep + substitution + nav-inject) | `scripts/field_atlas/build_field_atlas.py` |
| Structure allowlist | edit (BOTH new paths, r1 f4) | `config/repo_structure.yml`: `_explorer.json` + `atlas_template.html` |
| Tests | new + edit | `tests/test_build_pages.py`, `tests/integration/site/test_public_link_graph.py`, `tests/unit/site/` |
| Regenerated | artifacts (committed) | `reports/field-atlas/index.html`, `reports/lower_tertiary/lifecycle/_explorer.json`; posters expected byte-identical (assert in PR review) |

## Design decisions (r2 — r1 findings folded inline)

**D1 — One new published sidecar: `lifecycle/_explorer.json`, single-sourced from the post-enrichment payloads (r1 f1).**

```json
{
  "meta": {"generated_by": "build_lifecycle_posters.py", "issue": 946},
  "fields": {"<id>": <the enriched dict from main(): facts_to_field() + norms + performance>},
  "wells": <verbatim content of wells/_wells.json>
}
```

The `fields` values are the very dicts `main()` embeds into each poster (captured AFTER the `norms`/`performance` attach at L433–434), serialized once — identity by construction, verified by gate D6(c). `wells` embedded verbatim → the shell makes **one fetch total**; the payload's own `performance` key supersedes any separate `_performance.json` fetch (r1 f9). Published by `build_lower_tertiary()` next to `_performance.json`; **the sidecar is a committed report artifact** (Pages builds from frozen reports — an emitted-but-uncommitted sidecar deploys nothing, r1 f6).

*Rejected:* publishing `_facts.json` (raw, lacks computed edges; skip was deliberate); shell scraping `const FIELD` from posters (fragile, N fetches); iframing posters (double chrome, breaks one-page + hash routing).

**D2 — Shell = same page, progressive enhancement, template extracted; in-place panels are RICH-ONLY (r1 f5).**
Template moves to `reports/field-atlas/atlas_template.html` (mirrors `lifecycle_template.html`; generator becomes loader + `__ROSTER_JSON__` substitution + nav-inject; extraction is a separate no-behavior commit). Funnel/search/tier-chips/story markup unchanged. New hidden panel `<section>` below the grid. **Only cards with a non-null `lifecycle_id` (the 10 rich fields) get click-to-open panels; the other 110 sample/roadmap cards keep exactly their current behavior** (tier badge + no drill) — they have no payload and no stable id to route to; upgrading them is #947's job (E1 owns the id federation). The `Life-cycle →` anchor stays a real href (middle-click/no-JS/SEO front door). `_explorer.json` fetched lazily on first panel open, cached in memory; fetch failure renders a visible panel error + the page degrades to current behavior (no silent catch).

**D3 — Hash router: `#/field/<id>` · `#/field/<id>/wells` · `#/field/<id>/wells/<slot>`.**
Hash-only (no pushState — Pages has no rewrites). On load: parse → restore → scroll into view. Unknown id/slot fails soft (visible "unknown field" panel message; funnel unaffected). JS breadcrumb inside the panel (`Atlas ▸ Big Foot ▸ Wells ▸ A004`), each crumb an `<a href="#/…">`. **Router links are always bare `#/…`** — never `index.html#/…`, which the BFS would capture and fail as a phantom fragment (r1 f8).

**D4 — Panels = summary altitude + explicit href-rebase rule (r1 f2).**
All payload hrefs are lifecycle-relative (`wellsHref: "wells/"`, `assetsHref: "assets/<id>_assets.html"`, `economics_href: "../economics-<id>.html"`). The shell resolves EVERY payload href through one resolver against the sidecar's home: `resolve(h) = new URL(h, new URL("../lifecycle/", document.baseURI))` — no href is ever emitted verbatim into the panel DOM.
- *Field panel:* header (name/operator/status/tree badge); compact stage strip from `gates`+`currentPhase` (you-are-here, no spans re-render); `metrics` row; `hostFacts`; `reservoir` card when present; performance snapshot from the payload's `performance` key; action row: `Full poster →`, `Economics →`/`Benchmark →` (when present), `Wells (n) →` (when `wellsHref`), `Assets →` (when `assetsHref`).
- *Wells panel:* table from `wells.wells` filtered by `field_id` (slot, spud, rig days, TVD, first oil, cum oil, uptime, status); row click → stage detail.
- *Stage detail (A004):* stage cards Spud→Drill→Complete→First oil→Workover→Producing from the well record + `Full well timeline →` (rebased `wells/big_foot_A004_well.html`).
- *Jack/St Malo:* same field panel; wells action renders as a plain note "Well-level timelines: Big Foot only — rollout #948". No dead links ever rendered.
- *Template hygiene (r1 f7):* panel markup/renderers must not contain the literal `<h1` (nav-spine `inject()` fails closed on a second occurrence anywhere in the page string, including inside `<script>`); page keeps exactly one nav MARKER.

**D5 — Zero-regression contract for rebuild-in-place.**
Pins land first: embedded-ROSTER entry count == 120 (counted from the embedded JSON, not client DOM — r1 f10), funnel select ids, search box, tier chips, `Life-cycle →` hrefs present for rich entries, nav crumb marker once.

**D6 — Gate extension: make the JS-built-link coverage REAL (r1 f2, f3).**
JS-built hrefs stay excluded from HTML scraping (declared exclusion); coverage is data-side on the PUBLISHED `_explorer.json`:
(a) every href field in `fields.*` resolves to an existing file **from BOTH bases** — `lifecycle/` (poster parity) AND the shell's rebase rule (`field-atlas/` context via the `../lifecycle/` base) — the existing `_resolve` helper is reused with the correct base per check;
(b) every well in `wells.wells` has its `wells/<field_id>_<slot>_well.html` page published;
(c) sidecar identity: each poster's parsed `const FIELD` == `_explorer.json["fields"][id]` (consistent with D1 because the sidecar serializes the post-enrichment dicts);
(d) `_explorer.json` published whenever posters are;
(e) **repair the vacuous roster check**: the test recomputes `lifecycle_id` via `fields_registry.resolve()` exactly as the generator does (L34–37) and asserts each resolved rich roster entry has its poster AND its `_explorer.json` entry — real assertions replacing the always-None path.

**D7 — Local preview honesty.** `fetch()` fails on `file://`; sanctioned preview documented in the template header: `python3 -m http.server` from `public/`. No code path depends on `file://`.

## Implementation steps

| # | Step | Files |
|---|---|---|
| T1 | Emit `_explorer.json` from the post-enrichment dicts in `main()` + verbatim `_wells.json`; commit the artifact | `build_lifecycle_posters.py`, `reports/.../lifecycle/_explorer.json` |
| T2 | Publish it in `build_lower_tertiary()`; allowlist BOTH `_explorer.json` and `atlas_template.html` | `build_pages.py`, `config/repo_structure.yml` |
| T3 | Extract atlas template (no-behavior commit; regenerated `index.html` byte-comparable) | `build_field_atlas.py`, `atlas_template.html` |
| T4 | Shell: panel section, hash router (bare `#/…`), lazy fetch+cache with visible error path, href resolver, renderers, JS breadcrumb, honest-degradation notes, no literal `<h1` in script strings | `atlas_template.html` |
| T5 | Regenerate + commit `field-atlas/index.html` and `_explorer.json`; assert posters byte-identical | generated artifacts |
| T6 | Tests: (a) D5 pins; (b) D6(a–e) gate additions; (c) `_explorer.json` publish test via the monkeypatch seam; JS itself is untested — coverage is data-side (stated honestly; the Python-mirror-of-JS-regex idea is dropped as brittle, r1 f10) | `tests/test_build_pages.py`, `test_public_link_graph.py`, `tests/unit/site/` |
| T7 | Lint mirror (exact black/isort/flake8 + flags); PR `feat(explorer): …` subject ≤80; auto-merge armed; post-deploy live verify (200s + one hash deep-link `#/field/big_foot/wells/A004` manually) | — |

Diff: 3 scripts (r1 f10), 1 template file, ~3–4 test files, 1 config, 2 committed generated artifacts. No `src/` changes (flake8 surface unchanged).

## Acceptance mapping (issue #946 → plan)

| Criterion | Delivered by |
|---|---|
| 120 fields, funnel/search/chips no regression | D2, D5, T6a |
| Big Foot panel in place (lifecycle summary, performance, reservoir, economics card) | D1, D4 |
| A004 stage detail in place from wells data | D4 |
| Jack/St Malo honest no-wells note, no dead link | D4, D6 |
| URL hash restores state; breadcrumb navigates up | D3 |
| Gates green incl. new edges; stdlib-only build | D6, T2, G-facts (pages.yml) |

## Risks & mitigations

- **R1 sidecar drift vs posters** → identity by construction (same dicts) + D6(c).
- **R2 live-funnel regression** → pins first (T6a), extraction isolated (T3), post-deploy live verify (T7).
- **R3 sidecar growth at all-countries scale** → tracer scopes to 10 LT payloads (~40 KB); sharding decision explicitly handed to E1 wave 1 (#947), not silently deferred.
- **R4 known test flake under box contention** (pressure-atlas/registry reds) → rerun in isolation before declaring red.
- **R5 parallel lanes** → additive-only payload writer (no key changes); rebase check before PR; fresh clone/worktree off origin/main; NEVER the FUSE checkout (porcelain git hangs on `/mnt/local-analysis`).

## Ops notes for the implementer

- Test recipe: `./.venv/bin/python -m pytest tests/test_build_pages.py tests/integration/site/ tests/unit/site/ -o addopts="" --no-cov -q`.
- Merge: agent verifies, human merges (`gh pr merge <N> --squash --delete-branch --repo vamseeachanta/worldenergydata`).
