# Conference-Corpus Coverage Baseline & Deferral Memo (#2305)

**Date:** 2026-04-17
**Parent:** #1878 (closed — main-index enrichment)
**Deferred to:** **#2325** (conference-corpus enrichment design)
**Companion artifacts:** #2306 (maturity YAML bookkeeping), #2307 (accessibility registry contract)

---

## TL;DR

The conference corpus is **0% enriched** and **0% covered** by the main ace-drive summaries directory. The #1878 enrichment pipeline cannot run unchanged against it because of schema divergence and path-universe mismatch. Rather than ship 49K rows of misleading `summary_done=False` metadata or speculate on a new design mid-PR, this issue is being resolved-by-decision and the design work is deferred to **#2325** with concrete revival criteria.

---

## Baseline probe (empirical, 2026-04-17)

Run from `/mnt/local-analysis/workspace-hub`:

| File | Records | `content_type` populated | `summary_done=True` | Path-fallback match against `/mnt/ace/data/document-index/summaries/` |
|---|---:|---:|---:|---:|
| `data/document-index/conference-index-batch.jsonl` | 22,069 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `data/document-index/conference-index.jsonl` | 27,735 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `data/document-index/conference-phase-a-results.jsonl` | 14,180 | 0 (0.0%) | 0 (0.0%) | — (not an index file; see below) |

Random sample probe: 0/100 summaries in `/mnt/ace/data/document-index/summaries/` (717,141 total files) reference a conference-pattern path (searched for "onference", "OMAE", "OTC").

Directory check: `ls /mnt/ace/data/document-index/` returns exactly one subdirectory, `summaries/`. **No conference-specific summaries directory exists.**

---

## Schema divergence

The #1878 enrichment script (`scripts/data/document-index/enrich-summary-metadata.py`) keys on:

- `record["ext"]` for `content_type` derivation (via `content_type_map.yaml`)
- `record["content_hash"]` for primary summary-file lookup (falls back to `sha256(path)[:16]`)

Conference schemas differ:

| File | Keys | `ext` / `extension` | `content_hash` |
|---|---|---|---|
| `conference-index-batch.jsonl` | `{conference, extension, path, source}` | `extension` (with leading dot, e.g. `.pdf`) | absent |
| `conference-index.jsonl` | `{collection, extension, filename, path, relative_path, size_bytes, year}` | `extension` (with leading dot) | absent |
| `conference-phase-a-results.jsonl` | `{conference, extraction_status, file_size_bytes, page_count, path, title, year}` | neither (this is a Phase-A extraction-results audit artifact, not an index) | absent |

So the Scope 3 claim in #2305 ("The enrichment script, validator, and carryover helper from #1878 should work unchanged") is empirically falsified. Any enrichment would require a new schema adapter.

---

## The sibling file: `conference-phase-a-results.jsonl`

This file (14,180 records) sits in the same directory and was examined to confirm it is **not a third index** but an audit trail of Phase-A text extraction (page counts, extraction status, titles). It does not carry enriched fields and is not a candidate for the same enrichment pattern.

Flagged for the successor issue (#2325): this file's `title` and `page_count` may be a partial substitute for summary content, and could be joined into any eventual conference enrichment.

---

## The 1.03M-record maturity-YAML gap (partially explained)

`data/document-index/resource-intelligence-maturity.yaml` publishes `total_index_records: 1033933`. Adding up what we know:

| Source | Count |
|---|---:|
| `index.jsonl` unique records | 649,564 |
| `index.jsonl` provenance events (~1 per record) | 649,655 |
| `conference-index.jsonl` | 27,735 |
| `conference-index-batch.jsonl` | 22,069 |
| `conference-phase-a-results.jsonl` | 14,180 |
| **Sum of 4 files** | **713,548** |
| **Maturity YAML claim** | **1,033,933** |
| **Gap** | **~320,385** |

Hypotheses for the 320K unaccounted records, most likely first:

1. **Older shards / snapshots.** The `data/document-index/shards/` directory exists; if the maturity YAML aggregates across shard snapshots (pre-dedup), it would over-count. This is the most plausible source of a clean 320K delta.
2. **Pre-dedup raw scan count.** Phase A deduplicates by `content_hash` before writing the canonical index; a pre-dedup raw scan may have counted duplicates that got merged out.
3. **Cross-corpus aggregation.** The figure could include records from a third corpus (e.g., an older `og_standards` snapshot) not currently represented in the workspace.

**Scope boundary:** This gap is not fully resolved here. Listed in #2325's "related" section so it is investigated alongside conference enrichment.

---

## Why partial enrichment now is a bad idea

A superficially attractive alternative: derive `content_type` from `extension` (strip the dot; reuse `content_type_map.yaml`) and set `summary_done=False` across all conference records. This was explicitly rejected:

1. **No way to validate `summary_done=False`.** For the main index, False means "summary file checked, content empty." For conferences, it would mean "we didn't look because we couldn't." Same field value, different semantics — an invisible trap.
2. **Misleading observed coverage.** Shipping two new populated fields makes the corpus look "enriched" to consumers of the accessibility registry, when in reality only one signal is computed.
3. **#2309 will break it anyway.** The upcoming `summary_done` / `summary_file_exists` split assumes summaries either exist or don't. If we pre-populate `summary_done=False` on conferences without a matching summaries pool, #2309's logic would need a third state.

A clean new design in #2325 is cheaper than retrofitting a partial shim.

---

## Recommendation: defer to #2325

#2325 owns the conference-enrichment design. This memo is the closeout for #2305. Specifically, #2325 should decide between three options (full text in that issue):

- **A.** Generate summaries via Phase-B-style extraction on the 14K Phase-A results.
- **B.** Ship `content_type`-only enrichment; omit `summary_done` or carry a documented caveat.
- **C.** Defer indefinitely (conference corpus not agent-queryable via enriched path).

### Revival criteria (from #2325)

Work #2325 when any of:

- Conference summaries are produced in a separate pipeline (check `conference-phase-a-results.jsonl` growth).
- An agent workflow requires conference `content_type` for routing (trigger: first downstream consumer requests it).
- A decision is made to unify conference-corpus handling with the main index (likely tied to #2205 operating-model evolution).

---

## Sources consumed (per #2208 retrieval contract)

- Issue #1878 (main-index enrichment) — closed; ops results informed the "summaries coverage" comparison
- Issue #2305 — this issue's body, Scope 1-3 premises
- `data/document-index/conference-index-batch.jsonl` — schema probed
- `data/document-index/conference-index.jsonl` — schema probed
- `data/document-index/conference-phase-a-results.jsonl` — sibling artifact acknowledged
- `/mnt/ace/data/document-index/summaries/` — filename inventory + 100-sample content probe
- `scripts/data/document-index/enrich-summary-metadata.py` — reference for "reuse unchanged" premise
- `data/document-index/resource-intelligence-maturity.yaml` — 1.03M-record figure reconciled

## Promotion candidates (per #2208 / #2209)

- **For L3 durable knowledge:** the fact that **conference summaries are not present in the main ace summaries corpus** is worth surfacing in the #2307 accessibility registry entry (via a `gaps:` note on a potential new conference asset). Captured as an action for #2325.
- **None else.** Memo content is transient (L5) — the durable outcome is #2325's design decision.
