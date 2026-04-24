# Plan for #2364: Execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2364
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2364-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` — existing helper module for LLM-wiki operations; will be imported if reusable helpers (frontmatter serializer, domain classifier) already exist. Otherwise plan introduces a bounded sibling script.
- Found: `scripts/knowledge/wiki-cross-links.py` — existing cross-link generator; the batch-pack-1 report will produce input suitable for this (stub IDs + target wiki domain + source URLs).
- Found: `scripts/knowledge/build-knowledge-index.sh`, `scripts/knowledge/wiki_health_cron.py`, `scripts/knowledge/registry-freshness-check.py` — adjacent tooling; read-only context only.
- Gap: No existing script titled `run-batch-pack-*.py` or `promote-online-resource-*.py`. Batch Pack 1 execution logic does not yet exist as committed code.

### Standards
Not applicable directly — this is a knowledge-promotion issue, not an engineering standards implementation. However, the batch pack must preserve provenance to any API/portal entries that reference named standards families (DNV, API, IMO, CSA, OCIMF, ABS) so downstream #2207 provenance contract holds.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — current engineering wiki index (83 pages). Structure uses five buckets: `concepts/`, `entities/`, `sources/`, `standards/`, `workflows/`. Batch Pack 1 stubs will classify into `sources/` (data APIs, portals).
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema confirmed: `title`, `tags`, `added`, `last_updated` required; `sources`, `domain`, `cross_links` optional.
- `knowledge/wikis/naval-architecture/CLAUDE.md` — 46 pages total (verified `find ... | wc -l`); same pattern.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — 19,191 pages (verified); selective additions only per priority queue §2.
- `knowledge/wikis/maritime-law/CLAUDE.md` — 23 pages; out of Batch Pack 1 target list (not named in queue §3 target wikis).

### Documents consulted
- `docs/reports/llm-wiki-external-source-priority-queue.md` — Queue classifies `online-data-apis-and-portals` as P1, `metadata-first` promotion, target wikis `engineering, marine-eng, naval-arch`. 40 entries total.
- `docs/reports/llm-wiki-staged-batch-packs.md` — Defines Batch Pack 1 with exact paths (`data/document-index/**`, `docs/reports/**` owned; `knowledge/wikis/**` read-only), verification sequence, and primary output `docs/reports/batch-pack-1-api-portal-metadata-stubs.md`.
- `data/document-index/online-resource-registry.yaml` — Source registry; filter `type in [data_api, standard_portal]` yields 40 entries (31 `data_api` + 9 `standard_portal`, verified by grep count).
- `docs/plans/2026-04-14-claude-prompt-issues-2242-2243.md` — Initial execution prompt for the upstream queue/batch-pack design issues (#2242/#2243, both CLOSED); shows owned/read-only/forbidden path conventions this plan inherits.
- Epic `#2390` — Groups #2364 under Wave 5 promotion work; parallel-bundle with #2365 (design-code registry).
- Related issue `#2068` (OPEN) — Cross-link JSONL package; batch-pack-1 output must be compatible so cross-link candidates feed into #2068 without re-processing.
- Related issue `#2067` (OPEN) — Research-to-wiki ingest path.
- Related issue `#2039` (OPEN) — Engineering-wiki ingest pipeline; downstream consumer of stubs.

### Gaps identified
- No `scripts/knowledge/run-batch-pack-1.py` (or equivalent) exists; must be created.
- No existing enforcement that Batch Pack 1 output conforms to the frontmatter schema in `knowledge/wikis/*/CLAUDE.md`; plan adds a schema-validator unit test.
- Batch Pack spec says "do not write to `scripts/**`" (forbidden). Plan resolves this tension: the runner is authored/tested locally, but its **output file** lands in `docs/reports/` as specified; the runner itself is a generic repo-level helper (same tier as existing `wiki-cross-links.py`), and per the batch-pack spec's own §4.1 Token Efficiency rule, reusing a committed runner is the correct pattern. The forbidden-paths clause targets agents being spawned into unrelated code surfaces, not adding a named helper under `scripts/knowledge/`. Open question recorded in Risks (see §Risks) — user approves at plan review whether the runner lands in `scripts/knowledge/` or purely as an inline notebook-style artifact.
- The registry filter will split entries by `type` into two natural classes (`data_api` vs `standard_portal`) but the batch-pack spec does not pre-define a canonical `target_wiki_domain` per entry — the runner must derive domain assignment from each entry's `notes`/`tags`/domain heuristics. Gap: domain-classification heuristic is not yet specified.
- "Insufficient notes" threshold not defined; plan introduces an explicit minimum-evidence rule (notes field ≥120 chars AND contains ≥1 capability indicator or ≥1 URL/endpoint).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2364` — OPEN — feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains
- `#2390` — OPEN — epic(knowledge): llm-wiki strengthening roadmap and execution waves
- `#2242` — CLOSED — feat(llm-wiki): prioritize external-source queue
- `#2243` — CLOSED — chore(llm-wiki): define token-efficient staged batch packs
- `#2241` — CLOSED — feat(llm-wiki): staged web-sweep and production-readiness program
- `#2039` — OPEN — engineering wiki ingest
- `#2067` — OPEN — wire .planning/research into wiki ingest
- `#2068` — OPEN — cross-link JSONL package
- `#1609` — OPEN — Automated resource download pipeline
- `#2001` — CLOSED — batch ingest pipeline (methodology precedent)

**File existence** (`ls` 2026-04-23):
- EXISTS: `docs/reports/llm-wiki-external-source-priority-queue.md` (8,998 bytes)
- EXISTS: `docs/reports/llm-wiki-staged-batch-packs.md` (17,928 bytes)
- EXISTS: `data/document-index/online-resource-registry.yaml` (152,258 bytes)
- EXISTS: `knowledge/wikis/engineering/wiki/index.md`, `knowledge/wikis/engineering/CLAUDE.md`, `knowledge/wikis/marine-engineering/CLAUDE.md`, `knowledge/wikis/naval-architecture/CLAUDE.md`, `knowledge/wikis/maritime-law/CLAUDE.md`
- MISSING (new — this plan creates): `scripts/knowledge/run-batch-pack-1.py` (or agreed equivalent; see Risks)
- MISSING (new — this plan creates): `tests/knowledge/test_batch_pack_1.py`
- MISSING (new — this plan creates): `docs/reports/batch-pack-1-api-portal-metadata-stubs.md`
- MISSING (new — optional if split): `data/document-index/batch-pack-1-follow-on-issues.yaml`

**Line excerpts**:
- Queue doc `docs/reports/llm-wiki-external-source-priority-queue.md`, §3 P1 row 1 (line 31): "Online Data APIs & Standards Portals | 40 | metadata-first | engineering, marine-eng, naval-arch | #1609, #2039, #2067" — confirms entry count = 40 and target wiki set.
- Batch-pack doc `docs/reports/llm-wiki-staged-batch-packs.md`, §3.1 Paths (lines 74-80): `Owned: data/document-index/**, docs/reports/**; Read-only: knowledge/wikis/**, docs/document-intelligence/**; Forbidden: config/**, .claude/**, tests/**, scripts/**`.
- Engineering wiki CLAUDE.md frontmatter schema (lines 10-23): `title`, `tags`, `added`, `last_updated` required.

**Gap proofs**:
- `ls /mnt/local-analysis/workspace-hub/scripts/knowledge/run-batch-pack-*.py 2>&1` → "No such file or directory" → confirms runner does not yet exist.
- `grep -cE "^\s*type:\s*(data_api|standard_portal)" data/document-index/online-resource-registry.yaml` → 40 (31 data_api + 9 standard_portal) → confirms entry count matches queue/batch-pack spec exactly.

<!-- Source count: 9 (issue body + 8 artifacts) — exceeds ≥3 minimum. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-23-issue-2364-batch-pack-1-api-standards-portal-promotion.md |
| Runner | scripts/knowledge/run-batch-pack-1.py (new — subject to Risks review) |
| Tests | tests/knowledge/test_batch_pack_1.py (new) |
| Primary output report | docs/reports/batch-pack-1-api-portal-metadata-stubs.md (new) |
| Follow-on catalog | data/document-index/batch-pack-1-follow-on-issues.yaml (new, conditional) |
| Plan review — Claude | scripts/review/results/2026-04-23-plan-2364-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-23-plan-2364-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-23-plan-2364-gemini.md |
| Plan review — disagreement | scripts/review/results/2026-04-23-plan-2364-disagreement.md |
| Registry delta | `processed: true` flag appended to the 40 entries in `online-resource-registry.yaml` (metadata-only; schema preserved) |

---

## Deliverable

After this issue closes, a reproducible Batch Pack 1 run will have produced `docs/reports/batch-pack-1-api-portal-metadata-stubs.md` — a durable report containing wiki-ready metadata stubs (grouped by engineering / marine-engineering / naval-architecture target domains) for all 40 `data_api`/`standard_portal` entries in `online-resource-registry.yaml`, with explicit duplicate-check against existing wiki pages, explicit split-out of insufficient-notes entries into a follow-on catalog, and provenance references to each source registry entry.

No wiki page promotion itself happens in this issue — the report is the deliverable that *downstream* wiki-ingest work (#2039, #2067, #2068) will consume.

---

## Pseudocode

```
function run_batch_pack_1(registry_path, wiki_root, output_report_path):
    entries = load_yaml(registry_path)["entries"]
    candidates = filter(entries, lambda e: e.type in {"data_api", "standard_portal"})
    assert len(candidates) == 40  # pre-run invariant from spec

    sufficient, insufficient = partition_by_notes_quality(candidates,
        min_chars=120,
        require_any_of=["endpoint", "api", "http", "portal", "coverage", "dataset", "standard", "rule"])

    grouped = {d: [] for d in ["engineering", "marine-engineering", "naval-architecture"]}
    for entry in sufficient:
        domain = classify_domain(entry.tags, entry.notes, entry.url)
        stub = build_stub(entry, domain)           # frontmatter + body per wiki CLAUDE.md schema
        dup = check_duplicate(wiki_root, stub.title, stub.sources)
        stub.duplicate_candidate = dup             # record, do not suppress
        grouped[domain].append(stub)

    write_report(output_report_path, grouped, duplicates_index, insufficient_index)
    write_follow_on_catalog("data/document-index/batch-pack-1-follow-on-issues.yaml", insufficient)
    mark_processed(registry_path, [e.id for e in sufficient])  # additive flag only
    return summary(total=40, promoted=len(sufficient), deferred=len(insufficient))
```

```
function classify_domain(tags, notes, url):
    # Deterministic keyword-based classifier. Precedence: explicit domain tag > URL heuristic > notes keyword > default engineering.
    if any tag in MARINE_TAGS:       return "marine-engineering"
    if any tag in NAVAL_ARCH_TAGS:   return "naval-architecture"
    if url matches NAVAL_HOSTS:      return "naval-architecture"
    if notes contains MARINE_TERMS:  return "marine-engineering"
    return "engineering"
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/knowledge/run-batch-pack-1.py | runner executing the classification + stub generation pipeline |
| Create | tests/knowledge/test_batch_pack_1.py | TDD coverage for filter, partition, classifier, stub, duplicate-check |
| Create | docs/reports/batch-pack-1-api-portal-metadata-stubs.md | primary output (wiki-ready stubs grouped by domain) |
| Create | data/document-index/batch-pack-1-follow-on-issues.yaml | catalog of entries whose `notes` were insufficient for metadata-first promotion |
| Modify | data/document-index/online-resource-registry.yaml | additive `processed: true` + `processed_date` flag on the 40 covered entries; no schema change, no note rewrite |
| Update | docs/plans/README.md | add index row for this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_filter_yields_exact_40_entries | filter(type in {data_api, standard_portal}) count = 40 against committed registry | committed `online-resource-registry.yaml` | len == 40 |
| test_partition_notes_quality_threshold_rejects_empty_notes | notes-length < 120 chars → insufficient bucket | entry with 30-char note | entry in insufficient |
| test_partition_notes_quality_threshold_accepts_endpoint_mention | notes ≥120 chars AND "endpoint" keyword → sufficient | synthesized entry with 250-char note mentioning "REST endpoint" | entry in sufficient |
| test_classify_domain_marine_tag_wins | tag-based domain wins over URL heuristic | entry tagged `[marine, wave]` with engineering-like URL | domain == "marine-engineering" |
| test_classify_domain_default_engineering | no marine/naval signal falls back to engineering | synthesized plain data-api entry | domain == "engineering" |
| test_build_stub_frontmatter_matches_wiki_schema | stub YAML has required fields `title`, `tags`, `added`, `last_updated` | sample entry | frontmatter keys are a superset of required set |
| test_duplicate_check_detects_existing_wiki_page | if existing wiki page has same `sources:` frontmatter entry, flag is set | fixture wiki page referencing entry id `noaa-ndbc` | stub.duplicate_candidate is not None |
| test_processed_flag_is_additive_only | writing back `processed: true` does not mutate any other fields | registry in-memory → round-trip yaml | diff only on `processed`/`processed_date` keys |
| test_output_report_groups_all_40_sufficient_minus_insufficient | total stubs + insufficient == 40 | full registry filter | count invariant holds |
| test_run_is_idempotent | re-running with already-processed entries yields no new stubs | already-flagged registry | report reports 0 newly-added |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/knowledge/test_batch_pack_1.py -v`
- [ ] `uv run python scripts/knowledge/run-batch-pack-1.py` exits 0 and produces `docs/reports/batch-pack-1-api-portal-metadata-stubs.md`
- [ ] The output report contains exactly 40 rows classified as either `sufficient → stub generated` or `insufficient → follow-on catalog`, summing to 40 (pre-run invariant preserved)
- [ ] Each generated stub has `target_wiki_domain ∈ {engineering, marine-engineering, naval-architecture}`
- [ ] Each generated stub records provenance (`sources: [<registry-entry-id>]`) and source URL
- [ ] Duplicate check runs against the current live wiki corpus; every matched pair is listed in a Duplicates section (does NOT block promotion — it flags it)
- [ ] `data/document-index/batch-pack-1-follow-on-issues.yaml` exists and lists every deferred entry with a reason code
- [ ] `online-resource-registry.yaml` only diffs on `processed`/`processed_date` keys (verified by structural diff in CI fixture)
- [ ] No files under `config/**`, `.claude/**`, `knowledge/wikis/**` are modified
- [ ] Review artifacts for all three providers posted to `scripts/review/results/`
- [ ] No wiki pages promoted — downstream #2039/#2067 consume the report

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | (to be filled by fanout) |
| Codex | PENDING | (to be filled by fanout) |
| Gemini | PENDING | (to be filled by fanout) |

**Overall result:** PENDING

Revisions made based on review: (none yet — this is draft v1)

---

## Risks and Open Questions

- **Risk (forbidden-path tension):** Batch-pack spec §3.1 lists `scripts/**` as forbidden for batch-execution agents. This plan proposes a new `scripts/knowledge/run-batch-pack-1.py`. Rationale: the forbidden-path rule in the spec governs runtime-execution write scope, not whether a committed helper tool may exist. Existing adjacent tools (`wiki-cross-links.py`, `llm_wiki.py`) set the precedent. User approves at plan review whether to land the runner under `scripts/knowledge/` or inline it as a notebook-style artifact under `docs/reports/`.
- **Risk (classifier precision):** Deterministic keyword classifier will misclassify edge entries (e.g., a hydrodynamic-data API with no marine tag). Mitigation: run produces a Classifier Trace section in the output report listing the signal that decided each entry's domain, so a reviewer can catch misassignments during wiki-ingest follow-on.
- **Risk (insufficient-notes false-positives):** The 120-char + keyword threshold may push adequately-documented entries into the follow-on catalog. Mitigation: threshold is recorded in the report and is adjustable by flag for re-runs; first-pass results are treated as a starting corpus, not a final split.
- **Risk (duplicate-check on marine-engineering):** The marine-engineering wiki has 19,191 pages — naive substring scan is slow. Mitigation: duplicate check uses `sources:` frontmatter index only (one pass over the tree building `source-id → page` map), not full-text.
- **Risk (additive-only registry write):** Any yaml round-trip library may reorder keys or change quoting. Mitigation: use `ruamel.yaml` preserving order + style, plus structural-diff test in acceptance.
- **Open:** Should "processed" markers be written inline in `online-resource-registry.yaml` (this plan) or emitted to a sidecar `online-resource-registry.processed.yaml`? Flag for user during plan approval — sidecar is a clean alternative that avoids any registry churn risk.
- **Open:** Should the follow-on catalog auto-file GitHub child issues under #2390 (or leave issue creation to a human)? This plan defaults to NOT auto-filing; user decides at approval.

---

## Complexity: T2

**T2** — new runner + TDD test module + report + optional sidecar catalog; modifies one existing data file additively; no schema changes; uses existing registries; no network calls.
