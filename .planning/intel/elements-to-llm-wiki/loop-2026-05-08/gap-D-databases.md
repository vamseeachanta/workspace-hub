# llm-wiki Ecosystem — Gap D: Databases & Registries

**Generated:** 2026-05-08
**Scope:** All registries / index files / databases that participate in (or should participate in) the llm-wiki ecosystem.
**Method:** ~10 wall-min directory walk + grep-based consumer-graph trace across `/scripts/`, `/.claude/skills/`, `/.github/`. READ-ONLY.

---

## Executive Summary (≈200 words)

The llm-wiki ecosystem rests on **~25 registries/databases** spread across six surfaces: `data/document-index/` (the heaviest, ~22 YAML/JSONL files), `data/design-codes/`, `config/document-intelligence/` (empty stub), `config/ai-tools/`, `knowledge-base/`, and `llm-wiki/seeds/`. Roughly **40% have a live, in-tree consumer** (a non-review-results script or skill that loads the file). The remaining 60% are read by humans, by review-cycle plans, or by no one at all. The single most under-utilized asset is **`.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv` (671 records, 190 KB)** — produced 2026-05-01 by `build-elements-wiki-inventory.py` and explicitly cited in `wiki-ingest-report.md` as the queue for issue #2536, but **no script, skill, or cron job consumes it**; it exists as a one-shot file. The most broken reference is the **`config/document-intelligence/` directory itself**: `.gitkeep` only, 0 files, despite multiple skills and the `intelligence-accessibility-registry.yaml` parent-model link pointing to it as the configuration surface for doc-intelligence runs. Elements ingest artifacts (8 buckets, 41,561 files, 1.92 TB indexed) landed sources/catalog pages into 5 wiki domains but never propagated into the `intelligence-accessibility-registry` (no `wiki-asset-management` / `wiki-engineering-standards` / `wiki-lng-projects` rows in registry v1.1.2). The Elements ingest is durable on the wiki side (frontmatter-validated source pages) but **stuck as transient intel on the registry side**.

---

## 1. Master Inventory Table

### 1A. `data/document-index/` (primary doc-intelligence surface)

