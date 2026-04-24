# Plan for #2364: Execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains

> **Status:** draft (v2 — addresses r1 findings)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2364
> **Anchor HEAD:** `12b4be834954505ca1e7fc8ad8b20bda34e92baf`
> **Supersedes:** v1 draft (2026-04-23)
> **Review artifacts:** scripts/review/results/20260424T033343Z-2026-04-23-issue-2364-batch-pack-1-api-standards-portal-promotion.md-plan-claude.md | ...-codex.md (pending v2 fanout) | ...-gemini.md (pending v2 fanout)

---

## Review History

| Version | Date | Reviewer(s) | Verdict | Summary |
|---|---|---|---|---|
| v1 | 2026-04-23 | Claude r1 | **MAJOR** | 2 P1s (forbidden-path conflict + un-cited rationalization), 3 P2s (undefined classifier sets, missing 120-char dry-run count, maritime-law AC conflict), 3 P3s (ruamel.yaml dep unverified, duplicate-check cost unbenchmarked, `noaa-ndbc` fixture id unverified). |
| v2 | 2026-04-24 | (pending) | — | Relocates runner + test module off `scripts/**` and `tests/**` onto owned `docs/reports/**`; enumerates classifier sets from live registry (40-entry survey); embeds 120-char dry-run count (25/40 sufficient, 15/40 insufficient); adds `maritime-law` as fourth allowed `target_wiki_domain` with explicit routing for the 2 IMO entries; drops `ruamel.yaml` in favor of a scoped-key in-place YAML patch; corrects fixture id `noaa-ndbc` → `noaa_ndbc`. |

