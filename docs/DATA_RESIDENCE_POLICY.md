# Data Residence Policy

> **ADR-004** | Last Updated: 2026-02-08

Canonical policy for data governance across all repositories in the workspace-hub. Every dataset must belong to exactly one tier. When in doubt, apply the Boundary Test.

---

## Three-Tier Data Model

| Tier | Name | Owner Repo | Description |
|------|------|------------|-------------|
| 1 | Collection Data | `worldenergydata` | Raw data collected from external public sources via APIs, web scraping, or downloads |
| 2 | Engineering Reference Data | `digitalmodel` | Industry standard lookup tables, material properties, and design code parameters consumed by engineering analysis |
| 3 | Project Data | `rock-oil-field`, `client_projects` | Project-specific configurations, analysis inputs/outputs, and client deliverables |

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

### Tier 3 — Project Data (project repos)

Project-specific configurations, analysis inputs/outputs, and client deliverables. Never stored in `worldenergydata` or `digitalmodel`. Always in the project repo (`rock-oil-field`, `client_projects`, or equivalent).

---

## Boundary Test

Ask: **"Where did this data originate?"**

| Origin | Tier | Owner |
|--------|------|-------|
| Public API, website, or database | Tier 1 | `worldenergydata` |
| Engineering standard (DNV-RP-C203, API 2A, BS 7608) | Tier 2 | `digitalmodel` |
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

### The Decision Tree

For every data file, ask: **"Can this be regenerated from a pipeline?"**

```
Is the file regenerable from a pipeline/acquirer script?
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
| **Engineering reference data** | Always | Normal git | SN curves YAML, steel grades YAML (<1MB) |
| **Curated/filtered datasets** | If <10MB | Normal git | Filtered oil & gas safety records |
| **Curated datasets 10-100MB** | Yes | Git LFS | Processed BSEE production summaries |
| **Raw API downloads** | Never | .gitignore | OSHA CSVs (6.6GB), EPA TRI bulk data |
| **ZIP archives of raw data** | Never | .gitignore | `osha_inspection_20260201.csv.zip` |
| **Analysis outputs/reports** | Never | .gitignore | Generated HTML reports, plots |
| **Binary data files** | If needed | Git LFS | `.bin` conversion files |

### Regeneration Documentation

Every `.gitignore`'d data directory MUST contain a `README.md` with:

1. **Source**: URL or API endpoint where data originates
2. **Command**: Exact command to regenerate (`uv run python -m ...`)
3. **Expected output**: File list and approximate sizes
4. **Last known good**: Date of last successful acquisition
5. **Dependencies**: Any API keys, rate limits, or access requirements

### Size Thresholds

| Threshold | Action |
|-----------|--------|
| < 10 MB | Commit to git normally |
| 10–100 MB | Use Git LFS (configure in `.gitattributes`) |
| > 100 MB | Never commit. `.gitignore` + pipeline regeneration |

### Pre-Commit Guard

Repos should configure a pre-commit hook or CI check that blocks commits containing files > 50MB that are not tracked by Git LFS. This prevents accidental large data commits.
