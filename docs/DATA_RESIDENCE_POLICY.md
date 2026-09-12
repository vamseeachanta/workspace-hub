# Data Residence Policy

> **ADR-004** | Last Updated: 2026-02-08

Canonical policy for data governance across all repositories in the workspace-hub. Every dataset must belong to exactly one tier. When in doubt, apply the Boundary Test.

**2026-09-08 operational clarification:** apply [the all-agent data handling contract](architecture/agent-data-handling-contract.md) for source discovery, knowledge-vs-computational ownership, manifests and retrieval. The tier owner identifies collection/engineering/project responsibility; storage and redistribution still follow source rights and the later layer contracts. Vendor-licensed standards originals stay outside Git; client-supplied and measured originals stay in their owning private repository under the required-original exception below, llm-wiki owns source interpretation and authorized knowledge, and digitalmodel consumes source-qualified engineering artifacts. An external origin does not move every downstream derivative into the raw-collection tier.

---

## Three-Tier Data Model

| Tier | Name | Owner Repo | Description |
|------|------|------------|-------------|
| 1 | Collection Data | `worldenergydata` | Raw data collected from external public sources via APIs, web scraping, or downloads |
| 2 | Engineering Reference Data | `digitalmodel` | Industry standard lookup tables, material properties, and design code parameters consumed by engineering analysis |
| 3 | Project Data | `client-b`, `client-c` | Project-specific configurations, analysis inputs/outputs, and client deliverables |

### Tier 1 — Collection Data (`worldenergydata`)

Raw data collected from external public sources. If the data comes from an external public source, `worldenergydata` owns it.

**Examples:**

- BSEE well and production data
- SODIR field data
- MarineTraffic vessel specifications
- NDBC metocean data
- Marine safety incidents
- Oil prices
- LNG terminal data
- Vessel hull geometry (OBJ from CAD exports, OrcaWave)

### Tier 2 — Engineering Reference Data (`digitalmodel`)

Industry standard lookup tables, material properties, and design code parameters consumed by engineering analysis. If the data comes from an engineering standard/code or is a lookup table for analysis, `digitalmodel` owns it.

**Examples:**

| Category | Sources / Standards |
|----------|-------------------|
| SN curves | DNV-RP-C203, API RP 2A, BS 7608, AWS D1.1 |
| Steel material grades | API 5L, ASTM A106 |
| OCIMF coefficients | OCIMF mooring equipment guidelines |
| Hydrodynamic coefficients | Industry reference tables |
| Equipment specifications | Vendor-neutral reference data |
| Pipe capacity tables | Design code tables |

### Tier 2a — Research Literature (`/mnt/ace-data/digitalmodel/docs/domains/`)

Downloaded academic papers, conference proceedings, ITTC guidelines, classification society rules, and textbooks used as reference material for engineering analysis. Organized by domain (hydrodynamics, naval_architecture, pipeline, etc.) with per-domain `download-literature.sh` scripts for reproducible acquisition.

Acquisition and retention require source-specific rights evidence; a download script
is not permission. Vendor-licensed or copyrighted items require a `sources:`
reference, edition and authorized-access record for the permitted location.
Unknown rights block acquisition/retention decisions. Historical path examples
below do not establish a current licensed location or authorize bulk downloads.

**Not committed to git** — stored on local drive (`/mnt/ace` on ace-linux-1). Each domain folder contains a download script that documents provenance.

**Examples:**
- ITTC resistance/propulsion guidelines
- Holtrop-Mennen 1982 power prediction paper
- DNV-RP-C205 environmental conditions
- Barrass & Derrett ship stability textbook
- LR classification rules

### Tier 3 — Project Data (project repos)

Project-specific configurations, analysis inputs/outputs, and client deliverables. Never stored in `worldenergydata` or `digitalmodel`. Always in the project repo (`client-b`, `client-c`, or equivalent).

---

## Boundary Test

Ask: **"Where did this data originate?"**

| Origin | Tier | Owner |
|--------|------|-------|
| Public API, website, or database | Tier 1 | `worldenergydata` |
| Engineering standard (DNV-RP-C203, API 2A, BS 7608) | Tier 2 | `digitalmodel` |
| Research paper, textbook, ITTC guideline | Tier 2a | `/mnt/ace-data/digitalmodel/docs/domains/` |
| Specific project or client | Tier 3 | Project repo |

---

## Handoff Contract: `worldenergydata` → `digitalmodel`

1. `digitalmodel` declares external data dependencies in `config/data_sources.yaml`.
2. Access is **read-only and path-based**. No copying data between repos.
3. If `worldenergydata` is unavailable (standalone use), `digitalmodel` gracefully degrades with a clear error.
4. `worldenergydata` **must not** reference `digitalmodel` as a data source. No circular dependencies.

---

## Specific Decisions

| Dataset | Tier | Owner | Rationale |
|---------|------|-------|-----------|
| Vessel hull geometry | 1 | `worldenergydata` | Collection data sourced from CAD exports and OrcaWave |
| SN curves | 2 | `digitalmodel` | Engineering standard data, externalized from code to YAML |
| Material properties | 2 | `digitalmodel` | Engineering reference lookup tables |
| Vessel engineering databases (FPSO, rigs) | 2 | `digitalmodel` | Curated reference data for engineering analysis |
| Hydrodynamic coefficients | 2 | `digitalmodel` | Industry reference tables for analysis |