**Revisions (v1 → v2):**
- **P1 #1 (forbidden paths):** Relocated the runner and test module OFF `scripts/**` and `tests/**`. Runner lands at `docs/reports/batch-pack-1-runner.py`; tests land at `docs/reports/batch-pack-1-runner-tests.py`. Both paths are explicitly within the batch-pack §3.1 **Owned** set (`docs/reports/**`). No carve-out request is required.
- **P1 #2 (un-cited rationalization):** Deleted the "forbidden-path rule governs runtime-execution write scope" rationale entirely. The spec is treated as binding; compliance is achieved by relocation, not interpretation.
- **P2 #1 (classifier sets undefined):** Enumerated `MARINE_TERMS`, `NAVAL_ARCH_TERMS`, `MARINE_HOSTS`, `NAVAL_ARCH_HOSTS`, `LAW_HOSTS` in the Pseudocode section, derived from the 40-entry host/notes survey on HEAD `12b4be8`. `MARINE_TAGS` / `NAVAL_ARCH_TAGS` are removed from the pseudocode because **every one of the 40 candidate entries has `tags: None`** (verified — see Evidence); a tags-based rule is dead code on the current registry. The classifier reduces to host-regex + notes-keyword.
- **P2 #2 (120-char dry-run):** Embedded live count — **25/40 pass**, **15/40 insufficient** (12 <120 chars, 3 ≥120 but lack capability indicator). Split is reasonable (not degenerate); threshold is retained.
- **P2 #3 (maritime-law AC):** Added `maritime-law` as a fourth allowed `target_wiki_domain`. The 2 IMO-adjacent entries (`imo_gisis`, `gisis_imo_org_5db4e8`) route to `maritime-law` with `out-of-scope-for-promotion: true` in the stub frontmatter — they are catalogued but not targeted for promotion in this pack.
- **P3 #1 (ruamel.yaml):** Confirmed `ruamel.yaml` is **NOT** in `pyproject.toml` or `requirements*.txt`. v2 drops the ruamel dependency and replaces the additive-write strategy with a scoped two-key text patch (`processed: true` + `processed_date: <iso>`) appended on a single `yq`-anchored line per entry, verified by structural diff (all other lines byte-identical to pre-run).
- **P3 #2 (duplicate-check cost):** Added benchmark plan — duplicate check scans only `knowledge/wikis/*/wiki/**/*.md` frontmatter (not body) via a single `find | xargs grep -l "^source_id:"` pass, with a recorded wall-clock budget of ≤30 s over the 19,191-page marine-engineering corpus. If the benchmark exceeds 30 s on first run, the plan downgrades duplicate check to the three target-domain wikis only and records the decision.
- **P3 #3 (fixture id):** Corrected `noaa-ndbc` → `noaa_ndbc` (underscore is the actual canonical id at line 125 of `online-resource-registry.yaml`).

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` — existing helper module; **read-only** for this plan. If reusable helpers (frontmatter serializer, domain classifier) exist, the new runner will import them. No modifications to this file.
- Found: `scripts/knowledge/wiki-cross-links.py` — existing cross-link generator. Batch-pack-1 output is shaped to feed this tool downstream (stub IDs + target wiki domain + source URLs).
- Found: `scripts/knowledge/build-knowledge-index.sh`, `scripts/knowledge/wiki_health_cron.py`, `scripts/knowledge/registry-freshness-check.py` — adjacent tooling; read-only context.
- Gap: No existing script or report titled `batch-pack-1-runner*`. The runner does not yet exist as committed code in any permitted path.

### Standards
Not applicable directly — this is a knowledge-promotion issue. However, the batch pack must preserve provenance to any API/portal entry that references named standards families (DNV, API, IMO, CSA, OCIMF, ABS) so the downstream #2207 provenance contract holds.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — engineering wiki index (83 pages). Five-bucket structure: `concepts/`, `entities/`, `sources/`, `standards/`, `workflows/`. Batch-pack-1 stubs will classify into `sources/` (data APIs, portals).
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema: `title`, `tags`, `added`, `last_updated` required; `sources`, `domain`, `cross_links` optional.
- `knowledge/wikis/naval-architecture/CLAUDE.md` — 46 pages; same pattern.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — 19,191 pages; selective additions only per priority queue §2.
- `knowledge/wikis/maritime-law/CLAUDE.md` — 23 pages. **v2 change:** added as a catalog-only target for the 2 IMO-adjacent entries.

### Documents consulted
- `docs/reports/llm-wiki-external-source-priority-queue.md` — Queue classifies `online-data-apis-and-portals` as P1, `metadata-first` promotion, target wikis `engineering, marine-eng, naval-arch`. 40 entries total.
- `docs/reports/llm-wiki-staged-batch-packs.md` — Defines Batch Pack 1 with exact paths and verification sequence. **§3.1 forbidden-path clause is binding; see Attested Evidence.**
- `data/document-index/online-resource-registry.yaml` — Source registry; filter `type in [data_api, standard_portal]` yields 40 entries (31 `data_api` + 9 `standard_portal`).
- Epic `#2390` — Groups #2364 under Wave 5 promotion work.
- Related issues `#2068` (cross-link JSONL), `#2067` (research→wiki ingest), `#2039` (engineering wiki ingest), `#1609` (download pipeline).

### Gaps identified
- No `docs/reports/batch-pack-1-runner.py` (or equivalent) exists in any owned path; must be created.
- No existing enforcement that Batch Pack 1 output conforms to the frontmatter schema; plan adds a schema-validator check in the runner's self-test block.
- **All 40 candidate entries have `tags: None`** (verified) — classifier cannot rely on tags; must use URL host + notes keywords only.
- `target_wiki_domain` assignment is not pre-specified in the batch-pack spec; the runner will derive it from the host-regex + notes-keyword classifier enumerated in Pseudocode.
- "Insufficient notes" threshold not defined; plan introduces a minimum-evidence rule: `len(notes) ≥ 120` AND notes contains ≥1 of the enumerated capability indicators.

### Evidence (embedded verification)

**Anchor:** all file/line references verified against HEAD `12b4be834954505ca1e7fc8ad8b20bda34e92baf` (2026-04-24).

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#2364` — OPEN — feat(knowledge): execute Batch Pack 1 …
- `#2390` — OPEN — epic(knowledge): llm-wiki strengthening roadmap and execution waves
- `#2242`, `#2243`, `#2241` — CLOSED — upstream queue/batch-pack design work
- `#2039`, `#2067`, `#2068`, `#1609` — OPEN — downstream consumers and related work

