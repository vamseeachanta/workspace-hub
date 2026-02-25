# OrcaFlex .dat → Enriched YAML Pipeline (WRK-589 / WRK-595)

Converts binary OrcaFlex `.dat` model files to **enriched, client-clean YAML
test fixtures** using worldenergydata public databases (vessel fleet, riser
components, pipe schedules). All stages run on **acma-ansys05**.

## Pipeline (all on acma-ansys05)

```
Stage 1  Extract    .dat + OrcFxAPI → raw YAML
Stage 2  Enrich     raw YAML + worldenergydata → enriched YAML → client_projects/ (staging)
Stage 3  Clean      strip client names → legal scan → digitalmodel/data/orcaflex/
```

## Stage 1 — Extract

Requires OrcaFlex Python API (`pip install OrcFxAPI` with valid license on acma-ansys05).

```cmd
python scripts\data\orcaflex\dat-to-yaml.py ^
    --input "\\ace-linux-2\dde\Orcaflex\0000 Drilling Riser Development\Latest" ^
    --output "client_projects\data\raw\orcaflex-extracted\drilling-riser-development" ^
    --project drilling-riser-development
```

## Stage 2+3 — Enrich + Clean (also on acma-ansys05)

Requires `worldenergydata` installed:
```cmd
pip install -e path\to\worldenergydata
```

```cmd
# Preview
python scripts\data\orcaflex\enrich-and-clean.py ^
    --input  client_projects\data\raw\orcaflex-extracted\ ^
    --output digitalmodel\data\orcaflex\ ^
    --dry-run

# Run for real
python scripts\data\orcaflex\enrich-and-clean.py ^
    --input  client_projects\data\raw\orcaflex-extracted\ ^
    --output digitalmodel\data\orcaflex\

# Legal scan + commit
bash scripts/legal/legal-sanity-scan.sh
cd digitalmodel && git add data/orcaflex/ && git commit -m "data(orcaflex): enriched fixtures WRK-595"
```

## Enrichment Logic — Not Anonymization

The pipeline **enriches** extracted objects with public engineering data
rather than replacing names with generic labels.

### Line objects

| OrcaFlex OD (m) | worldenergydata lookup | Output `component_type` |
|-----------------|----------------------|------------------------|
| ~0.5334m (21") | `DrillingRiserLoader.filter_by_size(21.0)` | `marine_drilling_riser_joint` |
| ~0.476m (18.75") | `DrillingRiserLoader.filter_by_size(18.75)` | `marine_drilling_riser_joint` |
| ~0.2731m (10.75") | `PipelineSpecLookup.match_od_wt(...)` | `pipeline_segment` |
| other | fallback | `unknown_line` |

### Vessel objects

BSEE rig fleet (2,320 rigs, Feb 2026) provides: `vessel_class`, `water_depth_rating_m`.
Client name is stripped; vessel classified by engineering context.

### Enriched output example

```yaml
lines:
- component_type: marine_drilling_riser_joint
  nps_in: 21.0
  public_match:
    grade_range: [G105, S135]
    api_standard: API-STD-16F
    source: worldenergydata.vessel_fleet.DrillingRiserLoader
  dat_properties:       # numeric values from .dat — unchanged
    OD: [0.5334]
    WallThickness: [0.025]
    Length: [15.24, 15.24, 15.24]
    CDn: 1.0
  # name: stripped (client-specific)

vessels:
- vessel_class: drillship
  water_depth_rating_m: 3658
  public_source: worldenergydata.vessel_fleet.BSEE_rig_fleet
  dat_properties:
    InitialX: 0.0
    InitialY: 0.0
  # name: stripped
```

## worldenergydata Database Status

| Dataset | Status | WRK |
|---------|--------|-----|
| `drilling_riser_components.csv` | 24 rows (9 joints, 6 BOPs, 3 LMRPs, 4 flex, 2 telescopic) | WRK-593: expand |
| `rig_fleet_full.bin` | 2,320 rigs (99 drillships) from BSEE — Feb 2026 | ready |
| `construction_vessels.csv` | missing | WRK-593: create |
| `api_5l_pipe_schedule.csv` | missing | WRK-594: create |
| `PipelineSpecLookup` class | missing | WRK-594: implement |

## Priority Extraction Order

| Project | .dat count | Standards | Key lookup |
|---------|-----------|-----------|------------|
| `0000 Drilling Riser Dev/Latest` | 31 | DNV-OS-F201 | 21" riser joints |
| `31290 WellHead Fatigue/BOP on Wellhead` | 240 | API-RP-2A-WSD | BOPs + riser joints |
| `611 Mecor S Lay/Reference` | 3 | DNV-OS-F101 | pipeline OD match |
| `5 - OrcaFlex API Check` | 1 | — | minimal fixture |

## Scripts

| Script | Stage | Notes |
|--------|-------|-------|
| `dat-to-yaml.py` | 1 | OrcFxAPI extraction; needs OrcaFlex license |
| `enrich-and-clean.py` | 2+3 | worldenergydata enrichment + legal scan |
| ~~`anonymize-import.py`~~ | — | Superseded by enrich-and-clean.py (WRK-595) |
