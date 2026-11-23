# Plan for #2305: Conference-index-batch coverage baseline + decision memo

> **Status:** adversarial-reviewed
> **Complexity:** T1
> **Date:** 2026-04-17 (rev-2 after Claude APPROVE+MINOR)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2305
> **Parent:** #1878 (closed)
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2305-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `data/document-index/conference-index-batch.jsonl` — 22,069 records. Schema: `{conference, extension, path, source}`. Thinner than `index.jsonl`; no `ext`, `content_hash`, `domain`.
- Found: `data/document-index/conference-index.jsonl` — 27,735 records. Schema: `{collection, extension, filename, path, relative_path, size_bytes, year}`. Richer than batch but still no `content_hash`.
- Found: `scripts/data/document-index/enrich-summary-metadata.py` (from #1878) — keys on `record.get("ext")` and `record.get("content_hash")`. **Would not run unchanged** against conference schema.
- Found: `scripts/data/document-index/_summary_lookup.py` (from #1878) — path-fallback uses `sha256(path.encode()).hexdigest()[:16]`.
- Gap: No schema-adapter exists to handle `extension` → `ext`. No conference-specific summary pipeline.

### Standards
Not applicable.

### LLM Wiki pages consulted
Not applicable.

### Documents consulted

| Source | Finding |
|---|---|
| Issue #2305 body | Scope 1: report baseline count. Scope 2: if >10% broken, enrich. Scope 3: reuse enrichment unchanged. |
| Empirical probe (this session, 2026-04-17) | Both conference files: 0% content_type, 0% summary_done, **0% path-fallback match** against `/mnt/ace/data/document-index/summaries/` (717,141 files). |
| Empirical probe (100 random ace summaries) | 0/100 sampled summaries reference a conference-pattern path (searched for "onference", "OMAE", "OTC"). No conference summaries found in the main ace summaries dir. |
| `ls /mnt/ace/data/document-index/` | Only one `summaries/` directory; no conference-specific sibling dir exists. |
| #2306 (closed, `a13da73df`) | Maturity YAML now holds `index_jsonl_only` block. This plan should NOT touch the `total_index_records: 1033933` combined figure; the conference-batch scope is the remainder (1.03M − 649K ≈ 384K, but the actual conference files only total 22K + 28K — a mismatch worth noting). |

### Gaps identified

- Ace drive summaries do not cover the conference corpus.
- Enrichment script uses `ext` field name; conference schema uses `extension`.
- The maturity YAML's 1.03M combined figure is larger than `index.jsonl` (649K) + conference files (22K + 28K = 50K). The origin of the 1.03M is unclear — a **third, older, or combined-differently** corpus may be feeding that figure. Worth flagging but out of scope for #2305.

<!-- Source count: 6 distinct (issue body + 5 others). Contract requires ≥3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2305-conference-batch-baseline.md` |
| Baseline report | `docs/reports/2026-04-17-issue-2305-conference-batch-baseline.md` |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2305-claude.md` |

---

## Deliverable

A markdown report at `docs/reports/2026-04-17-issue-2305-conference-batch-baseline.md` that:

1. Confirms 100% of conference records (both files) lack `content_type` / `summary_done`
2. Confirms 0% path-fallback match against the main ace summaries dir
3. Documents the schema divergence (`extension` vs `ext`; no `content_hash`)
4. Recommends: **defer full conference enrichment to a new issue** rather than trying to run the current enrichment pipeline against an incompatible corpus
5. Flags the 1.03M-record mismatch in the maturity YAML for a separate investigation

---

## Pseudocode

T1 — trivial. Report generation from existing probe data. No code.

---

## Edit specification

**Create:** `docs/reports/2026-04-17-issue-2305-conference-batch-baseline.md` with the baseline numbers, schema comparison, and recommendation (content detailed below).

**Update:** `docs/plans/README.md` to add this plan row.

**No** edits to `conference-index-batch.jsonl`, `conference-index.jsonl`, or the enrichment pipeline.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/reports/2026-04-17-issue-2305-conference-batch-baseline.md` | The decision memo is the deliverable |
| Update | `docs/plans/README.md` | Plan row |

---

## TDD Test List

Not applicable — decision memo, not code.

---

## Acceptance Criteria

- [ ] Report file exists at the path above
- [ ] Report cites empirical numbers: `conference-index-batch.jsonl`=22,069, `conference-index.jsonl`=27,735, both 0% content_type + 0% summary_done + 0% ace-summary match
- [ ] Report explicitly mentions `conference-phase-a-results.jsonl` (14,180 records, sibling Phase-A processing artifact; schema `{conference, extraction_status, file_size_bytes, page_count, path, title, year}`) so future readers see it was examined, not overlooked
- [ ] Report documents schema divergence (`extension` vs `ext`; no `content_hash`)
- [ ] Report affirms the negative: `ls /mnt/ace/data/document-index/` shows only `summaries/` — no conference-specific summaries dir exists
- [ ] Report contains a "Recommendation" section with a concrete next-step proposal (file follow-up issue vs. partial-enrichment-now)
- [ ] Report **names at least one hypothesis** for the 1.03M vs ~700K gap (empirical: index 649K, provenance events 649.6K, 4-file sum 713K; 320K unaccounted). Candidates to list: older shard/snapshot in `data/document-index/shards/`; pre-dedup raw scan count; cross-corpus aggregation
- [ ] Report defines **revival criteria** for the follow-up issue (concrete triggers, e.g., "when conference summaries are produced" or "decision to ship content_type-only enrichment")
- [ ] At close time, a new follow-up issue is filed for conference enrichment; the memo is updated with its number, and #2305 close comment links it

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE+MINOR (5 memo-content asks → addressed in rev-2) | Deferral is empirically honest, not evasive. Asks: (1) name 1.03M-gap hypothesis; (2) acknowledge sibling `conference-phase-a-results.jsonl`; (3) affirm negative on conference summaries dir; (4) define revive criteria; (5) name follow-up issue number. All 5 incorporated into rev-2 acceptance criteria. |

**Overall result:** Ready for approval.

Revisions made in rev-2:
- Added probe for the 1.03M mismatch: index=649,564 / provenance=649,655 / 4-file-sum=713,548 → 320K unaccounted; plan now requires memo to name at least one hypothesis
- Added requirement to explicitly acknowledge `conference-phase-a-results.jsonl` (14,180 records, Phase-A extraction-results artifact)
- Added requirement to affirm the negative (no conference-specific summaries dir)
- Added revival-criteria requirement
- Added follow-up-issue-number requirement (file at close time, link back)

---

## Risks and Open Questions

- **Risk:** A future reader might interpret "deferred to follow-up" as "low priority." The report should make clear this is a **scope-honest** decision, not a downgrade — the ace summaries simply don't cover conference paths.
- **Open:** Should the report recommend **partial enrichment** (add `content_type` from `extension`, leave `summary_done` as False) now, versus full deferral? Default recommendation in the report: **full deferral**, because (a) `summary_done=False` everywhere is misleading metadata if there's no way to validate it, and (b) schema divergence means the "reuse unchanged" premise of #2305 doesn't hold — any enrichment would be a new design.
- **Open:** Why does maturity YAML say 1.03M combined records when index.jsonl (649K) + conference files (22K + 28K) = ~700K? Recommend: separate follow-up issue to reconcile (also goes into the report).

---

## Complexity: T1

Single markdown report generation from probe data already in hand. No code, no tests, no schema changes. Single-provider adversarial review sufficient.