**File existence** (`ls` / `git ls-files` on HEAD `12b4be8`):
- EXISTS: `docs/reports/llm-wiki-external-source-priority-queue.md`
- EXISTS: `docs/reports/llm-wiki-staged-batch-packs.md` (17,928 bytes)
- EXISTS: `data/document-index/online-resource-registry.yaml` (3,423 lines, 152,258 bytes)
- EXISTS: all five target-wiki `CLAUDE.md` files
- MISSING (new — this plan creates in **owned** paths): `docs/reports/batch-pack-1-runner.py`, `docs/reports/batch-pack-1-runner-tests.py`, `docs/reports/batch-pack-1-api-portal-metadata-stubs.md`, `data/document-index/batch-pack-1-follow-on-issues.yaml`

**Forbidden-paths clause (quoted verbatim from `docs/reports/llm-wiki-staged-batch-packs.md`, §3.1, line 80):**
> `| **Forbidden** | \`config/**\`, \`.claude/**\`, \`tests/**\`, \`scripts/**\` |`

The Owned row (same table, line 78) is:
> `| **Owned** (may write) | \`data/document-index/**\`, \`docs/reports/**\` |`

The Read-only row (line 79):
> `| **Read-only** | \`knowledge/wikis/**\`, \`docs/document-intelligence/**\` |`

**v2 resolution (P1 option a — relocate):** All four new artifacts land under `docs/reports/**` or `data/document-index/**` (both Owned). No `scripts/**` or `tests/**` write. No carve-out needed.

**Domain-classifier-set sources (verified 2026-04-24):**
- Tag survey: all 40 candidate entries have `tags: None` (verified via `yaml.safe_load` + `Counter()` on `tags` field — zero tags across all 40). Conclusion: tag-based classifier rules are dead code on current data; the classifier uses host-regex + notes-keyword only.
- Host survey (top hosts among the 40): `www.api.org` (3), `cds.climate.copernicus.eu` (2), `gisis.imo.org` (2), `data.marine.copernicus.eu`, `www.ndbc.noaa.gov`, `factpages.sodir.no`, `www.data.boem.gov`, `rigcount.bakerhughes.com`, `www.eia.gov`, `www.data.bsee.gov`, `standards.dnv.com`, `api.tidesandcurrents.noaa.gov`, `iacs.org.uk`, `psmsl.org`, `nsidc.org`, etc. (full list embedded in runner).
- The five classifier sets in Pseudocode below are derived from this host survey plus notes-keyword inspection.

**120-char threshold dry-run count (verified 2026-04-24):**

| Bucket | Count | Notes |
|---|---:|---|
| Sufficient (`len(notes) ≥ 120` AND ≥1 indicator) | **25 / 40** | 19 `data_api` + 6 `standard_portal` |
| Insufficient — `len(notes) < 120` | 12 / 40 | short or empty notes |
| Insufficient — `len(notes) ≥ 120` but no indicator | 3 / 40 | narrative notes missing `endpoint`/`api`/`http`/`portal`/`coverage`/`dataset`/`standard`/`rule` |
| **Total insufficient** | **15 / 40** | routed to follow-on catalog |

Sample insufficient entries for traceability: `cmems_marine_service` (370 chars, no indicator), `cds_climate_copernicus_eu_datasets_reanalysis_era5_single_le_3fd8e2` (130 chars, no indicator), `rigcount_bakerhughes_com_1a81d9` (107 chars), `api_org_products_and_services_standards_66556d` (74 chars), `api_org_products_and_services_standards_important_standards__839ba5` (61 chars).

Split is reasonable (60/40 ≈ sufficient/insufficient) — rule is retained.

