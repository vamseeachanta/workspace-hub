# LLM-Wiki Staged Batch Packs

> **Issue:** [#2243](https://github.com/vamseeachanta/workspace-hub/issues/2243)
> **Queue dependency:** [#2242](https://github.com/vamseeachanta/workspace-hub/issues/2242)
> **Parent umbrella:** [#2241](https://github.com/vamseeachanta/workspace-hub/issues/2241)
> **Queue artifact:** `data/document-index/llm-wiki-external-source-priority-queue.yaml`
> **Date:** 2026-04-14

---

## 1. Purpose

This document defines reusable staged execution packs for LLM-wiki strengthening. Each batch pack is a self-contained agent execution slice derived from the priority queue (#2242). Packs are designed for bounded, low-contention runs that minimize token waste and git conflicts.

## 2. Batch Pack Structure Template

Every batch pack follows this structure:

```yaml
batch_pack:
  id: batch-pack-N
  name: "descriptive name"
  source_family: family_id from priority queue
  promotion_mode: metadata-first | summary-backed | raw-extraction
  target_wiki_domains: [list]
  
  scope:
    source_registry: path to source YAML/JSONL
    source_filter: filter expression
    entry_count: approximate entries to process
  
  paths:
    owned: [paths agent may write to]
    read_only: [paths agent may read but not write]
    forbidden: [paths agent must not touch]
  
  verification:
    pre_run: [checks before starting]
    post_run: [checks after completion]
    acceptance: [criteria for declaring success]
  
  return_format:
    primary_output: description of main deliverable
    secondary_outputs: [additional artifacts]
    issue_comment: whether to post summary to GitHub issue
  
  execution:
    overnight_safe: true | false | conditional
    estimated_token_cost: low | medium | high
    max_duration_minutes: number
    contention_risk: low | medium | high
    follow_on_issue_rule: when to create child issues
```

## 3. Batch Pack Definitions

---

### Batch Pack 1: Online API & Standards Portal Metadata Sweep

**Priority queue family:** `online-data-apis-and-portals` (P1)
**Promotion mode:** metadata-first
**Overnight safe:** Yes

#### Scope

| Parameter | Value |
|---|---|
| Source registry | `data/document-index/online-resource-registry.yaml` |
| Source filter | `type in [data_api, standard_portal]` |
| Entry count | 40 |
| Target wiki domains | engineering, marine-engineering, naval-architecture |

#### Paths

| Category | Paths |
|---|---|
| **Owned** (may write) | `data/document-index/**`, `docs/reports/**` |
| **Read-only** | `knowledge/wikis/**`, `docs/document-intelligence/**` |
| **Forbidden** | `config/**`, `.claude/**`, `tests/**`, `scripts/**` |

#### Input Data

The agent reads each entry's `notes` field from the online resource registry. These notes already contain structured capability summaries (API endpoints, data coverage, access methods, licensing). No network access or source downloading is required.

#### Processing Steps

1. Read `online-resource-registry.yaml` and filter for `type in [data_api, standard_portal]`
2. For each entry, extract from `notes`:
   - Capability summary (what data/standards it provides)
   - Access method (API, portal navigation, download)
   - Domain relevance (which engineering domains it serves)
   - Licensing/access restrictions
3. Group entries by target wiki domain
4. Generate wiki-ready metadata stubs per entry
5. Produce a batch output report with cross-references to existing wiki pages

#### Verification

| Check | Command / Method |
|---|---|
| **Pre-run:** registry file exists | `test -f data/document-index/online-resource-registry.yaml` |
| **Pre-run:** filter returns expected count | `yq '.entries[] | select(.type == "data_api" or .type == "standard_portal")' \| wc -l` |
| **Post-run:** output YAML parses | `python3 -c "import yaml; yaml.safe_load(open('output.yaml'))"` |
| **Post-run:** no entries without domain mapping | check all stubs have `target_wiki_domain` assigned |
| **Post-run:** no duplicate entries | check output IDs are unique |
| **Acceptance:** all 40 entries processed | count of output stubs = 40 |

#### Return Format

- **Primary output:** `docs/reports/batch-pack-1-api-portal-metadata-stubs.md` — wiki-ready metadata stubs grouped by domain
- **Secondary outputs:** enriched entries appended to queue artifact with `processed: true` flag
- **Issue comment:** Post summary to #2242 with count of stubs generated per domain

#### Execution Constraints

| Constraint | Value |
|---|---|
| Estimated token cost | Low (~50k tokens) |
| Max duration | 30 minutes |
| Contention risk | Low — no shared write paths with other wiki work |
| Follow-on issues | Create child issue if any entry has insufficient notes for stub generation |

#### Related Issues

- #1609 — download pipeline (for entries needing actual data download)
- #2039 — engineering wiki ingest (upstream consumer of stubs)
- #2067 — wire research into wiki ingest

---

### Batch Pack 2: Indexed Conference Paper Summary Promotion

**Priority queue family:** `indexed-conference-papers` (P1)
**Promotion mode:** summary-backed
**Overnight safe:** Yes

#### Scope

| Parameter | Value |
|---|---|
| Source registry | `data/document-index/conference-paper-catalog.yaml` |
| Source filter | `indexing_status = phase_a_complete` (DOT, OMAE, ISOPE) |
| Entry count | 3 collections, ~18,000 PDFs (process by collection) |
| Target wiki domains | marine-engineering, naval-architecture, engineering |

#### Paths

| Category | Paths |
|---|---|
| **Owned** (may write) | `data/document-index/**`, `docs/reports/**`, `docs/document-intelligence/**` |
| **Read-only** | `knowledge/wikis/**`, `/mnt/ace/docs/conferences/**` (mounted source) |
| **Forbidden** | `config/**`, `.claude/**`, `tests/**` |

#### Input Data

The agent reads existing phase_a indexing outputs:
- `data/document-index/conference-index-batch.jsonl` — batch processing results
- `data/document-index/conference-phase-a-results.jsonl` — phase A classification results
- `data/document-index/conference-index-stats.yaml` — collection statistics
- `data/document-index/conference-index-manifest.json` — processing manifest

No re-reading of source PDFs is required. All title/abstract/domain data comes from existing indexed outputs.

#### Processing Steps

1. Read phase_a outputs for DOT, OMAE, and ISOPE collections
2. Group indexed papers by engineering domain (subsea, structural, marine, pipeline, VIV, hydrodynamics)
3. For each domain group:
   a. Identify the top papers by relevance/citation indicators
   b. Generate wiki topic summary stubs (one per major topic cluster)
   c. Generate cross-link candidates between conferences and existing wiki pages
4. Produce domain-organized batch output with provenance references

#### Sub-slicing for Overnight Runs

This pack should be sub-sliced by collection to stay within single-run bounds:

| Sub-slice | Collection | PDFs | Estimated Tokens |
|---|---|---:|---|
| 2a | DOT | 1,456 | ~150k |
| 2b | OMAE | 7,292 | ~300k |
| 2c | ISOPE | 4,074 | ~200k |

Run one sub-slice per overnight session.

#### Verification

| Check | Command / Method |
|---|---|
| **Pre-run:** indexed data exists | `test -f data/document-index/conference-phase-a-results.jsonl` |
| **Pre-run:** mount is available (if reading source for sampling) | `test -d /mnt/ace/docs/conferences/DOT` |
| **Post-run:** stubs reference valid conference registry entries | cross-check IDs against `conference-registry.yaml` |
| **Post-run:** domain tags are valid | check against `marine-subdomain-tags.yaml` |
| **Post-run:** no orphan cross-links | all linked wiki pages exist |
| **Acceptance:** per-collection output report generated | one report per sub-slice |

#### Return Format

- **Primary output:** `docs/reports/batch-pack-2-conference-summary-stubs.md` — domain-organized topic stubs
- **Secondary outputs:** cross-link candidates for #2068, updated processing manifest
- **Issue comment:** Post summary to #2242 and #2068 with topic cluster counts

#### Execution Constraints

| Constraint | Value |
|---|---|
| Estimated token cost | Medium (~150-300k tokens per sub-slice) |
| Max duration | 60 minutes per sub-slice |
| Contention risk | Low — reads indexed data, writes to reports only |
| Follow-on issues | Create child issue for any collection needing re-indexing |

#### Related Issues

- #2001 — batch ingest precedent (methodology reference)
- #2039, #2067 — engineering wiki ingest consumers
- #2068 — cross-link JSONL package

---

### Batch Pack 3: Online GitHub/Tool Repo README Extraction

**Priority queue family:** `online-github-repos-and-tools` (P2)
**Promotion mode:** metadata-first
**Overnight safe:** Conditional (requires network access for GitHub API)

#### Scope

| Parameter | Value |
|---|---|
| Source registry | `data/document-index/online-resource-registry.yaml` |
| Source filter | `type in [github_repo, tool]` |
| Entry count | 153 |
| Target wiki domains | engineering, marine-engineering |

#### Paths

| Category | Paths |
|---|---|
| **Owned** (may write) | `data/document-index/**`, `docs/reports/**` |
| **Read-only** | `knowledge/wikis/**` |
| **Forbidden** | `config/**`, `.claude/**`, `tests/**`, `scripts/**` |

#### Input Data

Two-tier approach:
1. **Tier A (offline):** Entries with sufficient `notes` in the registry (majority) — process from existing metadata
2. **Tier B (online):** Entries with minimal notes — requires GitHub API or web scraping for README content

#### Processing Steps

1. Read `online-resource-registry.yaml` and filter for `type in [github_repo, tool]`
2. Classify entries into Tier A (rich notes) vs Tier B (needs scraping)
3. **Tier A processing:**
   a. Extract tool name, domain, capabilities, license, installation method from notes
   b. Generate wiki tool-profile stubs
4. **Tier B processing (network required):**
   a. Fetch README from GitHub API (`gh api repos/{owner}/{repo}/readme`)
   b. Extract capabilities, installation, and domain relevance
   c. Generate wiki tool-profile stubs
5. Merge outputs and group by target wiki domain

#### Sub-slicing by Domain

| Sub-slice | Domain | Entries | Network Needed |
|---|---|---:|---|
| 3a | cad (CadQuery, Gmsh, NGSolve, etc.) | ~20 | Partial |
| 3b | hydrodynamics (wavespectra, OpenFOAM, etc.) | ~30 | Partial |
| 3c | data_science + general | ~40 | Partial |
| 3d | remaining domains | ~63 | Partial |

#### Verification

| Check | Command / Method |
|---|---|
| **Pre-run:** registry file exists | `test -f data/document-index/online-resource-registry.yaml` |
| **Pre-run:** GitHub CLI authenticated (for Tier B) | `gh auth status` |
| **Post-run:** each stub has source URL | check all stubs have `url` field |
| **Post-run:** each stub has domain assignment | check all stubs have `target_wiki_domain` |
| **Post-run:** no duplicate tool profiles | check output IDs unique |
| **Acceptance:** Tier A entries all processed; Tier B attempted | count matches expected |

#### Return Format

- **Primary output:** `docs/reports/batch-pack-3-tool-profile-stubs.md` — wiki-ready tool profiles grouped by domain
- **Secondary outputs:** list of Tier B entries that failed scraping (for manual follow-up)
- **Issue comment:** Post summary to #2242 with counts per domain

#### Execution Constraints

| Constraint | Value |
|---|---|
| Estimated token cost | Low-medium (~100k tokens) |
| Max duration | 45 minutes |
| Contention risk | Low |
| Network requirement | GitHub API for Tier B entries |
| Follow-on issues | Create issue for Tier B entries that fail automated extraction |

#### Related Issues

- #2039 — engineering wiki ingest
- #2042 — skill metadata as wiki pages (related approach)

---

### Batch Pack 4: Standards Summary Domain-by-Domain Promotion

**Priority queue family:** `standards-with-existing-summaries` (P1)
**Promotion mode:** summary-backed
**Overnight safe:** Yes

#### Scope

| Parameter | Value |
|---|---|
| Source registry | `data/document-index/resource-intelligence-maturity.yaml` |
| Source data | Document index shards with existing summaries |
| Entry count | ~639,000 summaries across 10 domains |
| Target wiki domains | engineering, marine-engineering |

#### Paths

| Category | Paths |
|---|---|
| **Owned** (may write) | `data/document-index/**`, `docs/reports/**` |
| **Read-only** | `knowledge/wikis/**`, `data/document-index/shards/**` |
| **Forbidden** | `config/**`, `.claude/**`, `tests/**`, `/mnt/ace/**` (do not read source PDFs) |

#### Input Data

The agent reads existing summaries from document index shards:
- `data/document-index/shards/shard-00.json` through `shard-09.json`
- `data/document-index/shards/ace-shard-00.json` through `ace-shard-09.json`
- Cross-reference with `data/document-index/standards-transfer-ledger.yaml` for provenance

No source PDF reading. All data comes from pre-existing indexed summaries.

#### Sub-slicing by Standards Domain

| Sub-slice | Domain | Priority | Existing Calc Coverage |
|---|---|---|---|
| 4a | cathodic-protection | High | 47.4% |
| 4b | pipeline | High | 21.8% |
| 4c | structural | High | 5.6% |
| 4d | marine | High | 12.1% |
| 4e | process | Medium | 0% (new domain, 55 standards) |
| 4f | drilling | Medium | 0% (new domain, 9 standards) |
| 4g-j | remaining domains | Low | varies |

Run 1-2 sub-slices per overnight session, prioritizing domains with highest gap severity in target wikis.

#### Processing Steps

1. For each domain sub-slice:
   a. Query index shards for entries in that domain with existing summaries
   b. Cluster entries by topic (e.g., within pipeline: design, inspection, corrosion, materials)
   c. Generate wiki-ready topic stubs from summary clusters
   d. Add provenance links to standards-transfer-ledger entries
2. Cross-reference with existing wiki pages to avoid duplicates
3. Produce domain-organized output report

#### Verification

| Check | Command / Method |
|---|---|
| **Pre-run:** index shards exist | `ls data/document-index/shards/*.json \| wc -l` |
| **Post-run:** stubs reference valid shard entries | spot-check 10% of provenance links |
| **Post-run:** no duplicate topics | check for topic name collisions across domains |
| **Acceptance:** domain report covers all entries with summaries | summary count matches shard query |

#### Return Format

- **Primary output:** `docs/reports/batch-pack-4-standards-summary-stubs-{domain}.md` — per-domain topic stubs
- **Secondary outputs:** updated maturity tracker with promoted counts
- **Issue comment:** Post domain progress to #2242

#### Execution Constraints

| Constraint | Value |
|---|---|
| Estimated token cost | Low per sub-slice (~50-100k tokens) |
| Max duration | 45 minutes per domain sub-slice |
| Contention risk | Low — reads shards, writes to reports only |
| Follow-on issues | Create issue for domains needing deeper extraction |

#### Related Issues

- #2216 — ACMA integration (related standards work)
- #2207 — provenance/reuse contract
- #2039 — engineering wiki ingest

---

## 4. Cross-Cutting Execution Rules

### 4.1 Token Efficiency

1. **Never re-read source documents** when summaries exist in the index
2. **Process offline data first** (Tier A) before attempting network operations (Tier B)
3. **Batch by domain** to reuse domain context across entries
4. **Stop early** if token budget is exceeded — produce partial output rather than over-spending

### 4.2 Git Contention Prevention

1. Each batch pack writes to its own output file — no shared write targets between packs
2. Pack execution order follows the priority queue — P1 before P2
3. Different packs never run concurrently on the same worktree
4. Output files use the pattern `batch-pack-N-*.md` for easy identification

### 4.3 Follow-On Issue Protocol

Create a new child issue under #2241 when:
- A source entry requires data that doesn't exist in any registry
- A promoted stub reveals a gap that needs dedicated research
- An entire source family needs a dedicated extraction pipeline
- More than 10% of entries in a batch fail automated processing

Do NOT create follow-on issues for:
- Individual entries that need minor metadata enrichment (batch these)
- Sources already covered by an existing open issue
- Sources on the do-not-process-yet list (these are intentionally deferred)

### 4.4 Overnight Execution Checklist

Before launching any batch pack for overnight unattended execution:

- [ ] Correct worktree checked out and clean (`git status` shows no unexpected changes)
- [ ] Source registries are up-to-date (`git pull` if needed)
- [ ] Mount dependencies are available (run `test -d <mount_path>` for each)
- [ ] Network is available (for Tier B / conditional packs only)
- [ ] No other agent session is writing to the same owned paths
- [ ] Previous batch pack output has been committed (avoid stale conflicts)

### 4.5 Batch Output Validation Sequence

After every batch pack run:

```bash
# 1. Check YAML output parses
python3 -c "import yaml; yaml.safe_load(open('output.yaml'))" 2>&1

# 2. Verify only owned paths were modified
git diff --name-only | grep -v -E '^(data/document-index/|docs/reports/|docs/document-intelligence/)' && echo "WARN: unexpected paths modified"

# 3. Count output stubs
grep -c '##' docs/reports/batch-pack-*.md

# 4. Check for orphan references
# (manual spot-check of 5 random cross-references)
```

## 5. Execution Summary Matrix

| Pack | Family | Priority | Promotion | Overnight | Est. Tokens | Sub-slices |
|---|---|---|---|---|---|---|
| **1** | Online APIs & Portals | P1 | metadata-first | Yes | ~50k | 1 |
| **2** | Indexed Conferences | P1 | summary-backed | Yes | ~650k total | 3 (DOT/OMAE/ISOPE) |
| **3** | GitHub Repos & Tools | P2 | metadata-first | Conditional | ~100k | 4 (by domain) |
| **4** | Standards Summaries | P1 | summary-backed | Yes | ~500k total | 6-10 (by domain) |

Total estimated cost for all 4 packs: ~1.3M tokens across 14-18 sub-slices.
