# WRK-309 Implementation Plan — Document Intelligence

## Context

Thousands of engineering standards, reports, and reference documents exist across
three drives (`/mnt/ace`, `/mnt/remote/ace-linux-2/dde`, `/mnt/local-analysis`).
They are opaque to agents. This plan builds a living knowledge layer — filesystem
index → content summaries → domain classification → per-repo data-source specs —
turning static files into active context that agents can query.

Structural decisions made during planning session 2026-02-22.

---

## Repo Tier Classification (confirmed by user)

### Tier 1 — Reference Repos (foundational, maximum investment)

| Repo | Mission | Why Tier 1 |
|------|---------|-----------|
| `digitalmodel` | Offshore/subsea/marine engineering calcs | 700+ modules, 2000+ tests, PRODUCTION. All domain repos would call into it. |
| `worldenergydata` | Global energy market data aggregation | Authoritative source for energy data. Other repos consume its outputs. |
| `assetutilities` | Business automation utilities | Shared tooling across repos; common primitives. |
| `assethold` | Stock portfolio management | Production-quality daily tooling; self-contained reference for investment domain. |

### Tier 2 — Application Repos (domain-specific, consume Tier 1)

| Repo | Domain | Notes |
|------|--------|-------|
| `pdf-large-reader` | Document processing | **Review WRK needed**: may be superseded by AI agent native PDF capabilities; create WRK-NNN to assess before further investment |
| `doris` | Subsea pipeline design | Project-driven, formalisation needed |
| `OGManufacturing` | Drilling / production | Early stage, needs repo structure first |
| `acma-projects` | Structural consultancy | Document-driven, early |
| `saipem` | Umbilical installation | Project-specific, not yet portable |
| `rock-oil-field` | Offshore installation | Project-driven |
| `frontierdeepwater` | Deepwater project docs | Document repo, limited portable code |

### Tier 3 — Personal / Admin / Project (low engineering investment)

`aceengineer-admin`, `aceengineer-website`, `seanation`, `hobbies`, `teamresumes`,
`sd-work`, `sabithaandkrishnaestates`, `achantas-data`, `client_projects`

---

## Data Source Taxonomy (complete)

### Type 1 — Engineering Standards (static, reference) — PRIMARY

| Source | Location | Size | Pre-indexed? |
|--------|----------|------|-------------|
| O&G-Standards | `/mnt/ace/O&G-Standards/` | 27,343 docs, 9.55GB | **YES** — SQLite + embeddings + FTS |
| Additional standards | `/mnt/ace/docs/_standards/` | 36GB | No |
| Discipline knowledge | `/mnt/ace/docs/drilling/`, `knowledge_skills/`, `misc/` | 3.4TB | No |

### Type 2 — Project Documents (static, client-sensitive)

| Source | Location | Size | Legal Risk |
|--------|----------|------|-----------|
| Numbered project folders | `/mnt/ace/docs/0000–0200+` | Large | HIGH — client identifiers in paths |
| Source system repo | `/mnt/ace/_ss_repo/` | 193GB | HIGH |
| va-hdd-2 archive | `/mnt/ace/data/va-hdd-2/` | 883GB | HIGH — BP/2HDD project data |
| DDE archive | `/mnt/remote/ace-linux-2/dde/documents/` | ~145 folders | HIGH |
| 2H projects | `/mnt/ace/2H/` | 42MB | MEDIUM — placeholder data |

### Type 3 — Live External APIs (dynamic, per-repo)

| API | Repo | Auth | Data |
|-----|------|------|------|
| BSEE (GOM well/production) | worldenergydata | Public | Well APDs, production, platforms |
| EIA (US energy) | worldenergydata | API key | Petroleum, electricity, international |
| SODIR (Norwegian NCS) | worldenergydata | Public | Blocks, wellbores, fields |
| ANP Brazil / AER Canada / CNH Mexico | worldenergydata | Public | Country-level production |
| IMO GISIS (marine casualties) | worldenergydata | Optional | Incident reports 2010–2025 |
| ERA5 / NOAA / Open-Meteo | worldenergydata + digitalmodel | Key / Public | Metocean streaming |
| yfinance (stock prices + fundamentals) | assethold | Public | OHLCV, P/E, P/B, EV/EBITDA |
| Insider trading feed | assethold | TBD | Insider buy/sell signals |

### Type 4 — Knowledge / Intelligence Stores (derived, local)