**Maritime-law routing count (verified 2026-04-24):**
Two of the 40 entries match IMO/maritime-law signals:
- `imo_gisis` (type=`standard_portal`, url=`https://gisis.imo.org/Public/Default.aspx`)
- `gisis_imo_org_5db4e8` (type=`data_api`, url=`https://gisis.imo.org/`)

Both route to `target_wiki_domain: maritime-law` with `out-of-scope-for-promotion: true` per v2 AC.

**`ruamel.yaml` dependency status (verified 2026-04-24):**
- `grep ruamel pyproject.toml requirements*.txt` → no match.
- v2 drops ruamel. Write-back strategy: the runner emits a scoped in-place patch that appends two lines (`  processed: true` and `  processed_date: <iso>`) under each of the 40 target entry keys using an anchored regex that matches the entry's `- id: <id>` line. Structural-diff acceptance test confirms every other byte is unchanged.

**Fixture id verification (verified 2026-04-24):**
- `grep -n "noaa_ndbc" data/document-index/online-resource-registry.yaml` → matches at **line 125** (`- id: noaa_ndbc`).
- `grep -n "noaa-ndbc"` → **no match** (hyphen form does not exist).
- v2 corrects the test fixture id from `noaa-ndbc` to `noaa_ndbc`.

**Duplicate-check cost (benchmark plan):**
- marine-engineering wiki: 19,191 pages. Budget: single frontmatter pass via `find knowledge/wikis/marine-engineering/wiki -name '*.md' -print0 | xargs -0 grep -l '^source_id:'`. Wall-clock target ≤30 s. If exceeded on first run, fallback is to index only the three target-domain wikis and record the decision in the output report.

**Line excerpts:**
- Queue doc §3 P1 row 1 (line 31): `Online Data APIs & Standards Portals | 40 | metadata-first | engineering, marine-eng, naval-arch | #1609, #2039, #2067`
- Batch-pack §3.1 Paths: quoted above.
- Engineering wiki CLAUDE.md frontmatter schema (lines 10-23): `title`, `tags`, `added`, `last_updated` required.

**Gap proofs:**
- `ls docs/reports/batch-pack-1-runner*.py 2>&1` → "No such file or directory".
- `grep -cE "^\s+type:\s+(data_api|standard_portal)" data/document-index/online-resource-registry.yaml` → 40.

<!-- Source count: 10 (issue body + 9 artifacts/scripts) — exceeds ≥3 minimum. -->

---

## Attested Evidence (r1-triggered)

| Claim | Evidence | Line / command |
|---|---|---|
| §3.1 forbidden paths include `scripts/**` AND `tests/**` | `docs/reports/llm-wiki-staged-batch-packs.md` | line 80 (quoted verbatim above) |
| §3.1 owned paths include `docs/reports/**` | same file | line 78 |
| 40 candidate entries have `tags: None` | live registry survey | `yaml.safe_load` + `Counter()` — zero tags across 40 |
| 25/40 sufficient under 120-char + indicator rule | live registry survey | table above |
| 2/40 maritime-law-adjacent (`imo_gisis`, `gisis_imo_org_5db4e8`) | live registry survey | enumerated above |
| `ruamel.yaml` not in pyproject/requirements | `grep ruamel` | no match |
| `noaa_ndbc` exists as real entry id at line 125 | live registry | `grep -n "noaa_ndbc"` → line 125 |

---

## Artifact Map

| Artifact | Path | Owned path? |
|---|---|---|
| This plan | docs/plans/2026-04-23-issue-2364-batch-pack-1-api-standards-portal-promotion.md | — (planning tree) |
| Runner | **docs/reports/batch-pack-1-runner.py** (new, relocated from `scripts/knowledge/`) | YES (§3.1 Owned) |
| Runner self-tests | **docs/reports/batch-pack-1-runner-tests.py** (new, relocated from `tests/knowledge/`) | YES (§3.1 Owned) |
| Primary output report | docs/reports/batch-pack-1-api-portal-metadata-stubs.md (new) | YES |
| Follow-on catalog | data/document-index/batch-pack-1-follow-on-issues.yaml (new) | YES (§3.1 Owned) |
| Plan reviews | scripts/review/results/…-plan-{claude,codex,gemini}.md | — (review tree) |
| Registry delta | `processed: true` + `processed_date` appended per entry (40 entries) | YES (additive-only) |