| File | Format | Rows / Keys | Producer | Consumer(s) | Last-mod | Role |
|---|---|---|---|---|---|---|
| `intelligence-accessibility-registry.yaml` | YAML | ~30 assets, schema v1.1.2 | hand-edited | `scripts/data/document-index/validate-accessibility-registry.py`; referenced by `data-intelligence-map.md`, `holistic-resource-intelligence.md` | 2026-05-01 | Map of all wikis/registries/maps with reachability metadata (#2136) |
| `resource-intelligence-maturity.yaml` | YAML | 59 lines, ~12 metrics | hand-edited | none in tree (markdown twin tracked) | 2026-04-17 | Standards-read percentage, key-calc maturity tracker |
| `resource-intelligence-maturity.md` | MD | summary | hand-edited | none in tree | 2026-04-22 | Human-readable twin of YAML above |
| `online-resource-registry.yaml` | YAML | 247 entries, 152 KB | `build-online-resource-registry.py`, `connect-web-resources-to-registry.py` | `cross-reference-registries.py`, `registry-freshness-check.py`, `external-doc-reingest.sh`, `generate-domain-resource-views.py`, `download_and_catalog.py` | 2026-04-16 | Web resources canonical list (most-consumed registry) |
| `online-resource-registry-patch-2026-05-03.yaml` | YAML | 10 KB patch | hand-edited | none yet — pending merge | 2026-05-03 | Standalone patch file (orphan candidate) |
| `llm-wiki-external-source-priority-queue.yaml` | YAML | 334 lines, 5 priority families | hand-edited (#2242) | none in tree (referenced from issue plans only) | 2026-04-14 | P1-P4 priority queue, depends on 7 upstream registries |
| `mounted-source-registry.yaml` | YAML | 8 source roots | hand-edited | referenced by priority-queue.yaml | 2026-04-11 | Drive-mount inventory |
| `conference-registry.yaml` | YAML | 27,735 files | `phase-a-index.py`, `prep-conference-index.py` | `cross-reference-registries.py`, `conference-stats.py` | 2026-04-05 | Conference-paper index |
| `conference-paper-catalog.yaml` | YAML | 30 conferences, ~22k PDFs | `phase-a-index.py` | priority-queue.yaml | 2026-04-04 | Catalog twin of conference-registry |
| `conference-index.jsonl` | JSONL | 7.4 MB | `phase-a-index.py` | `conference-stats.py` | 2026-04-05 | Per-paper records |
| `conference-index-batch.jsonl` | JSONL | 3.4 MB | `phase-a-index.py` | none in tree | 2026-04-04 | Batch checkpoint (orphan) |
| `conference-phase-a-results.jsonl` | JSONL | 11 MB | `phase-a-index.py` | none in tree | 2026-04-04 | Phase-a output (likely orphan) |
| `dde-literature-catalog.yaml` | YAML | 87 items, 5,456 PDFs | `dde-migration-report.py`, `build-ledger.py` | priority-queue.yaml; `cross-reference-registries.py` (indirect) | 2026-04-03 | Doris DDE drive lit catalog |
| `dde-standards-inventory.yaml` | YAML | 20 KB | `phase-a-index.py` | `cross-reference-registries.py` (indirect) | 2026-04-03 | DDE-drive standards listing |
| `dde-oil-gas-codes-scan.yaml` | YAML | 6 KB | `phase-a-index.py` | none direct | 2026-04-03 | Oil-gas codes scan output |
| `dde-migration-report.yaml` | YAML | 2 KB | `dde-migration-report.py` | none direct | 2026-04-04 | Migration audit report |
| `standards-transfer-ledger.yaml` | YAML | 425 standards, 240 KB | `build-ledger.py` | `ace_resource_audit.py`, `generate-domain-resource-views.py`, `acma_wiki_unblock.py`, `cross-reference-registries.py`, `mark-exhausted.py`, `query-ledger.py`, `reclassify-domains.py` (most-consumed file in the surface) | 2026-04-11 | Local-standards ledger |
| `index.jsonl` | JSONL | 649,564 records, **623 MB** | `phase-a-index.py`, summary workers | `validate-index-metadata.py`, summary workers, downstream classifiers | 2026-04-17 | Master corpus index (heart of the doc-intel pipeline) |
| `index.jsonl.backup-2026-04-17` | JSONL | 604 MB | snapshot | none | 2026-04-16 | Backup; safe to age out |
| `research-literature-index.jsonl` | JSONL | 46 KB | `download_and_catalog.py` | none direct | 2026-04-05 | Research-literature subset |
| `coverage-audit.yaml` | YAML | 14 KB | `generate-coverage-report.py` | none direct | 2026-04-14 | Coverage audit output |
| `summary-extraction-plan.yaml` | YAML | 14 KB | `enrich-summary-metadata.py` | none direct | 2026-04-14 | Summary-extraction work plan |
| `freshness-cadences.yaml` | YAML | 5 KB | hand-edited (#2105) | governance plans only — no live consumer | 2026-05-01 | Per-asset freshness contracts |
| `enhancement-plan.yaml` | YAML | 1.7 MB | `phase-a-index.py` | none direct | 2026-03-15 | Old enhancement plan (archive candidate) |
| `registry.yaml` | YAML | 1.3 KB | `phase-a-index.py` | `cross-reference-registries.py` | 2026-04-01 | Top-level totals registry (small but live) |
| `marine-subdomain-tags.yaml` | YAML | 484 bytes | hand-edited | none direct | 2026-04-05 | Tag-list helper |
| `ship-plans-catalog.yaml` | YAML | 78 KB | hand-edited | none direct | 2026-03-31 | Ship-plans catalog |
| `public-og-data-sources.yaml` | YAML | 10 KB | hand-edited | none direct | 2026-03-31 | Public-OG data sources |
| `index-other-bucket-pack-manifest.yaml` | YAML | 610 KB | `build-index-other-bucket-packs.py` | none direct | 2026-04-14 | "Other" bucket pack manifest |
| `batch-pack-2-cross-link-candidates.jsonl` | JSONL | 6 KB | hand-edited | none direct | 2026-05-01 | Cross-link candidate output |
| `batch-pack-2-skipped.jsonl` | JSONL | 0 bytes | placeholder | none | 2026-05-01 | Empty skip log |
| `cross-drive-dedup-report.json` | JSON | 124 KB | `cross-drive-dedup-audit.py` | none direct | 2026-04-04 | Dedup audit |
| `engineering-refs-catalog.md` | MD | 9 KB | hand-edited | none direct | 2026-04-05 | Engineering refs (markdown) |
| `data-audit-report.md` | MD | 6.6 KB | hand-edited | none direct | 2026-04-22 | Audit report |
| `summaries/` | dir | 155 GB | summary workers | summary workers, `validate-index-metadata.py` | 2026-05-01 | Summary file tree (sidecar) |

### 1B. `data/design-codes/`

| File | Format | Rows | Producer | Consumer(s) | Last-mod | Role |
|---|---|---|---|---|---|---|
| `code-registry.yaml` | YAML | ~12 codes | hand-edited (#2216 / #2392) | `scripts/readiness/code-version-guard.sh` | 2026-03-31 | Design-code edition tracker (current/check/superseded) — **only consumer is the readiness guard** |

### 1C. `config/document-intelligence/`

| File | Format | Rows | Producer | Consumer(s) | Last-mod | Role |
|---|---|---|---|---|---|---|
| _(empty — only `.gitkeep`)_ | — | 0 | — | — | 2026-03-31 | **Surface declared by `intelligence-accessibility-registry.yaml` parent-model link, but never populated** — broken reference target |

### 1D. `config/ai-tools/`

| File | Format | Rows | Producer | Consumer(s) | Last-mod | Role |
|---|---|---|---|---|---|---|
| `agent-quota-latest.json` | JSON | 4 providers | hourly cron | hermes orchestrator, `provider-work-queue.json` | 2026-05-08 | Quota snapshot |
| `provider-work-queue.json` | JSON | 166 candidates | hermes router | provider-routing logic, dashboards | 2026-05-08 | Routed issue queue (touches llm-wiki indirectly through some queued issues) |
| `provider-utilization-weekly.json` | JSON | 31 KB | hermes | reporting | 2026-05-08 | Weekly per-provider utilization |
| `provider-routing-scorecard.json` | JSON | 5 KB | hermes router | provider-work-queue.json | 2026-05-08 | Scorecard |
| `provider-autolabel-candidates.json` | JSON | 14 KB | autolabeler | hermes | 2026-05-08 | Autolabel queue (refs llm-wiki issue keywords) |
| `continuous-planning-pipeline.json` | JSON | 440 KB | hermes | hermes | 2026-05-01 | Pipeline state (refs llm-wiki) |
| `weekly-utilization.json` | JSON | 5 KB | hermes | reporting | 2026-04-12 | Stale predecessor of provider-utilization-weekly |
| `agent-capability-radar.html` | HTML | 11 KB | scoring script | dashboards | 2026-05-08 | Capability radar |
| `agent-capability-scores.yaml` | YAML | 3 KB | hand-edited | none direct | 2026-03-31 | Capability scores |
| `mcp-servers.yaml`, `pricing.yaml`, `subscriptions.yaml`, `usage-tracking.yaml`, `release-scan-state.yaml`, `onet-lookup.yaml` | YAML | small | hand-edited | provider routing | various | Provider/tool metadata (not llm-wiki specific) |

> **No file under `config/ai-tools/` is llm-wiki-domain-specific** — wiki touches them only through the issue-queue routing.

### 1E. `knowledge-base/`

| File | Format | Rows | Producer | Consumer(s) | Last-mod | Role |
|---|---|---|---|---|---|---|
| `index.jsonl` | JSONL | 45 KB | `build-knowledge-index.sh` | `query-knowledge.sh`, `migrate-memory-to-knowledge.sh`, `synthesize_archive.py` | 2026-03-11 | Workspace knowledge entries (archived WRKs, decisions) |
| `wrk-completions.jsonl` | JSONL | 332 KB | `capture-wrk-summary.sh` | `query-knowledge.sh` | 2026-03-25 | Append-only WRK completion ledger |

### 1F. `llm-wiki/seeds/`

| File | Format | Rows / Keys | Producer | Consumer(s) | Last-mod | Role |
|---|---|---|---|---|---|---|
| `career-learnings.yaml` | YAML | 14 KB, ~entries[] | hand-edited | `scripts/knowledge/query-knowledge.sh --category` (declared in front-matter) | 2026-05-05 | Career-domain expertise seed → engineering wiki |
| `maritime-law-cases.yaml` | YAML | 16 KB | hand-edited | `query-knowledge.sh` (per schema header) | 2026-05-05 | Maritime-law cases → maritime-law wiki |
| `maritime-liabilities.yaml` | YAML | 11 KB | hand-edited | `query-knowledge.sh` (per schema header) | 2026-05-05 | Liabilities seed |
| `mooring-failures-lng-terminals.yaml` | YAML | 68 KB, 40 entries | hand-edited | `query-knowledge.sh --category mooring-failures` | 2026-05-05 | LNG-mooring failure seeds |
| `naval-architecture-resources.yaml` | YAML | 22 KB | hand-edited | none in tree (only schema reference) | 2026-05-05 | Naval-arch references seed |
| `schema.md` | MD | 2 KB | hand-edited | author guidance | 2026-05-05 | Seed schema spec |

### 1G. `.planning/intel/elements-to-llm-wiki/` (Elements Ingest 2026-05-01)

| File | Format | Rows | Producer | Consumer(s) | Last-mod | Role |
|---|---|---|---|---|---|---|
| `build-elements-wiki-inventory.py` | PY | 16 KB | hand-built | run once 2026-05-01 | 2026-05-01 | Producer of the entire intel pack |
| `elements-ingested-files.jsonl` | JSONL | 41,561 records, **44 MB** | the script above | none in tree | 2026-05-01 | Per-file ingest manifest (largest unconsumed asset) |
| `elements-wiki-classification.tsv` | TSV | 8 buckets | the script | wiki-ingest-report.md (read-only ref) | 2026-05-01 | Bucket classification |
| `elements-wiki-domain-summary.md` | MD | 2.8 KB | the script | _exists; called out in instruction so not re-summarized_ | 2026-05-01 | Bucket totals + per-wiki batch listing |
| `wiki-ingest-report.md` | MD | 4.2 KB | the script | _exists; called out in instruction so not re-summarized_ | 2026-05-01 | Execution report; references issues #2535/#2536 |
| `deep-extraction-candidates.tsv` | TSV | **671 records**, 190 KB | the script | **NONE** — explicitly named as the queue for #2536 but no consumer wired | 2026-05-01 | Deep-extraction work queue |
| `batches/asset-management.jsonl` | JSONL | 1 record | the script | wiki source-page (one-time) | 2026-05-01 | Per-domain Elements ingest batch |
| `batches/engineering.jsonl` | JSONL | 2 records | the script | wiki source-page (one-time) | 2026-05-01 | … |
| `batches/engineering-standards.jsonl` | JSONL | 1 record | the script | wiki source-page (one-time) | 2026-05-01 | … |
| `batches/lng-projects.jsonl` | JSONL | 2 records | the script | wiki source-page (one-time) | 2026-05-01 | … |
| `batches/marine-engineering.jsonl` | JSONL | 2 records | the script | wiki source-page (one-time) | 2026-05-01 | … |
| `wiki-validation/*.log` (15 files) | text | various | lint runs | logged once | 2026-05-01 | Per-wiki lint output (transient) |
| `repair-elements-source-frontmatter.py` | PY | 2 KB | hand-built | one-time fix | 2026-05-01 | Frontmatter repair script |

### 1H. `docs/document-intelligence/`

37 markdown files, of which the most live policy/operating docs are: `data-intelligence-map.md`, `intelligence-accessibility-map.md`, `llm-wiki-resource-doc-intelligence-operating-model.md`, `holistic-resource-intelligence.md`, `freshness-governance-contract.md`, `pyramid-conformance-checks.md`, `standards-codes-provenance-reuse-contract.md`, `durable-vs-transient-knowledge-boundary.md`, `registry-cross-reference-report.md`. These are read by humans + plan generation; **none are consumed programmatically** beyond `cross-reference-registries.py` writing into `registry-cross-reference-report.md`.

### 1I. `docs/reports/` (llm-wiki-prefixed)

| File | Last-mod | 1-line role |
|---|---|---|
| `2026-04-16-llm-wiki-resource-intelligence-unified-review.md` | 2026-04-16 | Cross-AI unified review of resource-intel surface |
| `acma-2227-metadata-only-wiki-stubs.md` | 2026-04-13 | Metadata-only wiki stub plan for #2227 |
| `acma-wiki-unblock-2245-handoff.yaml` | 2026-05-02 | Wiki-unblock handoff (#2245) |
| `engineering-wiki-skill-ingest-priority-pack.yaml` | 2026-04-14 | Priority pack for engineering wiki ingest skill (#2039–#2042) |
| `engineering-wiki-skill-ingest-readiness-2039-2042.md` | 2026-04-14 | Readiness summary for the same |
| `llm-wiki-external-source-priority-queue.md` | 2026-04-14 | Markdown twin of priority-queue.yaml |
| `llm-wiki-staged-batch-packs.md` | 2026-04-14 | Staged batch-pack plan (#2243) |

---

## 2. Orphans — Data Without Consumers

(In-tree script/skill consumer absent. Plans/reviews/reports don't count.)

1. `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv` — 671 records waiting for #2536
2. `.planning/intel/elements-to-llm-wiki/elements-ingested-files.jsonl` — 41,561 records, 44 MB
3. `.planning/intel/elements-to-llm-wiki/batches/*.jsonl` — 5 files, 8 records total (one-shot, never refreshed)
4. `data/document-index/online-resource-registry-patch-2026-05-03.yaml` — pending merge; no consumer
5. `data/document-index/llm-wiki-external-source-priority-queue.yaml` — referenced from issue plans only; no script reads it
6. `data/document-index/freshness-cadences.yaml` — `freshness-governance-contract.md` references it, but no live runner enforces the cadences
7. `data/document-index/resource-intelligence-maturity.yaml` — last refreshed 2026-04-17; tracker has no auto-refresher
8. `data/document-index/conference-index-batch.jsonl`, `conference-phase-a-results.jsonl` — phase-a outputs, no downstream
9. `data/document-index/coverage-audit.yaml`, `summary-extraction-plan.yaml`, `dde-oil-gas-codes-scan.yaml`, `dde-migration-report.yaml`, `cross-drive-dedup-report.json`, `index-other-bucket-pack-manifest.yaml`, `batch-pack-2-cross-link-candidates.jsonl` — point-in-time outputs with no readers
10. `data/document-index/marine-subdomain-tags.yaml`, `ship-plans-catalog.yaml`, `public-og-data-sources.yaml`, `engineering-refs-catalog.md` — small reference files, never wired
11. `data/document-index/enhancement-plan.yaml` (1.7 MB, 2026-03-15) — orphan, archive candidate
12. `data/document-index/index.jsonl.backup-2026-04-17` — 604 MB backup, no readers
13. `llm-wiki/seeds/naval-architecture-resources.yaml` — only the schema doc references it; not query-able
14. `config/ai-tools/agent-capability-scores.yaml`, `weekly-utilization.json` — superseded but still present

## 3. Broken References — Consumers Without Producers

1. **`config/document-intelligence/` is empty** — registry parent-model link in `intelligence-accessibility-registry.yaml` and several skills imply a configuration surface here; only `.gitkeep` exists.
2. **`intelligence-accessibility-registry.yaml` lacks rows for the 5 wiki domains created/updated by Elements ingest** (asset-management, engineering, engineering-standards, lng-projects, marine-engineering have rows for the wiki, but no row references the Elements ingest catalog as an input asset).
3. **`llm-wiki/seeds/naval-architecture-resources.yaml`** — schema and front-matter declare it queryable via `query-knowledge.sh --category naval-architecture`, but `query-knowledge.sh` does not auto-discover seeds in `llm-wiki/seeds/`; only `knowledge/seeds/` (different path) is wired. Recurrence of "llm-wiki hyphen-path pattern" smell.
4. **`freshness-governance-contract.md` declares per-asset cadences** that should drive a cron, but no scheduled job reads `freshness-cadences.yaml` to enforce them. (Compare `registry-freshness-check.py` which checks URL liveness only.)
5. **`llm-wiki-external-source-priority-queue.yaml` claims 7 upstream registry inputs**, but no script asserts these inputs are present and fresh — manual hand-edit only.
6. **`elements-ingested-files.jsonl` (44 MB) is not registered in `intelligence-accessibility-registry.yaml`** — registry has no `asset_type: ingest-manifest` entry.

## 4. Duplicate / Overlapping Coverage

- `online-resource-registry.yaml` (live) vs. `online-resource-registry-patch-2026-05-03.yaml` (pending)
- `conference-registry.yaml` vs. `conference-paper-catalog.yaml` (twins, ~95% overlap)
- `conference-index.jsonl` vs. `conference-index-batch.jsonl` vs. `conference-phase-a-results.jsonl` (three views of the same phase-a output)
- `resource-intelligence-maturity.yaml` vs. `resource-intelligence-maturity.md` (twin policy)
- `llm-wiki-external-source-priority-queue.yaml` vs. `llm-wiki-external-source-priority-queue.md` (twin)
- `dde-standards-inventory.yaml` vs. `standards-transfer-ledger.yaml` (overlap on Doris-DDE drive standards)
- `weekly-utilization.json` superseded by `provider-utilization-weekly.json`

## 5. Elements Ingest Durability Check

- **Wiki side (durable):** 8 source/catalog pages landed in 5 wiki domains under `llm-wiki/wikis/*/wiki/sources/elements-*.md`, frontmatter-validated by `repair-elements-source-frontmatter.py`, lint-clean.
- **Registry side (transient):** No row exists in `intelligence-accessibility-registry.yaml` describing the Elements ingest pipeline, the `elements-ingested-files.jsonl` index, or the `deep-extraction-candidates.tsv` queue. The 1.92 TB Elements corpus is **catalogued in `.planning/intel/`, not in `data/document-index/`**, so it sits in the transient-knowledge tier.
- **Deep-extraction queue (orphan):** 671 candidates with priority bands; no scheduler, no skill, no script picks the next item.

## 6. Top 5 Integration Gaps (with shape-of-fix)

| # | Gap | Fix shape |
|---|---|---|
| 1 | **`deep-extraction-candidates.tsv` has no consumer** — 671-row queue rots | Add a small dispatcher (e.g. `scripts/data/elements/next-extraction-candidate.py`) that pops next high-priority row, opens or updates a child issue under #2536, and updates a `status` column. Wire from `/whats-next` so candidates surface during dispatch. |
| 2 | **`config/document-intelligence/` empty** | Either populate (declare scoring weights, cadence overrides, profile defaults that `validate-accessibility-registry.py` and `cross-reference-registries.py` read) **or** drop the directory and remove parent-model references from registry headers. Currently both options are open and the empty dir confuses agents. |
| 3 | **Elements ingest invisible to registry** | Add three rows to `intelligence-accessibility-registry.yaml`: `asset_type: ingest-manifest` for `elements-ingested-files.jsonl`; `asset_type: extraction-queue` for `deep-extraction-candidates.tsv`; `asset_type: classification` for `elements-wiki-classification.tsv`. Then registry tracker / governance picks them up. |
| 4 | **`freshness-cadences.yaml` declares cadences with no enforcer** | Wire a nightly job (existing cron context: `scripts/cron/external-doc-reingest.sh`) that loads `freshness-cadences.yaml` and emits a stale-asset report into the daily-readiness issue. Eliminates the policy-without-mechanism gap that already failed once on `freshness-governance-contract.md`. |
| 5 | **`llm-wiki/seeds/` not query-able via `query-knowledge.sh`** | Patch `query-knowledge.sh` to also scan `llm-wiki/seeds/*.yaml` (currently only `knowledge/seeds/`). 5 seeds (career, mooring, maritime-law, maritime-liabilities, naval-arch) declare `query-knowledge.sh` consumption in their front-matter but only 4 of 5 actually land — naval-architecture-resources.yaml is silently dead. Path-naming hyphen pattern smell — verify with grep before fix. |

---

**End of inventory.**