| Store | Path | Size | Format |
|-------|------|------|--------|
| Ace knowledge index | `/mnt/ace/.ace-knowledge/index.db` | 1.2GB | SQLite |
| O&G standards inventory | `/mnt/ace/O&G-Standards/_inventory.db` | 6.4GB | SQLite + embeddings (all-MiniLM-L6-v2) |
| Document index (to build) | `data/document-index/index.jsonl` | — | JSONL, gitignored |
| Summaries (to build) | `data/document-index/summaries/` | — | JSON, gitignored |

### Type 5 — Workspace Specs & Plans (structured)

| Source | Path | Count |
|--------|------|-------|
| Module specs | `workspace-hub/specs/modules/` | 130+ |
| Repo specs | `workspace-hub/specs/repos/<repo>/` | One per submodule |
| WRK plans | `workspace-hub/specs/wrk/` | Per WRK item |
| Submodule specs/ | 20 submodules have `specs/` dirs | Varies |

### Type 6 — Submodule Data (active, varying maturity)

| Repo | data/ size | Content |
|------|-----------|---------|
| worldenergydata | 9.7GB | BSEE/USCG catalogs, energy modules |
| digitalmodel | 616KB | Fatigue tables, hull library |
| assethold | 296KB | Raw prices, processed results |

---

## Data Destinations

| Phase | Output | Path | Git | Format |
|-------|--------|------|-----|--------|
| A | Filesystem index | `data/document-index/index.jsonl` | **gitignored** | JSONL |
| B | Per-doc summaries | `data/document-index/summaries/<sha256>.json` | **gitignored** | JSON |
| C | Enhancement plan | `data/document-index/enhancement-plan.yaml` | gitignored until approved | YAML |
| D | Per-repo data sources | `specs/data-sources/<repo>.yaml` | **committed** (sanitized) | YAML |
| E | Master registry | `data/document-index/registry.yaml` | **committed** (sanitized) | YAML |
| E | Query CLI | `scripts/readiness/query-docs.sh` | committed | bash |
| F | WRK gap items | `.claude/work-queue/pending/WRK-NNN.md` | committed | Markdown |
| G | Repo-mission WRKs | `.claude/work-queue/pending/WRK-NNN.md` | committed | Markdown |

**`.gitignore` additions:**
```
data/document-index/index.jsonl
data/document-index/summaries/
data/document-index/enhancement-plan.yaml
```

---

## Phase A — Document Index (overnight batch, all sources parallel)

All source types run concurrently in a single overnight job.

### Source processing per type

**Type 1 (O&G-Standards):** Export from `_inventory.db` via SQL:
```sql
SELECT id, file_path, filename, extension, file_size, modified_date,
       content_hash, organization, doc_type, doc_number, title, is_duplicate
FROM documents
```
Emit records with `source=og_standards`, `og_db_id=<id>`, `host=ace-linux-1`.

**Type 1 (non-O&G-Standards standards):** `os.walk()` on `/mnt/ace/docs/_standards/`
with SHA256 computed on-the-fly.

**Type 2 (project docs):** `os.walk()` on `/mnt/ace/docs/`, `/mnt/ace/data/`,
`/mnt/ace/_ss_repo/`, `/mnt/remote/ace-linux-2/dde/documents/`.
Include ALL file types (CAD included, marked `is_cad=true`).
Exclude: `$RECYCLE.BIN`, `.git`, `__pycache__`, `System Volume Information`.

**Type 5 (specs):** Walk all 20 submodule `specs/` dirs + `workspace-hub/specs/`.
Include `.md`, `.yaml`, `.yml` only.

**Type 3 (API metadata):** Not a disk scan — generate from config. Each repo's API
sources are defined in `config.yaml` and emitted as structured records
(`source=api_metadata`, `repo=worldenergydata`, `api=BSEE`, etc.).

### JSONL record schema
```json
{
  "path": "/mnt/ace/O&G-Standards/DNV/...",
  "host": "ace-linux-1",
  "source": "og_standards|ace_standards|ace_project|dde_project|workspace_spec|api_metadata",
  "ext": "pdf",
  "size_mb": 1.2,
  "mtime": "2024-03-01",
  "content_hash": "sha256:abc123",
  "og_db_id": 42,
  "organization": "DNV",
  "doc_number": "RP-F103",
  "is_cad": false,
  "domain": null,
  "summary": null
}
```

### Deduplication
- Primary key: `content_hash` (SHA256, or MD5 from og-standards DB)
- Source priority for primary record: `og_standards` > `ace_standards` > `ace_project` > `dde_project`
- Duplicates: second occurrence gets `duplicate_of: <primary_path>` flag; both records retained