---

## Deliverable

After this issue closes, a reproducible Batch Pack 1 run will have produced `docs/reports/batch-pack-1-api-portal-metadata-stubs.md` — a durable report containing wiki-ready metadata stubs (grouped by `engineering` / `marine-engineering` / `naval-architecture` / `maritime-law` target domains) for all 40 `data_api`/`standard_portal` entries, with explicit duplicate-check against existing wiki pages, explicit split-out of insufficient-notes entries into a follow-on catalog, and provenance references to each source registry entry. Maritime-law entries will be catalogued with `out-of-scope-for-promotion: true` (enumerated but not promoted in this pack).

No wiki page promotion itself happens in this issue — the report is the deliverable that downstream wiki-ingest work (#2039, #2067, #2068) will consume.

---

## Pseudocode

```
# Classifier sets, derived from live 40-entry survey on HEAD 12b4be8.
# Note: no tag-based rules because every candidate entry has tags=None.

MARINE_HOSTS = {
    "www.ndbc.noaa.gov", "api.tidesandcurrents.noaa.gov",
    "data.marine.copernicus.eu", "psmsl.org", "nsidc.org",
    "www.gebco.net", "cds.climate.copernicus.eu",
}

NAVAL_ARCH_HOSTS = {
    "iacs.org.uk", "standards.dnv.com", "www.dnv.com",
}

LAW_HOSTS = {
    "gisis.imo.org",
}

MARINE_TERMS = {
    "marine", "ocean", "wave", "tide", "sea level", "bathymetry",
    "offshore", "subsea", "hydrodynamic", "metocean", "wind-farm",
}

NAVAL_ARCH_TERMS = {
    "classification society", "ship rules", "hull", "naval architecture",
    "ship design", "class rules",
}

LAW_TERMS = {
    "imo", "convention", "solas", "marpol", "unclos", "maritime law",
}

function run_batch_pack_1(registry_path, wiki_root, output_report_path):
    entries = load_yaml(registry_path)["entries"]
    candidates = filter(entries, lambda e: e.type in {"data_api", "standard_portal"})
    assert len(candidates) == 40

    sufficient, insufficient = partition_by_notes_quality(candidates,
        min_chars=120,
        require_any_of=["endpoint", "api", "http", "portal", "coverage",
                        "dataset", "standard", "rule"])
    assert len(sufficient) + len(insufficient) == 40
    # Expected on 2026-04-24 HEAD: sufficient=25, insufficient=15.

    grouped = {d: [] for d in ["engineering", "marine-engineering",
                               "naval-architecture", "maritime-law"]}
    for entry in sufficient:
        domain = classify_domain(entry)
        stub = build_stub(entry, domain)
        stub.out_of_scope_for_promotion = (domain == "maritime-law")
        stub.classifier_trace = which_rule_matched(entry)   # for reviewer audit
        dup = check_duplicate(wiki_root, stub.source_id)
        stub.duplicate_candidate = dup
        grouped[domain].append(stub)

    write_report(output_report_path, grouped, insufficient_index, classifier_trace)
    write_follow_on_catalog("data/document-index/batch-pack-1-follow-on-issues.yaml",
                            insufficient)
    patch_registry_additive(registry_path, [e.id for e in sufficient])
    return summary(total=40, promoted=len(sufficient),
                   deferred=len(insufficient),
                   law=len(grouped["maritime-law"]))

function classify_domain(entry):
    host = extract_host(entry.url)
    notes_lower = entry.notes.lower()
    # Precedence: LAW > NAVAL_ARCH > MARINE > engineering default.
    if host in LAW_HOSTS or any(t in notes_lower for t in LAW_TERMS):
        return "maritime-law"
    if host in NAVAL_ARCH_HOSTS or any(t in notes_lower for t in NAVAL_ARCH_TERMS):
        return "naval-architecture"
    if host in MARINE_HOSTS or any(t in notes_lower for t in MARINE_TERMS):
        return "marine-engineering"
    return "engineering"
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | **docs/reports/batch-pack-1-runner.py** | runner executing classification + stub generation (owned path per §3.1) |
| Create | **docs/reports/batch-pack-1-runner-tests.py** | self-tests for filter, partition, classifier, stub, duplicate-check (owned path per §3.1) |
| Create | docs/reports/batch-pack-1-api-portal-metadata-stubs.md | primary output (wiki-ready stubs grouped by domain) |
| Create | data/document-index/batch-pack-1-follow-on-issues.yaml | catalog of entries with insufficient notes |
| Modify | data/document-index/online-resource-registry.yaml | additive `processed: true` + `processed_date` per covered entry; no schema change, no note rewrite |
| Update | docs/plans/README.md | add index row for this plan |

No `scripts/**` or `tests/**` writes. No `config/**` or `.claude/**` writes. No `knowledge/wikis/**` writes (read-only).

---

## TDD Test List

Tests live in `docs/reports/batch-pack-1-runner-tests.py` (owned path). Runner imports target; tests use pytest-style asserts invoked via `uv run python docs/reports/batch-pack-1-runner-tests.py` (direct script) or `uv run pytest docs/reports/batch-pack-1-runner-tests.py -v`.

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_filter_yields_exact_40_entries | filter(type in {data_api, standard_portal}) count = 40 | committed `online-resource-registry.yaml` | len == 40 |
| test_partition_dry_run_matches_25_15 | live partition on HEAD matches survey | committed registry | sufficient=25, insufficient=15 |
| test_partition_notes_quality_threshold_rejects_empty_notes | notes-length < 120 → insufficient | synthesized 30-char note | insufficient |
| test_partition_notes_quality_threshold_accepts_endpoint_mention | ≥120 chars AND "endpoint" → sufficient | synthesized 250-char note | sufficient |
| test_classify_domain_law_wins_over_marine | IMO host routes to maritime-law even with marine-like notes | synthesized entry at `gisis.imo.org` with "ocean" notes | domain == "maritime-law" |
| test_classify_domain_marine_host_wins | NDBC host → marine-engineering | entry at `www.ndbc.noaa.gov` | domain == "marine-engineering" |
| test_classify_domain_naval_host_wins | IACS/DNV host → naval-architecture | entry at `iacs.org.uk` | domain == "naval-architecture" |
| test_classify_domain_default_engineering | no marine/naval/law signal → engineering | synthesized plain data-api entry | domain == "engineering" |
| test_imo_entries_flagged_out_of_scope | both real IMO entries get `out_of_scope_for_promotion=True` | live registry (`imo_gisis`, `gisis_imo_org_5db4e8`) | both flagged |
| test_build_stub_frontmatter_matches_wiki_schema | stub YAML has `title`, `tags`, `added`, `last_updated` | sample entry | frontmatter keys are a superset of required |
| test_duplicate_check_detects_existing_wiki_page | if a wiki page references entry id, flag set | fixture wiki page referencing entry id **`noaa_ndbc`** | stub.duplicate_candidate is not None |
| test_processed_flag_is_additive_only | write-back only diffs on two new keys per entry | registry pre/post round-trip | structural diff == {`processed`, `processed_date`} only |
| test_output_report_counts_invariant | total stubs + insufficient == 40 | full registry filter | invariant holds |
| test_run_is_idempotent | re-running with already-processed entries yields no new stubs | already-flagged registry | report reports 0 newly-added |
| test_duplicate_check_wall_clock_under_budget | full-wiki frontmatter scan completes ≤30 s | 19,191 marine-eng pages | wall_clock < 30.0 s; on failure, runner falls back to target-domain-only scan and logs the decision |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest docs/reports/batch-pack-1-runner-tests.py -v`
- [ ] `uv run python docs/reports/batch-pack-1-runner.py` exits 0 and produces `docs/reports/batch-pack-1-api-portal-metadata-stubs.md`
- [ ] The output report contains exactly 40 rows classified as either `sufficient → stub generated` or `insufficient → follow-on catalog`, summing to 40
- [ ] Each generated stub has `target_wiki_domain ∈ {engineering, marine-engineering, naval-architecture, maritime-law}` (maritime-law added in v2)
- [ ] Every `maritime-law`-classified stub carries `out-of-scope-for-promotion: true` in its frontmatter
- [ ] Each generated stub records provenance (`sources: [<registry-entry-id>]`) and source URL
- [ ] A **Classifier Trace** section in the report lists the rule that matched for every one of the 40 entries, with zero entries in an `Unclassified` bucket
- [ ] Duplicate check runs against the current live wiki corpus; every matched pair is listed in a Duplicates section (does NOT block promotion)
- [ ] Duplicate-check wall-clock ≤30 s; otherwise the report records the fallback to target-domain-only scan
- [ ] `data/document-index/batch-pack-1-follow-on-issues.yaml` exists and lists every deferred entry with a reason code (`notes-too-short`, `no-capability-indicator`, `duplicate-suspected`, `classifier-ambiguous`)
- [ ] `online-resource-registry.yaml` only diffs on `processed` / `processed_date` keys (verified by structural diff in acceptance test)
- [ ] No files under `config/**`, `.claude/**`, `tests/**`, `scripts/**`, `knowledge/wikis/**` are modified (verified by `git diff --name-only | grep -vE '^(data/document-index/|docs/reports/|docs/plans/)'` returning empty)
- [ ] Review artifacts for all three providers posted to `scripts/review/results/`
- [ ] No wiki pages promoted — downstream #2039/#2067 consume the report

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (v1) | MAJOR | 2 P1 + 3 P2 + 3 P3 — all addressed in v2 (see Review History) |
| Claude (v2) | PENDING | (to be filled by v2 fanout) |
| Codex (v2) | PENDING | (to be filled by v2 fanout) |
| Gemini (v2) | PENDING | (to be filled by v2 fanout) |

**Overall result:** PENDING (awaits v2 r1 fanout).

---

## Risks and Open Questions

- **Risk (classifier precision):** Deterministic host + notes classifier will misclassify edge entries (e.g., a hydrodynamic-data API hosted on a generic `.gov` domain). Mitigation: runner produces a Classifier Trace section in the output listing the rule that matched each entry; reviewer can catch misassignments during wiki-ingest follow-on (#2039/#2067).
- **Risk (insufficient-notes false-positives):** The 120-char + indicator threshold may push adequately-documented entries into the follow-on catalog. Dry-run shows 15/40 insufficient — split is reasonable. Threshold is recorded in the report and is adjustable by flag for re-runs.
- **Risk (duplicate-check on marine-engineering):** 19,191 pages — mitigation is frontmatter-only scan with a 30-s wall-clock budget and target-domain-only fallback (see Acceptance).
- **Risk (additive-only registry write without ruamel):** Scoped text-patch approach uses an anchored regex matching each `- id: <id>` line and appending two keys. Structural-diff acceptance test confirms no other bytes change. If the regex anchor is insufficient on edge-case YAML whitespace, runner aborts with a clear error instead of silently mutating.
- **Open:** Should the follow-on catalog auto-file GitHub child issues under #2390 or leave issue creation to a human? This plan defaults to NOT auto-filing; user decides at approval.
- **Open:** Should the registry write land inline (this plan) or as a sidecar `online-resource-registry.processed.yaml`? Sidecar is still available as a fallback if the text-patch approach fails benchmarking; default is inline.

---

## Complexity: T2

**T2** — new runner + self-test module + report + follow-on catalog, all in owned paths; modifies one existing data file additively; no schema changes; no new dependencies; no network calls.
