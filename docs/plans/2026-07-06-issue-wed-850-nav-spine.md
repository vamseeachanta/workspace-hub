# Plan for worldenergydata#850: Navigation spine — breadcrumb + consistent up/down links across Region▸Play▸Field▸Well▸Stage

> **Status:** draft
> **Complexity:** T2 — wide but mechanical: one tested helper + snippet adoption across 9 generators + 4 hand-authored pages; no data/methodology surface.
> **Date:** 2026-07-06
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/850 (repo: **worldenergydata**; attestation-vs-repo mismatch is a known tooling artifact)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-06-plan-wed850-claude.md | ...-codex.md (local-only by convention)

---

## Resource Intelligence Summary

### Link-graph survey (dedicated read-only agent over origin/main, 2026-07-06 — full findings preserved in the #850 issue comment posted with this plan)
- **Publish mapping** (`scripts/build_pages.py`): `lifecycle/**` copied verbatim (underscores kept); `drilling_insights` → `/drilling-insights.html`; `field_development/*` + `decommissioning/*` hyphenated (root and `/decommissioning/`); `capabilities/**` verbatim; economics/benchmark/portfolio/well-path generated at site root by the `page()` wrapper; `docs/intervention-db/` copied under `/intervention-db/`.
- **Only ONE real breadcrumb exists on the whole site**: the norms pages (#848, `build_phase_norms.py`) — `Capabilities ▸ Life-cycle hub ▸ Phase norms ▸ Stage`, written for the PUBLIC layout. This is the donor pattern.
- **8 dead-end families** (no way back up): `drilling-insights.html` (0 hrefs), `region-devtype-comparison.html` (0 hrefs), `intervention-db/intervention-stats-brief.html` (0 hrefs), lifecycle posters (no gallery/capabilities link), `lifecycle/index.html`, well pages + `wells/index.html`, `field-atlas/index.html`, `all-regions-atlas.html`/`pa-liability-wave.html` (lateral only).
- **Four "up" idioms coexist**: `page()` header `← worldenergydata`; `.crumb` `← Capabilities` (insights) / `← Life-cycle insights hub` (regional-liability); norms `▸` trail; bare `../`. **Hub-name collision**: norms' "Life-cycle hub" = `/lifecycle/index.html` while insights.html titles ITSELF "Life-cycle Insights hub".
- **Two concretely broken hrefs**: `reports/decommissioning/pa_liability_wave.html` (`../../docs/intervention-db/…` → 404 in public; must be `../intervention-db/…`) and `reports/capabilities/insights.html` (`../../scripts/build_pages.py` escapes the site root).
- **No include/partial mechanism exists** — every page is self-contained HTML. A shared crumb must be a **generator-injected snippet**. Generators needing it: `build_lifecycle_posters.py` (posters+gallery), `build_well_timelines.py` (wells+index), `build_phase_norms.py` (donor, refactor to helper), `build_drilling_insights.py`, `field_atlas/build_field_atlas.py`, `field_development/build_region_devtype_comparison.py` + `build_all_regions_atlas.py`, `decommissioning/build_pa_liability_wave.py` + `build_regional_liability.py`, and `build_pages.py::page()` (one edit covers all root-wrapped pages). Hand-authored direct edits: `capabilities/index.html`, `capabilities/insights.html`, `lifecycle/assets/stones_assets.html`, `docs/intervention-db/intervention-stats-brief.html` (frozen artifact, NO generator — a future regeneration cannot exist, but mark the edit with a comment).
- Orphans: none at family level; weakest inbound is wells (only big_foot poster links down — data reality: 9/10 fields have no well pages; chips already degrade, NOT a nav defect, out of scope).

### Existing repo code
- Donor crumb CSS/markup: `scripts/lower_tertiary/build_phase_norms.py` (merged #862). Precedent for src-module + tests: `phase_norms.py`, `well_economics.py` (both `src/worldenergydata/field_development/`).
- CI: black+isort on `src/ tests/`, flake8 on `src/` only; `uv.lock` pins black 25.9.0 / isort 8.0.1 / flake8 7.3.0; PR-title subject ≤80; tests via `./.venv/bin/python -m pytest`.

### Standards / LLM Wiki
Not applicable (site navigation; no standards-derived constants, no wiki content).

### Documents consulted
wed#850 (contract) · epic #754 both-altitudes comment · #848/#849 shipped plans (chips/econ cards create the deep pages this spine serves) · `docs/plans/README.md` (rows for wed#848/#849) · skill `workspace-hub-learned/wed-field-hub-drilldown-pages` · drive-file index ("site navigation breadcrumb information architecture", `--caller plan-resource-intel`): no relevant documents.

### Gaps identified
No shared nav helper; no canonical trail/label registry; no automated link-graph gate (published-site orphan/dead-end regressions are currently invisible).

### Evidence (embedded verification)
- Issue states: wed#850 OPEN `status:needs-plan`; #848/#849 CLOSED (merged #862/#864); #754 OPEN epic.
- Survey evidence: agent read `build_pages.py` mapping + every family template/generator on origin/main; per-family href quotes in the survey (posted to the issue).
- **Reproduction proofs: N/A — new-feature plan**; the two broken hrefs were verified against the publish mapping (survey section "Concrete broken links").
- Parallel-work check: no open wed PR/worktree touches these generators/templates (post-#862/#864 fetch); single-lane worktree off fresh origin/main; re-verify at implementation start (this plan touches MANY generated artifacts — the widest-diff lane in the family so far).

## Artifact Map
| Artifact | Kind | Path |
|---|---|---|
| Nav helper | new module | `src/worldenergydata/site/nav_spine.py` (+ `site/__init__.py`) |
| Trail registry | new YAML | `config/nav_spine.yml` (labels, per-family trails, public-path depths) |
| Generator adoption | edits ×9 + `page()` | scripts listed in survey §E |
| Hand-authored edits | ×4 | capabilities index + insights, stones_assets, intervention brief (+ the 2 broken-href fixes) |
| Link-graph gate | new test | `tests/unit/site/test_nav_spine.py` (helper units) + `tests/integration/site/test_public_link_graph.py` (build → walk) |
| Regenerated | artifacts | posters+gallery, wells+index, norms ×5, insights/devtype/atlas/decom pages |

## Deliverable
1. **One crumb component** (`nav_spine.render_crumb(family, context)`) emitting the norms-style `▸` trail with **public-layout hrefs**, injected by every family generator and pasted into the 4 hand-authored pages. Idempotent injection (marker comment `<!-- nav-spine -->`), theme-aware CSS inline in the snippet.
2. **Canonical trail registry** (`config/nav_spine.yml`): `Home ▸ Capabilities ▸ {Field atlas | Life-cycle gallery | Insights} ▸ {Field poster} ▸ {Wells | Assets | Phase norms ▸ Stage}` — one label per node, resolving the hub-name collision (`/lifecycle/index.html` = "Life-cycle gallery"; `/capabilities/insights.html` = "Insights"). Down-link CTAs keep their existing styling; only the UP grammar is unified.
3. **Dead-ends eliminated**: the 8 listed families each gain the crumb (their first up-link, for three of them their first href at all).
4. **Two broken hrefs fixed** (pa-liability-wave → `../intervention-db/…`; insights build-note → GitHub blob URL).
5. **Link-graph gate in CI**: integration test runs `build_pages.py` into a tmp dir, walks every internal href/anchor in the scoped families, asserts (a) zero unresolved targets, (b) every scoped page contains the nav-spine marker, (c) zero dead-ends (≥1 uplink per page). Future pages that forget the spine fail the build.

### Correctness rules
1. **Public layout only**: crumb hrefs computed from each page's PUBLIC path (registry stores the public dir; helper computes `../` depth). The norms donor proved source-relative intuition is wrong.
2. **Idempotent + clobber-safe**: injection keyed on the marker; hand-authored edits carry the marker too so a future generator can adopt them without duplication. Intervention brief edit noted as direct-artifact change (no generator exists).
3. **No label drift**: all trail labels come from the registry — generators never hardcode a hub name (kills the two-hubs collision permanently).
4. **Visual restraint**: crumb only (one line, muted); no redesign of any page; existing down-link CTAs untouched except the 2 broken hrefs.

## Pseudocode
```python
# src/worldenergydata/site/nav_spine.py
MARKER = "<!-- nav-spine -->"
def load_registry(path=None) -> dict            # config/nav_spine.yml
def trail_for(family: str, ctx: dict) -> list[tuple[label, href|None]]
def render_crumb(family, ctx, registry) -> str  # marker + <div class=crumbs>…</div>, last node unlinked
def inject(html: str, crumb: str, anchor: str) -> str  # idempotent via MARKER
def public_depth(public_dir: str) -> str        # "lifecycle/norms" -> "../../"
```
Integration test: run `build_pages.py` (subprocess, tmp `PUBLIC`), `html.parser`-walk scoped families' internal hrefs + `#anchors`, assert resolution + marker presence + ≥1 uplink.

## Files to Change
1. `src/worldenergydata/site/{__init__,nav_spine}.py` (new)
2. `config/nav_spine.yml` (new)
3. 9 generator scripts + `build_pages.py::page()` (survey §E list)
4. 4 hand-authored pages (+ 2 broken-href fixes; intervention brief marked)
5. `tests/unit/site/test_nav_spine.py`, `tests/integration/site/test_public_link_graph.py` (new)
6. Regenerated artifacts (posters, gallery, wells, norms, insight pages)

## TDD Test List (write first, confirm red)
1. `test_trail_for_each_family_matches_registry` — parametrized over all scoped families; labels/order exact.
2. `test_hrefs_computed_for_public_depth` — `/lifecycle/norms/` page → `../../capabilities/index.html`; root page → `capabilities/index.html`; wells → `../../…`.
3. `test_render_crumb_last_node_unlinked_and_marked` — current page label plain text; MARKER present exactly once.
4. `test_inject_idempotent` — double-inject → single crumb; inject into page already carrying marker → unchanged.
5. `test_registry_labels_unique` — no two nodes share a label (hub-collision regression guard).
6. `test_page_wrapper_carries_crumb` — `page()` output contains marker + correct root-depth trail.
7. Integration: `test_public_link_graph` — after a real `build_pages.py` run: all scoped internal hrefs resolve; every scoped page has MARKER; every scoped page ≥1 uplink; the two previously-broken hrefs resolve.
8. `test_no_hardcoded_hub_labels_in_generators` — grep guard: generator sources contain no trail-label string literals (registry-only).

## Acceptance Criteria (mirrors wed#850)
- [ ] Breadcrumb trail on every scoped page (8 dead-end families eliminated), each segment a working PUBLIC-layout link up
- [ ] Automated link-graph check: zero orphans, zero dead-ends, zero unresolved internal hrefs among scoped families — running in CI
- [ ] Insight front doors ↔ stage cards cross-links intact (regression-checked by the walker)
- [ ] One trail registry; hub-name collision resolved; no generator hardcodes labels
- [ ] The 2 broken hrefs fixed and regression-tested; PR screenshots show the crumb on a poster, a well page, an insight page, and capabilities

## Risks
1. **Widest-diff lane yet** (many regenerated artifacts) → single-lane worktree; re-check parallel work at start; keep the crumb snippet additive so diffs stay mechanical.
2. **Hand-edit clobber**: `stones_assets.html`/intervention brief have no generators — marker comment + note in each file header; capabilities pages are hand-maintained (coordinate if another lane touches them).
3. **build_pages integration test cost**: full build in CI may be slow → scope the walker to the copied families; if wall-clock excessive, split build once per session-scoped fixture.
4. **`page()` wrapper edit touches all root pages** → visual check on 2 representative economics pages in PR screenshots.
5. CI lint: helper lives in `src/` (flake8-gated); mirror all three linters at lockfile pins; PR title subject ≤80.

## Adversarial Review Summary
PENDING — T2: r1 Claude subagent (repo-verified) + r2 Codex; r3 inline per `feedback_r3_inline_loop_break_pattern` if MAJOR.
