# Plan for worldenergydata#947: Global-spine wave 1 — global roster federation into the Explorer feed + honest GoM play handling

> **Status:** adversarial-reviewed (r1 Fable subagent MAJOR/5 + MINOR/4, repo-AND-data-verified @ wed 7522747 → r2 this revision, all findings folded; dedup numbers now MEASURED, not estimated)
> **Complexity:** T2 — one new generated feed + funnel extension; no new ingest; stdlib-only build code.
> **Date:** 2026-07-11 (r2 same day)
> **Issue:** https://github.com/vamseeachanta/worldenergydata/issues/947 (parent epic #941, program #939)
> **Client:** N/A
> **Project:** (none)
> **Lane:** lane:claude
> **Review artifacts:** r1 findings summarized in the #947 evidence comment (subagent independently re-derived all counts and RAN the dedup match); local-only by convention.

---

## Resource Intelligence Summary

### Sources consulted (grounded on a LOCAL shallow clone of origin/main @ `7522747`; r1 re-verified every count)
- **Issue #947 + epic #941 + program #939**; #946 tracer SHIPPED (PR #953, live) — the shell + lazy-sidecar pattern this wave extends.
- **`data/modules/offshore_assets/curated/fields.csv`** — THE global catalog: **2,149 fields / 84 countries** (`FIELD_ID, FIELD_NAME, COUNTRY, BLOCK, RESERVE_TYPE, CURRENT_STATUS, DISCOVERY_DATE, PRODUCTION_START, WATER_DEPTH_M/FT, US_GOM_FLAG`). **No play, no operator.** US rows = 333, ALL GoM-flagged, none elsewhere. Spelled `US` (roster uses `USA`). Country spellings match coverage_summary exactly (r1-verified set equality).
- **`coverage_summary.csv`** — `by_country` 84 rows; `by_region` = exactly {GoM-flagged: 333, Rest of world: 1,816}. **No sub-country region tier exists globally.**
- **"205 countries"** = centroid geographic scope on the all-regions page (which already discloses "84 distinct" at its line 133) — NOT fields coverage. That page is out of scope; the funnel's new copy states 84.
- **Badge rule = `badge_for()` in `scripts/field_development/build_all_regions_atlas.py:108-118`, THREE branches (r1 f2):** (1) **US hardcoded RICH** (despite bsee `catalog_status: "sample"` — verified in scorecard + committed coverage CSV); (2) the 6 `COUNTRY_MODULE` countries → `CATALOG_TO_BADGE` on their module's catalog_status; (3) **no-module countries default SAMPLE** with module label `"offshore_assets (reference)"` (Angola/Nigeria verified SAMPLE in the committed CSV). Import of that module is side-effect-safe (sys.path insert + site_nav import only; generation is `__main__`-guarded).
- **Play attribution: NO in-repo source.** BSEE module has no field play/chronozone table; SubseaIQ none; the roster's 17 attributed entries (12 LT/Wilcox-family incl. North Platte Perdido Paleogene + 5 Miocene-family) are hand-curated. Wave 1 cannot source-attribute the 103 nulls.
- **Dedup ground truth (r1 COMPUTED, casefold + strip-parentheticals/punctuation):** 117/120 roster names match, suppressing 118 catalog rows; **215 unmatched** (118+215=333 ✓). Roster ⊄ catalog: **Anchor has no catalog GoM row.** Combined roster entries `Jack/St. Malo`, `Cascade/Chinook` vs separate catalog rows `Jack`,`St. Malo`,`Cascade`,`Chinook` → 4 intended duplicate roadmap cards (visible, acceptable). **False-merge hazard found: catalog holds DISTINCT `Big Bend (Noble)` and `Big Bend (Petrobras)`; naive paren-stripping suppresses BOTH from roster's `Big Bend (Noble)`** → exact-match-first rule required (D3). `Amberjack`/`Crackerjack` do NOT false-match.
- **`reports/field-atlas/_roster.json`** — hand-curated committed source (no writer script); 120 entries; funnel embeds it and computes `lifecycle_id` at build.
- **#946 shipped mechanics** — funnel JS: selects filled from `uniq()` over ROSTER; filter `(!c||f.country===c)&&(!d||f.domain===d)&&(!r||f.region===r)&&(!p||f.play===p)`; play select `.filter(Boolean)` drops nulls; cards get `data-fid` only with lifecycle_id (rich-only click guard — global rows degrade safely, r1-verified); `test_atlas_shell_pins` pins embed-count == on-disk roster count (safe: embed stays 120); the `public` test fixture builds the whole site in-process so a published feed is testable; BFS crawls `.html` only → fetch()-ed JSON needs no link-graph coverage beyond the contract test.
- CI: unchanged from #946 (lint trio versions/flags; feat-type PR title ≤80 chars; Pages deploy bare python3.11 stdlib).
- Drive-file search: not applicable — in-repo data federation.

