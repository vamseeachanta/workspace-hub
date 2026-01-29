# Data Organization & Enhancement Plan

## Executive Summary
This plan outlines the strategy to organize and leverage the legacy data in `/mnt/ace` to enhance the `digitalmodel` and `worldenergydata` repositories. The goal is to transform static file archives into active, structured assets for engineering validation, benchmarking, and operational analysis.

## 1. Repository Mandates

| Repository | Focus Area | Data Needs |
|------------|------------|------------|
| **digitalmodel** | Engineering Physics, Asset Lifecycle, Design & Analysis | Standards (API, DNV), FEA Models, Engineering Reports, Validation Benchmarks |
| **worldenergydata** | Energy Economics, Safety Stats, Production Operations | Production Logs, Safety Incident Reports, Field Surveillance Data, Market Data |

## 2. Data Mapping Strategy

We will use an "Index-in-Place" strategy to avoid duplicating massive files while making them accessible.

### A. Digital Model Mappings

| Source Path (`/mnt/ace/...`) | Destination Concept | Action |
|------------------------------|---------------------|--------|
| `O&G-Standards/*` | **Standards Library** | Create Index/Lookup tool in `digitalmodel`. Allow searching standards by code (e.g., "API 2RD"). |
| `docs/0110 STA EcoPetrol...` | **Mooring Benchmarks** | Ingest key OrcaFlex/sim files into `digitalmodel/benchmarks/mooring`. |
| `docs/0199 KM Drilling Riser` | **Riser Benchmarks** | Ingest Riser analysis files for `digitalmodel/benchmarks/riser`. |
| `docs/0116 Thinwall Pipe...` | **FEA Validation** | Use Abaqus/Ansys files to validate `digitalmodel` structural modules. |
| `data/fatigue/*` (if exists) | **Fatigue Database** | Continue populating `digitalmodel/data/fatigue`. |

### B. World Energy Data Mappings

| Source Path (`/mnt/ace/...`) | Destination Concept | Action |
|------------------------------|---------------------|--------|
| `Production/` | **Production Dashboard** | ETL pipelines to read field reports/PPTs and extract key metrics. |
| `docs/disciplines/integrity_management` | **Safety Analysis** | Feed incident reports into `worldenergydata`'s Marine Safety module. |
| `docs/disciplines/production` | **Forecasting** | Use historical production data to train forecasting models. |

## 3. Implementation Steps

### Phase 1: Infrastructure Setup (Immediate)
1.  **Digital Model**:
    *   Create `digitalmodel/data/standards`.
    *   Create `digitalmodel/benchmarks/legacy_projects`.
2.  **World Energy Data**:
    *   Create `worldenergydata/data/raw/legacy_production`.
    *   Create `worldenergydata/data/raw/legacy_safety`.

### Phase 2: Indexing Script
Develop a Python script (`/mnt/ace/scripts/index_assets.py`) to crawl `/mnt/ace` and generate a `assets.json` manifest.
*   **Metadata**: File path, Size, Modified Date, Likely Type (FEA Model, Report, Standard).
*   **Tags**: "Mooring", "Riser", "Fatigue", "Safety".

### Phase 3: Targeted Ingestion (Pilot)
1.  **Standards**: Link `digitalmodel` to `O&G-Standards` via the manifest.
2.  **Benchmark**: Select *one* high-quality project (e.g., `0110 STA EcoPetrol`) and write a script to run `digitalmodel`'s mooring analysis using its inputs, comparing results to the legacy report.

## 4. Proposed Directory Structure Enhancements

### digitalmodel
```text
digitalmodel/
├── data/
│   ├── standards/          # JSON index referencing /mnt/ace/O&G-Standards
│   ├── fatigue/            # Existing S-N curves
│   └── materials/          # New: Material properties extracted from legacy reports
├── benchmarks/
│   ├── mooring/
│   │   └── ecopetrol_benchmark/  # Inputs extracted from legacy project
│   └── riser/
```

### worldenergydata
```text
worldenergydata/
├── data/
│   ├── modules/
│   │   ├── marine_safety/
│   │   │   └── input/      # Symlinks to relevant /mnt/ace/docs/integrity files
│   │   └── production/
│   │       └── history/    # Aggregated production history from /mnt/ace/Production
```

## 5. Approval & Next Actions
*   **Review**: Confirm if this separation (Engineering vs. Operations) aligns with your vision.
*   **Action**: Upon approval, I will begin by creating the "Standards Index" for `digitalmodel`.
