# Plan for #2369: Execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2369
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2369-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` — LLM-wiki helper module (read-only context).
- Found: `scripts/knowledge/wiki-cross-links.py` — cross-link generator; Batch Pack 2 output must be shape-compatible so cross-link candidates feed into #2068 without re-processing.
- Found: `scripts/knowledge/build-knowledge-index.sh`, `registry-freshness-check.py` — adjacent tooling, read-only context.
- Gap: No `scripts/knowledge/run-batch-pack-2.py` (or equivalent) exists; runner must be created.

### Standards
Not applicable — conferences papers are primary literature, not standards. Provenance still matters: every generated topic-stub must cite its source conference papers by record id.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — 83 pages, organized into `concepts/`, `entities/`, `sources/`, `standards/`, `workflows/`. Conference topic clusters most naturally slot into `concepts/` or `sources/`.
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema (`title`, `tags`, `added`, `last_updated` required).
- `knowledge/wikis/marine-engineering/CLAUDE.md` — 19,191 pages; Batch Pack 2 primary target for hydrodynamics/structural/marine clusters.
- `knowledge/wikis/naval-architecture/CLAUDE.md` — 46 pages; secondary target for hydrodynamics and seakeeping clusters.

### Documents consulted
- `docs/reports/llm-wiki-external-source-priority-queue.md` — Queue classifies `indexed-conference-papers` as P1, `summary-backed` promotion. §5.2 lists DOT/OMAE/ISOPE as phase_a_complete. **Contradicted by repo data — see §Gaps/Readiness mismatch below.**
- `docs/reports/llm-wiki-staged-batch-packs.md` — §3.2 defines Batch Pack 2 with paths (`data/document-index/**`, `docs/reports/**`, `docs/document-intelligence/**` owned; `knowledge/wikis/**`, `/mnt/ace/docs/conferences/**` read-only; `config/**`, `.claude/**`, `tests/**` forbidden), sub-slice plan by collection, and primary output `docs/reports/batch-pack-2-conference-summary-stubs.md`.
- `data/document-index/conference-paper-catalog.yaml` — **authoritative source of phase-a-complete status**: DOT (`year_range: 2001-2013`), OMAE (`year_range: 1998-2014`), OTC (`year_range: 1988-2017`) are phase_a_complete; ISOPE is `not_indexed`. See Evidence block.
- `data/document-index/conference-phase-a-results.jsonl` — 14,180 records; line 1 sample shows DOT entry with `title`, `page_count`, `extraction_status: success` fields.
- `data/document-index/conference-index-stats.yaml` — top-priority index lists OMAE (7,292 PDFs), OTC (5,432 PDFs), ISOPE (4,074 PDFs), DOT (1,456 PDFs); confirms ISOPE PDFs physically exist on mount but per catalog yaml they are not phase_a indexed.
- `data/document-index/conference-index-batch.jsonl`, `conference-index.jsonl`, `conference-index-manifest.json`, `conference-registry.yaml` — existing index outputs available for summary-backed promotion without PDF re-reads.
- Epic `#2390` — Groups #2369 under Wave 6 with explicit readiness note: "issue body names DOT/OMAE/ISOPE as phase-A-complete starter collections, but repo data indicated DOT/OMAE/OTC are phase-A complete while ISOPE is not yet indexed. This should be reconciled before execution."
- Related issue `#2068` (OPEN) — cross-link JSONL package; downstream consumer.
- Related issue `#2039` (OPEN) — engineering wiki ingest; downstream consumer.
- Related issue `#2001` (CLOSED) — batch ingest precedent; methodology reference.

### Gaps identified
- **Readiness mismatch (CRITICAL):** Issue body, queue doc §5.2, and batch-pack spec §3.2 all name DOT/OMAE/ISOPE as the phase_a_complete starter set. The authoritative catalog yaml names DOT/OMAE/OTC. This plan's first execution wave must use **DOT + OMAE + OTC** (the actual phase_a_complete set) and record OTC as a substitute for ISOPE. ISOPE is deferred as "pending re-indexing" per the batch-pack spec's own §3.2 follow-on rule.
- No canonical topic/domain taxonomy for conference clustering — plan uses the six domain heuristics in the spec (subsea, structural, marine, pipeline, VIV, hydrodynamics) plus a `misc` bucket and records the mapping decision.
- No schema for conference "topic stub" yet — plan defines one (title, target wiki, paper count, top-N paper citations, short abstract cluster, cross-link candidates).
- No explicit de-duplication policy for wiki stubs that overlap with existing wiki pages — plan adds a `sources`-frontmatter duplicate check mirroring the #2364 pattern.
- Issue body acceptance criterion "no source-PDF rereads are required for the first execution slice" requires runner to refuse to read under `/mnt/ace/docs/conferences/` (enforced by a path guard + unit test).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2369` — OPEN — feat(knowledge): execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs
- `#2390` — OPEN — epic(knowledge): llm-wiki strengthening roadmap
- `#2242` — CLOSED — priority queue
- `#2243` — CLOSED — staged batch packs
- `#2001` — CLOSED — batch ingest precedent
- `#2039` — OPEN — engineering wiki ingest
- `#2067` — OPEN — wire research into wiki ingest
- `#2068` — OPEN — cross-link JSONL package

**File existence** (`ls` 2026-04-23):
- EXISTS: `docs/reports/llm-wiki-external-source-priority-queue.md`
- EXISTS: `docs/reports/llm-wiki-staged-batch-packs.md`
- EXISTS: `data/document-index/conference-paper-catalog.yaml`
- EXISTS: `data/document-index/conference-phase-a-results.jsonl` (14,180 lines)
- EXISTS: `data/document-index/conference-index-stats.yaml`
- EXISTS: `data/document-index/conference-index-batch.jsonl`
- EXISTS: `data/document-index/conference-index.jsonl`
- EXISTS: `data/document-index/conference-index-manifest.json`
- EXISTS: `data/document-index/conference-registry.yaml`
- MISSING (new — this plan creates): `scripts/knowledge/run-batch-pack-2.py`
- MISSING (new — this plan creates): `tests/knowledge/test_batch_pack_2.py`
- MISSING (new — this plan creates): `docs/reports/batch-pack-2-conference-summary-stubs.md`
- MISSING (new — this plan creates): `data/document-index/batch-pack-2-cross-link-candidates.jsonl`

**Line excerpts** (`grep/awk` 2026-04-23):
- `conference-paper-catalog.yaml` phase_a_complete entries (matched by `awk ... | paste - - | grep phase_a_complete`):
  ```
  - name: DOT      indexing_status: phase_a_complete
  - name: OMAE     indexing_status: phase_a_complete
  - name: OTC      indexing_status: phase_a_complete
  ```
- `conference-paper-catalog.yaml` ISOPE record:
  ```
  - name: ISOPE
    path: /mnt/ace/docs/conferences/ISOPE
    indexing_status: not_indexed
  ```
- `llm-wiki-external-source-priority-queue.md` §5.2 line 85 (contradicting source):
  ```
  ISOPE | 4,183 | 4,074 | marine, hydrodynamics | phase_a_complete
  ```
- `llm-wiki-staged-batch-packs.md` §3.2 line 144 (contradicting source):
  ```
  | Source filter | indexing_status = phase_a_complete (DOT, OMAE, ISOPE) |
  ```

**Gap proofs**:
- `ls /mnt/local-analysis/workspace-hub/scripts/knowledge/run-batch-pack-2*.py 2>&1` → "No such file or directory" → runner not yet committed.
- Actual phase_a_complete set: **3 collections (DOT + OMAE + OTC)**, total indexed PDFs 1,456 + 7,292 + 5,432 = **14,180**, which matches the line count of `conference-phase-a-results.jsonl` exactly (14,180 lines).

<!-- Source count: 11 (issue body + 10 artifacts) — exceeds ≥3 minimum. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-23-issue-2369-batch-pack-2-conference-summary-promotion.md |
| Runner | scripts/knowledge/run-batch-pack-2.py (new) |
| Tests | tests/knowledge/test_batch_pack_2.py (new) |
| Primary output report | docs/reports/batch-pack-2-conference-summary-stubs.md (new) |
| Cross-link candidates | data/document-index/batch-pack-2-cross-link-candidates.jsonl (new — input for #2068) |
| Plan review — Claude | scripts/review/results/2026-04-23-plan-2369-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-23-plan-2369-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-23-plan-2369-gemini.md |
| Plan review — disagreement | scripts/review/results/2026-04-23-plan-2369-disagreement.md |

---

## Deliverable

After this issue closes, `docs/reports/batch-pack-2-conference-summary-stubs.md` will exist, containing wiki-ready topic-cluster stubs derived from phase_a_complete conference indexing (actual set: DOT, OMAE, OTC), grouped by engineering domain (subsea, structural, marine, pipeline, VIV, hydrodynamics, misc) and mapped to target wiki domains (marine-engineering, naval-architecture, engineering). A companion JSONL cross-link-candidate file will exist at `data/document-index/batch-pack-2-cross-link-candidates.jsonl` for #2068 consumption. ISOPE will be explicitly deferred with a filed follow-on issue for re-indexing. No source-PDF reads will occur. No wiki pages will be promoted in this issue — the report is the input that downstream wiki-ingest work consumes.

---

## Pseudocode

```
function run_batch_pack_2(catalog_path, phase_a_jsonl, output_report_path):
    catalog = load_yaml(catalog_path)
    indexed = [c for c in catalog.conferences if c.indexing_status == "phase_a_complete"]
    assert {c.name for c in indexed} == {"DOT", "OMAE", "OTC"}    # actual phase_a set
    if {"ISOPE"} & {c.name for c in catalog.conferences if c.indexing_status != "phase_a_complete"}:
        defer_and_log("ISOPE", reason="not_indexed per catalog")  # explicit deferral

    papers = load_jsonl(phase_a_jsonl)
    assert path_guard_never_reads("/mnt/ace/docs/conferences/")   # hard invariant

    clusters = {d: [] for d in DOMAIN_BUCKETS}                    # 6 engineering domains + misc
    for paper in papers:
        domain = classify_paper_domain(paper.title, paper.conference, paper.path)
        clusters[domain].append(paper)

    stubs = []
    for domain, papers_in_domain in clusters.items():
        if len(papers_in_domain) == 0: continue
        topic_clusters = cluster_by_topic(papers_in_domain, top_n_per_cluster=10)
        for topic in topic_clusters:
            target_wiki = choose_target_wiki(domain, topic)
            stub = build_topic_stub(topic, target_wiki, provenance=[p.id for p in topic.top_papers])
            stub.duplicate_candidate = check_wiki_duplicate(stub.title, stub.sources, wiki_root)
            stubs.append(stub)

    write_report(output_report_path, stubs, deferred_collections=["ISOPE"])
    write_cross_link_jsonl("data/document-index/batch-pack-2-cross-link-candidates.jsonl", stubs)
    return summary(total_papers=len(papers), clusters=len(stubs), deferred=["ISOPE"])
```

```
function classify_paper_domain(title, conference, path):
    # Deterministic keyword match over the title. Precedence order: pipeline > VIV > hydrodynamics > marine > structural > subsea > misc.
    # Conference and path are fallback signals only.
    ...
```

```
function cluster_by_topic(papers, top_n_per_cluster):
    # Simple TF-IDF-style term grouping over titles; no network, no ML model download.
    # Returns a list of cluster objects with topic_label, top_papers (by a deterministic relevance score), paper_count.
    ...
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/knowledge/run-batch-pack-2.py | runner executing domain classification + topic clustering |
| Create | tests/knowledge/test_batch_pack_2.py | TDD coverage (14 tests, see list) |
| Create | docs/reports/batch-pack-2-conference-summary-stubs.md | primary output (topic stubs grouped by domain + wiki target) |
| Create | data/document-index/batch-pack-2-cross-link-candidates.jsonl | input for #2068 cross-link JSONL packaging |
| Update | docs/plans/README.md | add index row for this plan |
| (No modify) | data/document-index/conference-paper-catalog.yaml | plan does NOT rewrite ISOPE status — if ISOPE is ever indexed, that is scope of a separate follow-on issue |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_catalog_phase_a_complete_set_is_dot_omae_otc | authoritative phase_a set excludes ISOPE | committed catalog yaml | set == {"DOT","OMAE","OTC"} |
| test_isope_is_deferred_not_processed | ISOPE flagged as deferred with `not_indexed` reason | committed catalog yaml | "ISOPE" ∈ deferred_collections; no papers in output |
| test_phase_a_jsonl_line_count_matches_catalog | 14,180 lines accounts for DOT+OMAE+OTC pdf totals | committed phase_a_jsonl | 14,180 |
| test_path_guard_rejects_reading_conference_pdf_dir | runner refuses to open anything under /mnt/ace/docs/conferences/ | spy filesystem wrapper | PermissionError on attempted open |
| test_classify_paper_domain_pipeline_wins | title containing "pipeline" classifies to pipeline | title "Pipeline integrity under sour service" | domain == "pipeline" |
| test_classify_paper_domain_viv | title containing "VIV" classifies to VIV | title "VIV fatigue in deepwater risers" | domain == "VIV" |
| test_classify_paper_domain_default_misc | no keyword hit → misc | title "A general approach" | domain == "misc" |
| test_cluster_preserves_paper_count_per_domain | sum(cluster.paper_count) == len(papers_in_domain) | synthetic 100-paper domain | invariant holds |
| test_cluster_top_n_is_deterministic | same input → identical top-N ordering | fixed-seed inputs | byte-identical output |
| test_build_topic_stub_frontmatter_has_required_keys | stub frontmatter has `title`, `tags`, `added`, `last_updated` | synthesized cluster | keys present |
| test_build_topic_stub_provenance_is_list_of_paper_ids | provenance refers back to conference-phase-a-results.jsonl ids | synthesized cluster | each `sources:` entry resolvable to a phase_a record |
| test_duplicate_check_detects_existing_wiki_page | existing wiki page with matching `sources:` is flagged | fixture wiki page + stub | duplicate_candidate not None |
| test_cross_link_jsonl_schema | output JSONL rows conform to #2068 candidate schema | produced JSONL | pass schema check |
| test_runner_is_idempotent | re-running with same inputs yields identical report + JSONL bytes | run twice | byte-identical outputs |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/knowledge/test_batch_pack_2.py -v`
- [ ] `uv run python scripts/knowledge/run-batch-pack-2.py` exits 0 and produces `docs/reports/batch-pack-2-conference-summary-stubs.md` and `data/document-index/batch-pack-2-cross-link-candidates.jsonl`
- [ ] Output report explicitly records **DOT + OMAE + OTC** as processed and **ISOPE** as deferred with reason
- [ ] Runner never reads under `/mnt/ace/docs/conferences/` (enforced by test_path_guard_rejects_reading_conference_pdf_dir)
- [ ] Sum of classified papers == 14,180 (phase_a_complete total per repo data)
- [ ] Each stub's `target_wiki_domain ∈ {engineering, marine-engineering, naval-architecture}`
- [ ] Each stub records provenance as a list of phase-a record ids
- [ ] Duplicate-check flags overlapping existing wiki pages (does NOT auto-merge)
- [ ] Cross-link JSONL conforms to the #2068 candidate schema
- [ ] No wiki pages are promoted (knowledge/wikis/** read-only guard holds — verified by git diff scope)
- [ ] No files under `config/**`, `.claude/**` are modified
- [ ] ISOPE re-index follow-on issue is filed (or flagged for user to file) and linked from the report
- [ ] Review artifacts for all three providers posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | (to be filled by fanout) |
| Codex | PENDING | (to be filled by fanout) |
| Gemini | PENDING | (to be filled by fanout) |

**Overall result:** PENDING

Revisions made based on review: (none yet — draft v1)

---

## Risks and Open Questions

- **Risk (inherited misstatement):** Two committed upstream artifacts — the priority-queue doc §5.2 and the staged-batch-packs spec §3.2 — both name `DOT/OMAE/ISOPE` as the phase_a set. This plan does not rewrite those historical artifacts (they belong to closed issues #2242/#2243). Instead the plan treats the live `conference-paper-catalog.yaml` as authoritative and records the discrepancy explicitly in the output report. Optional follow-on: a documentation-only PR updating the two report docs to read "DOT/OMAE/OTC (ISOPE deferred pending re-indexing)" — flagged for user decision at plan review, not bundled into this issue.
- **Risk (OMAE scale):** OMAE alone contributes 7,292 phase_a PDFs. Even without PDF reads, TF-IDF clustering over 7,292 titles can be slow. Mitigation: runner supports `--collections` to sub-slice per spec §3.2 "Sub-slicing for Overnight Runs"; CI runs use a fixture sub-sample.
- **Risk (classifier precision):** Deterministic title-keyword classification will misclassify cross-domain papers. Mitigation: same Classifier Trace pattern as #2364, plus per-cluster confidence signal.
- **Risk (PDF read-through):** Any accidental use of a helper that follows file paths in phase_a JSONL could open PDFs. Mitigation: explicit path guard invariant + failing test.
- **Risk (duplicate-check scope):** The marine-engineering wiki is 19,191 pages; duplicate-check uses a `sources:` frontmatter index (same approach as #2364), not full-text scan.
- **Open:** Should the report group stubs first by `target_wiki_domain` (engineering/marine/naval) or first by engineering-topic-domain (pipeline/VIV/hydrodynamics/...)? Defaults to topic-domain per spec §3.2 step 2; user may reverse at approval time.
- **Open:** Should OTC appear as an explicit rename of ISOPE in the output, or as a co-equal third collection? This plan defaults to co-equal (with ISOPE deferred) because that matches authoritative repo state.
- **Open:** Auto-filing the ISOPE re-index follow-on issue vs leaving issue creation to a human. Plan defaults to leaving it to a human (writes a proposed issue body to the report).

---

## Complexity: T2

**T2** — new runner + TDD test module + report + JSONL cross-link artifact; zero mods to wiki pages; reads only indexed JSONL/YAML (no PDFs); explicit readiness-mismatch reconciliation is the load-bearing correctness move.