### Gaps identified
No global feed; no country normalization (`US`→`USA`); dedup needs an exact-first rule (Big Bend hazard); no play source for the 103 nulls; badge rule buried in one generator; funnel JS has no mechanics for non-roster rows (domain key, select repopulation, null-play filtering).

### Parallel-work check
No open lane touches `scripts/field_atlas/` or curated offshore_assets. Re-verify open PRs at implementation start; fresh local clone off origin/main (never the FUSE checkout).

## Goal

One roster feed powers the Explorer funnel **beyond GoM**: all 84 catalogued countries selectable with honest badges; picking a non-US country renders its fields (name/block/status/type/depth) as catalog cards; the GoM catalog tail (215 fields) becomes browsable beside the 120 concept-matched entries; GoM `play` nulls become **explicitly unattributed** (visible, filterable, reasoned) and the missing official source is filed as a data child.

## Non-goals (wave discipline)

- NO new regulator ingest (Norway #715/#716, UK, Brazil ladders are separate #941 children).
- NO canonical-id minting for global fields (registry-expansion child owns `fields.yml` growth; feed rows carry `catalog_id`).
- NO play web-research backfill (cite-or-null: no ingested source → null; the BSEE play-definitions ingest is a filed child).
- NO all-regions-atlas page changes (its own 205-vs-84 copy is its own issue; page untouched, pinned).

## Artifact Map

| Artifact | Kind | Path |
|---|---|---|
| Shared badge rule | new stdlib module | `scripts/catalog_badges.py` — **`badge_for()` lifted VERBATIM incl. US-RICH override + no-module→SAMPLE default** (r1 f2); `build_all_regions_atlas.py` re-pointed to import it |
| Feed generator | new | `scripts/field_atlas/build_atlas_feed.py` → `reports/field-atlas/_atlas_feed.json` (committed) |
| Funnel extension | edit | `reports/field-atlas/atlas_template.html` + `scripts/field_atlas/build_field_atlas.py` (embed `__COUNTRIES_JSON__`; lazy feed fetch; filter mechanics per D5) |
| Publish | edit | `scripts/build_pages.py::build_field_atlas` (copy `_atlas_feed.json`) |
| Allowlist | edit | `config/repo_structure.yml`: `reports/field-atlas/_atlas_feed.json` ONLY (`scripts/` is a wholesale-allowed root — r1 f8) |
| Tests | new + edit | feed contract + badge parity (all three branches), dedup invariants, funnel pins extension, coverage-CSV identity for the badge lift |
| Data child | new issue | `cat:data`: BSEE GoM field play/chronozone dataset (verified URL at filing, wed #855 pilot rule) |

## Design decisions (r2 — r1 findings folded inline)

**D1 — Two-tier feed: embedded country index + one lazily fetched global feed.**
`__ROSTER_JSON__` (120 GoM rows) stays embedded; `__COUNTRIES_JSON__` (84 rows: `{country, fields, facilities, badge, module}`) is embedded to populate the Country select and per-country header line; `_atlas_feed.json` (~490 KB, r1-measured) is fetched once and cached **on the first Country-select interaction of any kind** — selecting a non-USA country, re-selecting USA, or "All countries" (r1 f1 fix: the GoM catalog tail must be reachable). The zero-regression pin is therefore: **the initial paint (no interaction) is byte-for-byte today's page**; after any country interaction the feed augments the grid.

**D2 — Feed shape (from catalog + scorecard + roster).**
```json
{
  "meta": {"generated_by": "scripts/field_atlas/build_atlas_feed.py", "issue": 947,
            "source": "data/modules/offshore_assets/curated/fields.csv"},
  "countries": [{"country": "Norway", "fields": 302, "facilities": n, "badge": "ROADMAP", "module": "sodir"}],
  "fields": [{"catalog_id": "720", "name": "Aasta Hansteen (Luva)", "country": "Norway",
               "domain": "offshore", "region": "Norway", "block": "PL 218 …",
               "status": "Under Development", "reserve_type": "Gas",
               "water_depth_ft": 4290, "density_tier": "roadmap", "gom": false}]
}
```
- `domain: "offshore"` is materialized on every feed row (the catalog IS the offshore-assets inventory) — without it the existing filter `f.domain===d` zero-results every global row (r1 f5).
- **`density_tier` is `"roadmap"` for EVERY catalog-only row** (r1 f3): the page defines tiers per field ("roadmap = name/block only") and catalog rows carry exactly name/block/status — presenting the country-level catalog badge as a per-field tier would claim concept data that doesn't exist and visually invert Norway-vs-reference-country honesty. The country badge is a SEPARATE dimension: shown as a glyph in the Country select and on a country header line above the grid, never as the field-card pill.
- Country names normalized `US`→`USA`. No hrefs in feed rows → no dead links possible.

**D3 — GoM dedup: exact-name-first, ambiguity-guarded fallback (r1 f4, measured).**
Pass 1: exact normalized-name equality (casefold, whitespace/punctuation squeeze, parentheticals KEPT). Pass 2 (only for roster names still unmatched): parenthetical-stripped comparison, applied ONLY when the stripped key maps to exactly one catalog row (ambiguous keys skip — this protects `Big Bend (Petrobras)` from being suppressed by roster's `Big Bend (Noble)`). Measured outcome (r1): ~117 roster keys suppress ~118 catalog rows, ~215 unmatched → included as `roadmap` GoM rows. Known intended artifacts, stated in the PR body: `Anchor` has no catalog row (nothing to suppress); split rows for `Jack`,`St. Malo`,`Cascade`,`Chinook` render as roadmap duplicates beside their combined rich cards (visible, honest, cheap). Generator prints a dedup report incl. **suppressed-rows-per-key**; tests pin `suppressed + unmatched == 333` and **zero ambiguous-key suppressions**.

**D4 — Play honesty for the 103 GoM nulls (re-scoped from the issue's "backfill" wording).**
No ingested source exists (grounding + r1 concur). Wave 1 delivers: (a) a **"(unattributed)"** option appended explicitly to the Play select (not via `uniq()`, which drops nulls), with filter special-case `p==="(unattributed)" ? !f.play : f.play===p` — roster data untouched, no sentinel materialized (r1 f5); (b) the note explains why ("play attribution pending the BSEE play-definitions ingest — issue #<child>"); (c) a `cat:data` child filed with a verified URL (T7). This satisfies the issue's "attributed or explicitly `unknown` with reason" clause; attribution itself lands with the ingest child.

**D5 — Funnel mechanics, pinned (r1 f5):**
- Country select: options = union of ROSTER countries and `__COUNTRIES_JSON__` countries (84), each suffixed with its badge glyph; default remains USA.
- On first country interaction: fetch+cache feed; working set becomes `ROSTER ∪ feed.fields` (feed GoM rows already deduped at build).
- Domain select: unchanged options; feed rows all carry `domain:"offshore"` so the existing filter works.
- Region select: repopulated from the working set (`region` == country for feed rows); for a non-US country it therefore shows that country as its only region — plus a title tooltip "regional tiers land with the #941 ingest ladder".
- Play select: repopulated from working set + the explicit "(unattributed)" option; filter per D4(a).
- Count line + note: reflect active scope; new copy states "84 countries catalogued · 2,149 fields (GoM: 120 concept-matched + 215 further catalogued of BSEE's full 1,390)" — reconciling the existing 1,390 sentence with the catalog's 333 (r1 f7).
- Cards for feed rows: name, block, `status · reserve_type`, water depth, `roadmap` pill; no `data-fid` → the #946 rich-only click guard already keeps them inert (r1-verified).

**D6 — Gates.**
(a) Feed contract: published whenever the atlas is; parses; `countries` length == coverage `by_country` rows; every `fields[].country` ∈ countries; every row has `domain`; tier values all `"roadmap"`.
(b) **Badge parity encoding ALL THREE branches** (US→RICH override; 6 module countries via CATALOG_TO_BADGE; no-module→SAMPLE) recomputed from the scorecard against `countries[].badge` (r1 f2).
(c) Dedup invariants: `suppressed + unmatched == 333`; zero ambiguous-key suppressions; no normalized name in both the embedded roster and feed GoM rows (pass-1 sense).
(d) Badge-lift identity via **`all_regions_coverage.csv`** (date-free; committed HTML has a `date.today()` line so byte-diff of HTML is meaningless — r1 f6): regenerate the CSV with the lifted module and diff; the committed all-regions HTML is untouched.
(e) Funnel pins: existing `test_atlas_shell_pins` unchanged (embed stays 120); new pins for `__COUNTRIES_JSON__` embed, "(unattributed)" option, and the initial-paint zero-regression.

**D7 — Stdlib + deploy parity.** Feed generator and `catalog_badges.py` are stdlib-only (csv/json/pathlib).

## Implementation steps

| # | Step | Files |
|---|---|---|
| T1 | Lift `badge_for()` + `COUNTRY_MODULE` + `CATALOG_TO_BADGE` verbatim to `scripts/catalog_badges.py`; re-point `build_all_regions_atlas.py`; identity check via regenerated `all_regions_coverage.csv` diff (D6d) | 2 scripts |
| T2 | `build_atlas_feed.py` (D2/D3) + dedup report; commit `_atlas_feed.json` | new script + artifact |
| T3 | Publish feed in `build_pages.build_field_atlas`; allowlist `_atlas_feed.json` | build_pages.py, repo_structure.yml |
| T4 | Funnel mechanics per D5 (template + generator embed) | atlas_template.html, build_field_atlas.py |
| T5 | Regenerate artifacts (venv-min recipe from #946; NEVER the FUSE venv; `python3 - <<EOF` heredocs) | generated |
| T6 | Tests per D6; suite `tests/test_build_pages.py tests/integration/site/ tests/unit/site/ -o addopts="" --noconftest` | test files |
| T7 | File the `cat:data` BSEE play-definitions child (verified URL); lint mirror (black 25.9.0 / isort 8.0.1 / flake8 7.3.0 + flags); PR `feat(explorer): …` ≤80-char subject; auto-merge; post-deploy live verify (feed 200; Norway renders with roadmap cards + country badge; initial USA paint unchanged; "(unattributed)" filter returns 103) | — |

## Acceptance mapping (issue #947 → plan)

| Issue criterion | Delivered by |
|---|---|
| One roster feed, tiers beyond GoM, honest badges, never faked rich | D1/D2/D5 (per-field tier = roadmap for catalog rows; country badge separate; badge rule verbatim incl. US override) |
| GoM play nulls attributed **or explicitly unknown with reason** | D4 (explicit bucket + reason + filed ingest child) — attribution re-scoped to the data child; grounding + r1 prove no in-repo source |
| Registry loader + contract tests green; play tier usable beyond LT | registry untouched; play select partitions attributed / "(unattributed)" |
| No regression on all-regions atlas | page untouched; D6(d) CSV identity for the badge lift |

## Risks & mitigations

- **R1 feed staleness vs catalog** → deterministic from committed inputs; contract test recomputes counts.
- **R2 dedup errors** → exact-first + ambiguity guard (Big Bend case pinned by test); duplicates-by-design listed in the PR body; false-miss cost = visible duplicate roadmap card.
- **R3 GoM default regression** → initial paint pinned byte-equivalent; feed touches the grid only after a country interaction.
- **R4 badge-lift breaks all-regions atlas** → import-only refactor + CSV identity (D6d).
- **R5 badge wrongness** → parity test encodes all three `badge_for` branches (r1 f2 killed the two-branch assumption).
- **R6 feed size growth in later waves** → 490 KB now; per-region sharding decision explicitly deferred to the ingest-ladder children.

## Ops notes for the implementer

Same as #946: local shallow clone (FUSE git hangs), minimal venv (pyyaml+pydantic-settings+pytest), heredoc python (sandbox denies `python3 -c "…"`), tests with `-o addopts="" --noconftest`, agent verifies / human merges.