---

## Phase B — Content Extraction (overnight, resume-safe)

| Condition | Method |
|-----------|--------|
| `source=og_standards` | Query `document_text` table in `_inventory.db` — **no re-extraction** |
| `is_cad=true` | Write `{"type": "cad", "summary": null}` — no extraction |
| PDF, size < 100MB | `pdftotext <path> -` (subprocess) |
| PDF, size ≥ 100MB | `pdf-large-reader/src/cli.py` |
| DOCX | `python-docx` (available) |
| XLSX | `openpyxl` — headers + first 5 data rows |
| MD / TXT / YAML | Direct read, first 2000 chars |

**LLM summarisation** (after extraction, Haiku only):
- Skip if `word_count < 100` (no meaningful text)
- Skip if `source=api_metadata` (structured, not text)
- Batch size: 50 docs/call; daily budget cap configurable in `config.yaml`
- Estimated cost: ~$160 total (O&G-Standards: ~$65 via SQLite path; other docs: ~$96)
- Nightly batches at ~$20/day → ~1 week to complete non-standards sources

**Output per file** `data/document-index/summaries/<sha256>.json`:
```json
{
  "path": "...", "sha256": "...", "title": "...", "summary": "...",
  "keywords": [...], "page_count": 42, "word_count": 18000,
  "extraction_method": "og_sqlite|pdftotext|pdf_large_reader|docx|xlsx|direct",
  "extracted_at": "..."
}
```

---

## Phase C — Domain Classification (LLM, user-gated)

Domains: `structural`, `cathodic-protection`, `pipeline`, `marine`, `installation`,
`energy-economics`, `portfolio`, `materials`, `regulatory`, `cad`, `workspace-spec`, `other`

Map document → repo(s) using Tier 1 priority. Flag status:
`implemented | gap | data_source | reference`

Gate: **user review of `enhancement-plan.yaml` required before Phase D.**

---

## Phase D — Per-repo Data Source YAML (committed, legal-gated)

Focus order: Tier 1 repos first → Tier 2 repos → Tier 3 skipped.

Path sanitisation: strip client project identifiers via deny-list before writing.
`scripts/legal/legal-sanity-scan.sh` is hard gate before commit.

---

## Phase E — Linked Registry + Query CLI

`data/document-index/registry.yaml` — master registry (committed, sanitized).
Query CLI: `scripts/readiness/query-docs.sh --domain cp --repo digitalmodel`.
Quarterly cron: `scripts/cron/document-index-refresh.sh`.

---

## Phase F — WRK Gap Items

One WRK item per unimplemented standard with a located document.
Priority: Tier 1 repos first.

---

## Phase G — Repo-Mission WRK Items (18 Tier 1 items, approved)

Independent of Phases A–F. Can be created this session.

### `digitalmodel` (5 items)
| ID | Title | Standards |
|----|-------|-----------|
| G-1 | Expand S-N curve library: 17 → 20 standards | BS 7608 rev, ISO 19902, DNVGL-RP-C203 |
| G-2 | Structural module — jacket/topside analysis | API RP 2A, ISO 19902 |
| G-4 | Pipeline/flexibles module — pressure containment | DNV-ST-F101, API RP 1111 |
| G-5 | CP module — sacrificial anode design (full calcs) | DNV-RP-B401 |
| G-6 | CALM buoy mooring fatigue — spectral from OrcaFlex | DNVGL-RP-C205 |

### `worldenergydata` (6 items — includes G-3 moved from digitalmodel)
| ID | Title | Dependency |
|----|-------|-----------|
| G-3 | NDBC buoy data ingestion for metocean | NOAA NDBC API (existing client) |
| G-7 | Integrated web dashboard — Plotly Dash (BSEE + FDAS) | BSEE live API |
| G-8 | Production forecasting — Arps decline curve | Existing BSEE data |
| G-9 | Real-time EIA/IEA feed ingestion (weekly) | EIA API key |
| G-10 | MAIB + NTSB incident correlation with USCG MISLE | IMO GISIS + USCG |
| G-11 | Field development economics — MIRR/NPV + carbon cost | Internal model |

### `assethold` (4 items)
| ID | Title | Dependency |
|----|-------|-----------|
| G-12 | Fundamentals scoring — P/E, P/B, EV/EBITDA ranking | yfinance (wired) |
| G-13 | Covered call analyser — option chain + premium/yield | Options data API (TBD) |
| G-14 | Risk metrics — VaR, CVaR, Sharpe, max drawdown | Existing price data |
| G-15 | Sector exposure tracker — GICS auto-classify | yfinance fundamentals |