---

## Data Directory Conventions

| Repo | Directory Structure | Example |
|------|-------------------|---------|
| `worldenergydata` | `data/modules/<domain>/` | `data/modules/bsee/`, `data/modules/vessel_hull_models/` |
| `digitalmodel` | `data/<domain>/` | `data/fatigue/`, `data/materials/` |

External dependencies are declared in `config/data_sources.yaml` within the consuming repository.

---

## Git Commit Strategy for Data Files

### Required-original exception (evaluate first)

Client-supplied and measured originals shall be retained in the owning private repository under `data/<dataset>/raw/`, beside extracts, with SHA-256 manifest entries and narrow `.gitignore` exceptions. Regeneration, ZIP packaging and file size do not remove this evidence requirement. Vendor-licensed standards originals shall never be committed, even privately; retain authorized `sources:` references at their licensed location. Derived artifacts require source-specific rights independently of private visibility.

If rights, terms or storage limits prevent required private retention, ingest acceptance remains blocked pending an explicit owner decision. An external path alone is not retained evidence. No silent off-repo substitution or weakening of the licensed-original exclusion is permitted. See [the authority contract](architecture/agent-data-handling-contract.md).

### The Decision Tree

After the required-original exception above, for other data files ask: **"Can this be regenerated from a pipeline?"**

```
Required original? Apply the required-original exception above before this tree.
Otherwise, is the file regenerable from a pipeline/acquirer script?
├── YES → Do NOT commit. Add to .gitignore. Commit only the pipeline script + config.
│         Document regeneration command in a README.
└── NO → Is the file < 10 MB?
          ├── YES → Commit to git (normal).
          └── NO → Is the file < 100 MB?
                    ├── YES → Use Git LFS.
                    └── NO → Do NOT commit. Use external storage or .gitignore.
                              Document the data source and retrieval instructions.
```

### What to Commit vs. What to Exclude

| Category | Commit? | Method | Examples |
|----------|---------|--------|----------|
| **Pipeline scripts & configs** | Always | Normal git | `osha_acquirer.py`, `download_osha_data.sh` |
| **Engineering reference data** | Only where source-specific rights permit | Normal git | SN curves YAML, steel grades YAML (<1MB) |
| **Curated/filtered datasets** | If <10MB | Normal git | Filtered oil & gas safety records |
| **Curated datasets 10-100MB** | Yes | Git LFS | Processed BSEE production summaries |
| **Raw API downloads outside the required-original exception** | Never | .gitignore | OSHA CSVs (6.6GB), EPA TRI bulk data |
| **ZIP archives outside the required-original exception** | Never | .gitignore | `osha_inspection_20260201.csv.zip` |
| **Regenerable analysis outputs/reports outside issued-evidence requirements** | Normally exclude | .gitignore | Generated HTML reports, plots |
| **Binary data files** | If needed | Git LFS | `.bin` conversion files |

### Regeneration Documentation

Every `.gitignore`'d data directory MUST contain a `README.md` with:

1. **Source**: URL or API endpoint where data originates
2. **Command**: Exact command to regenerate (`uv run python -m ...`)
3. **Expected output**: File list and approximate sizes
4. **Last known good**: Date of last successful acquisition
5. **Dependencies**: Any API keys, rate limits, or access requirements

### Size Thresholds

These thresholds apply after the required-original exception; a storage conflict for required originals blocks ingest acceptance rather than changing ownership or permitting evidence loss.

| Threshold | Action |
|-----------|--------|
| < 10 MB | Commit to git normally |
| 10–100 MB | Use Git LFS (configure in `.gitattributes`) |
| > 100 MB | Never commit. `.gitignore` + pipeline regeneration |

### Pre-Commit Guard

Repos should configure a pre-commit hook or CI check that blocks commits containing files > 50MB that are not tracked by Git LFS. This prevents accidental large data commits.

---

## Generated Data — Physical Placement Map

Pipeline-generated artifacts outside the required-original exception that exceed git thresholds live on the ace NFS drive. Scripts use `$SUMMARIES_DIR` env var or read from `config.yaml` to resolve paths.

| Artifact | Ace Drive Path | Generator Script | Notes |
|----------|---------------|-----------------|-------|
| Document summaries (Phase B) | `/mnt/remote/ace-linux-1/ace/data/document-index/summaries/` | `phase-b-claude-worker.py`, `summarise-worker.py` | ~155MB, thousands of JSON files |
| Document index | In-repo: `data/document-index/index.jsonl` | `phase-b-extract.py` | Lightweight ledger, committed |
| Standards inventory DB | `/mnt/ace/O&G-Standards/_inventory.db` | External | SQLite, read-only from scripts |
| Research literature | `/mnt/ace/docs/domains/<domain>/literature/` | Per-domain `download-literature.sh` | Tier 2a |

### Path Resolution Convention

Scripts should resolve generated-data paths in this order:
1. **Env var** (`$SUMMARIES_DIR`) — for CI or cross-machine overrides
2. **Config file** (`config.yaml` → `output.summaries_dir`) — for pipeline scripts
3. **Default** (`/mnt/remote/ace-linux-1/ace/data/document-index/summaries`) — hardcoded fallback
