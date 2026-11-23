# Plan for digitalmodel#1444: Capabilities IA simplification — cluster spec + recently-added strip + citable reference index

> **Status:** adversarial-reviewed (r1 Claude MAJOR/8 + r2 Codex MAJOR/10 → r3 inline patch, this revision)
> **Complexity:** T2 — spec + tested extractor; NO index.html edits (revamp lane owns presentation).
> **Date:** 2026-07-06 (r3 same day)
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/1444 (repo: **digitalmodel** — attestation-vs-repo mismatch is a known tooling artifact)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-06-plan-dm1444-claude.md (MAJOR/8, repo-verified @ dm 0cdf1104) | ...-codex.md (MAJOR/10) — local-only by convention

---

## Resource Intelligence Summary

### Existing repo state (probed + r1 re-verified against digitalmodel `origin/main` @ 0cdf1104)
- `docs/api/capabilities/index.html`: 22 sections, flat 22-entry nav — **and r1 verified all 22 sections carry ids with a 1:1 nav-href mapping** → the anchor-stability contract is feasible and test-enforceable as a bijection.
- **Explorer census corrected (r1 M1)**: `docs/api/structural/` holds **9 explorer HTML + 9 JSON sidecars** (my original "18" conflated them); **8 more live explorers sit in 6 other `docs/api/` dirs**; **6 frozen duplicates under `docs/api/capabilities/api/` must be EXCLUDED**. Discovery = `docs/api/**/*-explorer.html` minus `capabilities/api/`, census asserted against the live tree (never a literal count).
- **PDF registry join key verified clean (r1 M3-positive)**: `scripts/capabilities/build_onepagers.py` SPECS ids use `sec-<anchor>` → mechanical section→PDF join. Coverage today: **12/22 sections** — the 10-section gap set is enumerated in the spec as explicit `gap` rows (r1 m1).
- **Section→explorer has NO stem key** (r1 M3): the only mechanical join is **parsing hrefs INSIDE each `<section>` block** (the page already links its explorers); leftovers resolved via a reviewed alias map; unmatched artifacts listed as `unlinked`, never guessed.
- **Git history is TRUNCATED — 19 commits since the 2026-07-04 slim (root 19e8eae3)** (r1 M2): local `git log` cannot date anything pre-slim. All git-derived recency dating is DEAD (also Codex F1: in-file sections never had file-add events).
- **dm CI routes pytest via `tests/DOMAINS.md`** (r1 M4): a new `tests/capabilities/` suite runs in CI only if a DOMAINS.md row is added — in scope.
- SPECS is stdlib-only and direct-file-loadable, but via **importlib on the real path** (it builds `dict()`s and reads the logo asset at import — AST parsing won't work) (r1 m2).
- Revamp lane: still not in git; `docs/capability-map/` exists, content compatible (r1-verified).

### Standards / LLM Wiki
Not applicable.

### Documents consulted
dm#1444 · dm#1391/#1388/#1411 (section + explorer + PDF programs) · PR #1389 coordination note · memory `project_dm_capabilities_page_expansion` + `reference_squash_merge_reachability_false_orphan` (the .git slim precedent behind r1 M2) · wed#850 shipped manifest/link-gate pattern · drive-file index: no relevant documents.

### Gaps identified
No cluster taxonomy; no machine inventory; no recency metadata (and no git substrate to derive it); no anchor contract; no CI wiring for a capabilities test domain.

### Evidence (embedded verification)
- Issue states: dm#1444 OPEN; no revamp PR open/merged.
- r1 verified: 22 ids + nav bijection; explorer/dupe census; SPECS `sec-<anchor>` ids + 12/22 coverage; 19-commit history; DOMAINS.md routing; capability-map dir; SPECS importlib feasibility.
- **Reproduction proofs: N/A — spec/documentation issue.**
- Parallel-work check: content lanes (#1441-#1446) touch section interiors, not this spec's files; coordinate only if the revamp awakens.

## Artifact Map
| Artifact | Kind | Path (digitalmodel) |
|---|---|---|
| IA spec (human, rendered) | new doc | `docs/capability-map/capabilities-ia-spec-1444.md` |
| Cluster map (machine SoT) | new YAML | `docs/capability-map/capabilities-clusters.yml` (Codex F10 — separate file, schema-tested; the MD renders FROM it) |
| Inventory (machine) | generated JSON | `docs/capability-map/capabilities-inventory.json` |
| Recency metadata | new YAML | `docs/capability-map/capabilities-added.yml` — frozen `added: {date, pr}` per section/explorer, **seeded once from `gh pr list` metadata** (network step at implementation, documented), maintained by hand thereafter; entries without evidence carry `added: unknown` honestly (r1 M2, Codex F1) |
| Extractor | new tested script | `scripts/capabilities/build_capabilities_inventory.py` (+ `--check` freshness mode, Codex F4) |
| Tests + CI wiring | new + edit | `tests/capabilities/test_capabilities_inventory.py` + **`tests/DOMAINS.md` capabilities row** (r1 M4) |

## Deliverable
1. **Cluster taxonomy** — every section in exactly one of **7 clusters** (r1 m4; Structures & FFS · Pipelines & Risers · Moorings & Stationkeeping · Hydrodynamics & Naval Architecture · Wells & Drilling · Field Development & Economics · Installation & Marine Ops), held in `capabilities-clusters.yml`; totality/disjointness tested against the live page census; an unclustered new section FAILS the capabilities test domain in CI (Codex F7).
2. **Recently-added strip model** — top-N from `capabilities-added.yml` (explicit metadata; no git derivation — the substrate does not exist post-slim). Display contract (N, fields, ordering) defined for the revamp owner; `unknown` recency renders honestly.
3. **Citable reference index** — section → explorer(s) → PDF → API page → validation anchor. Joins: in-section href parse (explorers) + SPECS `sec-<anchor>` (PDFs) + alias map for residuals; tests enforce one-to-one, no ambiguity, `gap`/`unlinked` rows explicit (10 PDF gaps enumerated) (Codex F3, r1 M1/M3/m1).
4. **Anchor-stability contract** — bijection nav-href ↔ section-id enumerated and test-locked; revamp must preserve it (wed#850 manifest/link-gate cited as the enforcement pattern).
5. **Governance** (Codex F6): AC requires the owner's explicit acceptance comment on dm#1444 (link evidence) before close — not just a thread tag. Spec-only boundary is itself an AC verified on the PR diff (Codex F9).

### Correctness rules
1. **Generated + freshness-gated**: spec tables render from the inventory; extractor `--check` compares committed artifacts to a fresh run and FAILS on drift (CI-run via the DOMAINS row); a documented regeneration command lives in the spec (Codex F4, r1 m3).
2. **One section, one cluster; unknowns fail closed** with actionable diagnostics (missing id, duplicate anchor, nav-only, section-only — all fixture-tested, Codex F2/F8).
3. **No presentation edits**: final diff must exclude `docs/api/capabilities/index.html` and page CSS/JS (AC-verified).
4. **Engine references**: use `docs/registry/module-routing.yaml` IF present at implementation start; if absent/renamed, the engine column is `n/a` with a named follow-on — never a third invented scheme (Codex F5).
5. **SPECS loaded via importlib real-path** (r1 m2); dm env `.venv/bin/python`, never `uv run`.

## Pseudocode (extractor)
```python
def parse_sections(index_html) -> list[Section]   # id, nav label, heading, in-section hrefs;
                                                  # bijection + duplicate/missing diagnostics
def discover_explorers() -> dict[path, meta]      # docs/api/**/*-explorer.html MINUS capabilities/api/
def load_pdf_specs() -> dict[sec_anchor, meta]    # importlib real-path on build_onepagers SPECS
def load_recency() -> dict                        # capabilities-added.yml (explicit metadata)
def build_inventory(clusters, aliases) -> dict    # joins + gap/unlinked marking + schema_version
def check_mode() -> int                           # regenerate vs committed → nonzero on drift
```

## TDD Test List (write first, confirm red)
1. `test_section_census_bijection_live_page` — nav-href set == section-id set, 1:1; duplicates/missing → diagnostic failure (Codex F2).
2. `test_parser_failure_fixtures` — fixtures: section w/o id, duplicate id, nav-only entry, section-only entry → each fails closed with the actionable message (Codex F8).
3. `test_cluster_mapping_total_disjoint_and_schema` — clusters YAML schema-valid; totality/disjointness vs live census; unknown section → error (Codex F7/F10).
4. `test_explorer_discovery_excludes_frozen_dupes` — census across docs/api/** minus capabilities/api/ matches the live tree; structural-only glob would under-count (regression, r1 M1).
5. `test_joins_one_to_one_with_gaps_and_unlinked` — in-section href + `sec-<anchor>` + alias joins; ambiguous → fail; 12/22 PDF coverage with 10 explicit gap rows (r1 M3/m1, Codex F3).
6. `test_recency_from_metadata_only` — no git calls in the extractor (guard); `unknown` entries surface as such (r1 M2, Codex F1).
7. `test_check_mode_fails_on_drift` — mutate a committed artifact → `--check` nonzero; clean → zero (Codex F4).
8. `test_md_tables_match_inventory_json` — rendered spec tables == generated JSON (r1 m3).
9. `test_specs_importlib_load` — SPECS loads via real path, `sec-*` keys present (r1 m2).
10. DOMAINS.md row added and the suite discovered by dm's CI runner (verified in the PR's CI run — the AC, not a local test).

## Acceptance Criteria
- [ ] All 22 current sections clustered (7 clusters, machine SoT YAML), zero unassigned, CI-enforced via the new DOMAINS row
- [ ] Recency model = explicit metadata seeded from PR history (no git derivation); `unknown` handled honestly
- [ ] Reference index: one-to-one joins, 10 PDF gaps + any `unlinked` artifacts explicit; frozen `capabilities/api/` dupes excluded
- [ ] Anchor bijection enumerated + test-locked; freshness `--check` green in CI; regeneration command documented
- [ ] Spec-only boundary verified on the diff (no index.html/CSS/JS); **owner acceptance comment linked on dm#1444 before close**

## Risks
1. Revamp awakening → spec is its input; coordinate via #1389 thread; no shared files.
2. dm CI conventions → verify exact lint/test toolchain from `.github/workflows/` at implementation start (lint-toolchain rule); DOMAINS row is the routing lever (r1 M4).
3. `import digitalmodel` OrcaFlex hang → extractor never imports the package (stdlib + importlib-file only).
4. Taxonomy judgment → owner adjusts at spec review; machine SoT keeps edits schema-valid (Codex F10).
5. `gh` seeding needs network/auth once → documented as an implementation step; failure degrades to `unknown` recency, never fabricated dates.

## Adversarial Review Summary
- **r1 (Claude subagent, repo-verified @ dm 0cdf1104): MAJOR/8** — corrected explorer census, killed git-dating (19-commit truncated history), located the real joins (`sec-<anchor>` clean; in-section hrefs for explorers), exposed DOMAINS.md CI routing.
- **r2 (Codex): MAJOR/10** — in-file section dating defect, freshness gate, alias-map joins, bijection/fixture tests, registry-absence fallback, formal acceptance, machine-readable cluster map, spec-only AC.
- **r3 (this revision, inline per `feedback_r3_inline_loop_break_pattern`)** — finding→patch map embedded throughout (each rule/test cites its finding).
- Awaiting user approval; not self-labeled.
