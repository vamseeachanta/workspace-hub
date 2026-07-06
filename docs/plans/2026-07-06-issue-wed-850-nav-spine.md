# Plan for worldenergydata#850: Navigation spine — breadcrumb + consistent up/down links across Region▸Play▸Field▸Well▸Stage

> **Status:** adversarial-reviewed (r1 Claude MAJOR/8 + r2 Codex MAJOR/10 → r3 inline patch, this revision)
> **Complexity:** T2 — wide but mechanical; helper is stdlib-only; no data/methodology surface.
> **Date:** 2026-07-06 (r3 same day)
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/850 (repo: **worldenergydata**; attestation-vs-repo mismatch is a known tooling artifact)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-06-plan-wed850-claude.md (MAJOR/8, repo-verified @ wed a7f6d272) | ...-codex.md (MAJOR/10; first dispatch timed out at 540s, retry succeeded) — local-only by convention; survey + evidence on the issue.

---

## Resource Intelligence Summary

### Link-graph survey (read-only agent over origin/main; full findings in the #850 issue comment)
- **Publish mapping** (`scripts/build_pages.py`): `lifecycle/**` copied verbatim (underscores kept); `drilling_insights` → `/drilling-insights.html`; `field_development/*` + `decommissioning/*` hyphenated; `capabilities/**` verbatim; economics/benchmark/portfolio/well-path generated at site root by `page()`; `docs/intervention-db/` → `/intervention-db/` (copied by `build_capabilities`).
- **Only one real breadcrumb site-wide**: the norms pages (#848 donor pattern, `build_phase_norms.py:255`, public-layout hrefs).
- **8 dead-end families**; **four competing "up" idioms**; **hub-name collision** ("Life-cycle hub" gallery vs "Life-cycle Insights hub").
- **Two broken hrefs** — r1 verified both verbatim AND located the pa-liability one **in the generator** (`scripts/decommissioning/build_pa_liability_wave.py:382`), not merely the artifact (r1 m1): fix at the generator + regenerate; the insights one is hand-authored (`reports/capabilities/insights.html`, `../../scripts/build_pages.py` → GitHub blob URL).
- **No include mechanism** — crumb must be generator-injected. Generators (r1 verified all exist at these paths): `scripts/lower_tertiary/build_{lifecycle_posters,well_timelines,phase_norms,drilling_insights}.py`, `scripts/field_atlas/build_field_atlas.py`, `scripts/field_development/build_{region_devtype_comparison,all_regions_atlas}.py`, `scripts/decommissioning/build_{pa_liability_wave,regional_liability}.py`, plus `build_pages.py::page()` (root-wrapped pages only — r1 verified no page gets both a generator crumb and a page() crumb, so no double-injection path exists).
- Hand-authored (maintained SOURCE named per Codex F5; build copies these verbatim, so edits survive clean rebuilds — regression-tested below): `reports/capabilities/index.html`, `reports/capabilities/insights.html`, `reports/lower_tertiary/lifecycle/assets/stones_assets.html`, `docs/intervention-db/intervention-stats-brief.html` (r1 verified: truly generator-less; not clobbered by any build step).

### Environment facts (r1 M1/M2 + Codex F7/F8/Q1 — correctness-critical)
- `build_pages.py` has **NO output-dir flag/env**; `PUBLIC` is a module constant. The ONLY safe test seam is the **in-process monkeypatch precedent in `tests/test_build_pages.py`** (import module, monkeypatch `PUBLIC`/`REPORTS` to tmp). The integration gate MUST use it — never a subprocess writing the repo's real `public/`.
- **Pages deploy runs `python scripts/build_pages.py` on bare Python 3.11 with NO project install** (`.github/workflows/pages.yml`); PyYAML is not a runtime dependency (only `types-PyYAML` in dev). **Therefore: the nav helper is STDLIB-ONLY and the registry is JSON**, imported without any third-party dependency. A guard test enforces stdlib-only imports (AST scan of the helper module).
- Build is stdlib-only and sub-second, and `build_pages.py` already supports `--domains` scoping (r1 m6) — no split-fixture mitigation needed.
- `worldenergydata.site` would be auto-discovered by setuptools (r1 verified), BUT the helper must be importable by bare-deploy `build_pages.py` → **single home `scripts/site_nav.py`** (stdlib-only, next to build_pages), imported by generators via the existing sys.path-insert pattern; tests import it by path. flake8 does not cover `scripts/` — accepted trade for deploy parity (black+isort still apply; AST guard keeps imports honest).

### Standards / LLM Wiki
Not applicable.

### Documents consulted
wed#850 + survey comment (issuecomment-4896565456) · epic #754 · #848/#849 shipped plans · `tests/test_build_pages.py` (monkeypatch precedent + 13+ assertions on `page()` output that WILL churn — in Files-to-Change per r1 m5) · `.github/workflows/pages.yml` (bare-python deploy) · skill `workspace-hub-learned/wed-field-hub-drilldown-pages` · drive-file index: no relevant documents.

### Gaps identified
No nav helper; no route manifest; no link-graph gate; the deploy-parity constraint was undocumented anywhere (this plan now records it).

### Evidence (embedded verification)
- Issue states: wed#850 OPEN `status:needs-plan`; #848/#849 CLOSED; #754 OPEN.
- r1 affirmatively verified: all 9 generator paths, `page()` scope, both broken-href strings + correct public-layout fixes, generator-less intervention brief, setuptools discovery, no dual-published page, donor crumb location.
- **Reproduction proofs: N/A — new-feature plan** (the two broken hrefs verified against the publish mapping by two independent reviewers).
- Parallel-work check: no open wed PR/worktree touches these files; re-verify at implementation start (widest-diff lane so far).

## Artifact Map
| Artifact | Kind | Path |
|---|---|---|
| Nav helper | new module (STDLIB-ONLY) | `scripts/site_nav.py` |
| **Route manifest** | new JSON | `config/nav_spine.json` — every scoped public page pattern → family, public dir, injection anchor, trail (labels + hrefs) |
| Generator adoption | edits ×9 + `page()` | list above; pa-liability generator also gets the href fix (r1 m1) |
| Hand-authored edits | ×4 sources | named above (+ insights href fix); marker comment lives in the SOURCE file |
| Tests | new + edit | `tests/unit/site/test_site_nav.py`, `tests/integration/site/test_public_link_graph.py`, **`tests/test_build_pages.py` (existing — page() assertions churn, r1 m5)** |
| Regenerated | artifacts | posters+gallery, wells+index, norms ×5, insight/devtype/atlas/decom pages |

## Deliverable
1. **One crumb component** — `site_nav.render_crumb(page_key, ctx)` emits the norms-style `▸` trail with public-layout hrefs; injected by every family generator and present in the 4 hand-authored sources. **`inject()` FAILS CLOSED** (Codex F4): anchor missing or ambiguous → exception (build stops); marker present → unchanged (idempotent).
2. **Route manifest as single source of truth** (Codex F1/F3/F9/F10 suggestion adopted): `config/nav_spine.json` enumerates every scoped page pattern with family, public path, anchor, and full expected trail. Helper, per-page tests, `page()` contexts, and the link walker are ALL manifest-driven — labels never hardcoded in generators, and `page()` receives an explicit per-callsite route key (no inference; root pages outside the scoped IA are enumerated `crumb: none` and get NO crumb, Codex F1).
3. **Dead-ends eliminated** (8 families) + hub-name collision resolved (gallery = "Life-cycle gallery"; insights = "Insights").
4. **Both broken hrefs fixed at their true sources** (generator + hand-authored source).
5. **Link-graph gate in CI** (fresh-build semantics kill the stale-marker false-pass, Codex F2): integration test imports `build_pages` in-process, monkeypatches `PUBLIC` to tmp (precedent), runs the build so every scoped page is FRESHLY generated, then:
   - asserts every manifest-scoped page EXISTS (kills the vacuous pass, r1 m3),
   - walks `<a href>` AND `src`/`srcset` of scoped pages: zero unresolved internal targets; `X#frag` must match an `id` in the target (r1 m4),
   - asserts marker count == 1 and crumb hrefs/labels EXACTLY equal the manifest trail per page (per-generator regression via fresh render, Codex F2/F9),
   - **reachability**: BFS from `capabilities/index.html` over walked edges reaches every scoped page (real inbound/orphan test, Codex F10). Declared exclusion: the field-atlas's JS-built poster links (r1 m2) — covered by a roster-driven target-exists check plus poster reachability via `lifecycle/index.html`.

### Correctness rules
1. **Public layout only** — trails stored in the manifest AS public hrefs; per-entry depth validity tested for ALL manifest entries against a synthetic public tree (not 3 samples, Codex F3).
2. **Fail-closed injection**; marker lives in maintained sources; clean-build regression proves hand-authored fixes + markers survive `build_pages.py` (Codex F5).
3. **Deploy parity**: helper stdlib-only (AST-scan guard test); registry JSON; zero new runtime deps; `pages.yml` unchanged (r1 M2, Codex F8).
4. **Visual restraint**: crumb only; existing CTAs untouched except the two broken hrefs.

## Pseudocode
```python
# scripts/site_nav.py  (stdlib only: json, pathlib, html)
MARKER = "<!-- nav-spine -->"
def load_manifest(path) -> dict                  # config/nav_spine.json
def trail(page_key, ctx) -> list[(label, href|None)]
def render_crumb(page_key, ctx, manifest) -> str # MARKER + <div class=crumbs>
def inject(html, crumb, anchor) -> str           # fail-closed: MissingAnchorError /
                                                 # AmbiguousAnchorError; idempotent on MARKER
```
Integration test: `import scripts.build_pages as bp; monkeypatch.setattr(bp, "PUBLIC", tmp)` (mirrors `tests/test_build_pages.py`), run, manifest-driven walk as above.

## Files to Change
1. `scripts/site_nav.py` (new, stdlib-only) + `config/nav_spine.json` (new)
2. 9 generators + `build_pages.py::page()` (explicit route keys per callsite)
3. 4 hand-authored sources (+ generator href fix in `build_pa_liability_wave.py`)
4. `tests/unit/site/test_site_nav.py` (new), `tests/integration/site/test_public_link_graph.py` (new), `tests/test_build_pages.py` (update churned assertions)
5. Regenerated artifacts

## TDD Test List (write first, confirm red)
1. `test_trail_matches_manifest_for_every_scoped_entry` — parametrized over ALL manifest entries (labels, hrefs, order).
2. `test_depth_prefixes_valid_for_all_manifest_public_paths` — every entry's hrefs resolve inside a synthetic public tree mirroring the manifest (covers /decommissioning/, /intervention-db/, hyphenated root, lifecycle/**; Codex F3).
3. `test_render_last_node_unlinked_marker_once`.
4. `test_inject_fail_closed_and_idempotent` — missing anchor raises; duplicated anchor raises; marked page unchanged (Codex F4).
5. `test_registry_labels_unique_and_page_keys_total` — label-collision guard + every scoped family has ≥1 manifest entry.
6. `test_page_wrapper_route_keys_explicit` — `page()` callers pass a manifest key; unmapped key raises; `crumb: none` pages get no marker (Codex F1).
7. `test_helper_is_stdlib_only` — AST scan of `scripts/site_nav.py`: stdlib imports only (r1 M2 deploy parity).
8. Integration `test_public_link_graph` (monkeypatched in-process build): manifest pages exist · zero unresolved href/src targets · fragments resolve to ids · marker==1 + exact trail per page · BFS reachability from capabilities · the two fixed hrefs resolve (r1 M1/m3/m4, Codex F2/F6/F10).
9. `test_hand_authored_fixes_survive_clean_build` — after the tmp build, copied capabilities/insights + intervention-brief pages still contain marker + fixed hrefs (Codex F5).
10. `test_roster_poster_targets_exist` — every `_roster.json` lifecycle_id has its poster file (JS-link exclusion coverage, r1 m2).

## Acceptance Criteria
- [ ] Breadcrumb on every manifest-scoped page; 8 dead-end families eliminated; hub collision resolved via the manifest (single label set)
- [ ] Link-graph gate in CI via the in-process monkeypatch seam: existence + resolution (href/src/fragments) + exact-trail + BFS reachability, all manifest-driven — zero unresolved targets and zero unreachable scoped pages; field-atlas JS-link exclusion documented and roster-checked
- [ ] Helper stdlib-only (guard test) — bare-python Pages deploy unaffected; zero new runtime deps
- [ ] Both broken hrefs fixed at their true sources and regression-tested through a clean build
- [ ] `tests/test_build_pages.py` updated and green; PR screenshots: poster, well page, insight page, capabilities, one economics page (page() blast-radius visual check)

## Risks
1. Widest-diff lane (regenerated artifacts) → single-lane worktree; re-check parallel work at start.
2. `page()` route-key threading touches many callsites → explicit keys + test 6; screenshots for visual QA.
3. Helper outside flake8 scope (`scripts/`) → accepted trade for deploy parity; black+isort apply; AST guard keeps imports honest.
4. Hand-authored capabilities pages churn under other lanes → coordinate at implementation; marker keeps re-injection idempotent.
5. CI lint at lockfile pins (black 25.9.0 / isort 8.0.1 / flake8 7.3.0 on src/); PR title subject ≤80; `./.venv/bin/python -m pytest`.

## Adversarial Review Summary
- **r1 (Claude subagent, repo-verified @ wed a7f6d272): MAJOR/8.** Clean-verified list in the artifact.
- **r2 (Codex, retry after a 540s timeout on the first dispatch): MAJOR/10.**
- **r3 (this revision, inline per `feedback_r3_inline_loop_break_pattern`)** — finding→patch: test seam = monkeypatch precedent (r1 M1, Codex F7/Q1); stdlib-only helper + JSON manifest + AST guard (r1 M2, Codex F8); generator-located href fix (r1 m1); route manifest drives depth tests + label contract + page() keys (Codex F1/F3/F9); fail-closed inject (Codex F4); fresh-build per-generator regression + marker exactness (Codex F2); fragment checks (r1 m4); manifest-existence kills vacuous pass (r1 m3); BFS reachability = real orphan test (Codex F10); JS-link exclusion + roster check (r1 m2, Codex F6); hand-authored source-of-truth + clean-build survival (Codex F5); `tests/test_build_pages.py` in scope (r1 m5); Risk-3 split-fixture removed (r1 m6); walker widened to src/srcset with declared exclusions (Codex F6).
- Awaiting user approval; not self-labeled.