### Cross-repo / workspace-hub (3 items)
| ID | Title | Notes |
|----|-------|-------|
| G-16 | Unified CLI — single `ace` command routing to all repos | workspace-hub coordination |
| G-17 | Shared engineering constants library | Extract from digitalmodel |
| G-18 | Agent-readable specs index | Overlaps Phase E; create as separate WRK |

### Tier 2 Phase G items
Created as-is from WRK-309 spec (doris 4, OGManufacturing 3, saipem/rock-oil-field 2,
acma-projects 3, frontierdeepwater — defer). Total: ~12 additional items.

**+ Additional WRK item:** Review `pdf-large-reader` vs. native AI agent PDF capabilities
and decide whether to continue investment or deprecate.

---

## Script Architecture

New directory: `scripts/data/document-index/`

| Script | Phase | Description |
|--------|-------|-------------|
| `config.yaml` | All | Source paths, exclusions, batch sizes, daily budget |
| `phase-a-index.py` | A | Multi-source parallel scan → `index.jsonl` |
| `phase-b-extract.py` | B | Text extraction + Haiku summarisation → `summaries/` |
| `phase-c-classify.py` | C | LLM domain classification → `enhancement-plan.yaml` |
| `phase-d-data-sources.py` | D | Sanitized per-repo YAML → `specs/data-sources/` |
| `phase-e-registry.py` | E | Master registry + query CLI |
| `phase-f-wrk-items.py` | F | Create WRK items from document gaps |
| `phase-g-wrk-items.py` | G | Create pre-seeded repo-mission WRK items |

**Reuse (do not rewrite):**
- `scripts/data/og-standards/inventory.py` — scan loop + hash pattern
- `scripts/data/og-standards/catalog.py` — output format pattern
- `pdf-large-reader/src/cli.py` — large PDF extraction
- `scripts/legal/legal-sanity-scan.sh` — Phase D/E gate
- `scripts/work-queue/*.sh` — Phase F/G WRK item creation

---

## Legal Gates

| Phase | Gate |
|-------|------|
| A–C | None needed (all output gitignored) |
| D | **Hard gate**: `legal-sanity-scan.sh` on `specs/data-sources/` before commit |
| E | **Hard gate**: `legal-sanity-scan.sh` on `registry.yaml` before commit |

---

## Execution Order

```
Phase G → create ~30 repo-mission WRK items (this session, no data dependency)
Phase A → run overnight: parallel scan of all source types → index.jsonl
Phase B → run nightly in batches: extraction + summarisation → summaries/
Phase C → LLM classification → enhancement-plan.yaml → USER REVIEW gate
Phase D → post-review: specs/data-sources/ YAMLs + legal gate + commit
Phase E → wire registry + CLI + cron
Phase F → WRK items from document gaps
```

---

## Critical Files

**Create:**
- `scripts/data/document-index/config.yaml`
- `scripts/data/document-index/phase-a-index.py`
- `scripts/data/document-index/phase-b-extract.py`
- `scripts/data/document-index/phase-c-classify.py`
- `scripts/data/document-index/phase-d-data-sources.py`
- `scripts/data/document-index/phase-e-registry.py`
- `scripts/data/document-index/phase-f-wrk-items.py`
- `scripts/data/document-index/phase-g-wrk-items.py`
- `scripts/readiness/query-docs.sh`
- `specs/data-sources/` (directory, Phase D)
- `data/document-index/.gitkeep`

**Modify:**
- `.gitignore` — add 3 entries
- `WRK-309.md` — update percent_complete after each phase

---

## Verification

| Phase | Check |
|-------|-------|
| A | `wc -l data/document-index/index.jsonl` > 27,000 |
| A | `jq -r .source data/document-index/index.jsonl \| sort \| uniq -c` — all source types present |
| B | `ls data/document-index/summaries/ \| wc -l` ≈ non-CAD doc count |
| C | `cat data/document-index/enhancement-plan.yaml` shows domain→repo mappings |
| D | `scripts/legal/legal-sanity-scan.sh specs/data-sources/` exits 0 |
| E | `scripts/readiness/query-docs.sh --domain cp --repo digitalmodel` returns results |
| E | `scripts/legal/legal-sanity-scan.sh data/document-index/registry.yaml` exits 0 |
