---
name: orcaflex-enrichment
version: 1.0.0
description: >
  Convert OrcaFlex .dat binary model files to enriched YAML fixtures using
  worldenergydata public databases (vessel fleet, riser components, pipe schedules).
  All stages run on acma-ansys05. Output committed to digitalmodel as test fixtures.
triggers:
  - "orcaflex dat to yaml"
  - "enrich orcaflex"
  - "extract orcaflex model"
  - "orcaflex pipeline fixtures"
computer: acma-ansys05
repos: [workspace-hub, worldenergydata, digitalmodel, client_projects]
related_wrk: [WRK-589, WRK-593, WRK-594, WRK-595]
---

# OrcaFlex Enrichment Skill

Converts binary OrcaFlex `.dat` model files to **enriched, client-clean YAML
test fixtures** using worldenergydata public databases.

## Pipeline (all on acma-ansys05)

```
Stage 1  Extract    .dat + OrcFxAPI → raw YAML params
Stage 2  Enrich     raw YAML + worldenergydata lookups → enriched YAML → client_projects/
Stage 3  Clean      enriched YAML → strip client names → legal scan → digitalmodel/
```

## Stage 1 — Extract

```cmd
python scripts\data\orcaflex\dat-to-yaml.py ^
    --input "\\ace-linux-2\dde\Orcaflex\0000 Drilling Riser Development\Latest" ^
    --output "client_projects\data\raw\orcaflex-extracted\drilling-riser-development" ^
    --project drilling-riser-development
```

Extracts: `general`, `environment`, `lines[]`, `vessels[]` per .dat file.

## Stage 2 — Enrich + Stage (client_projects)

```cmd
python scripts\data\orcaflex\enrich-and-clean.py ^
    --input  client_projects\data\raw\orcaflex-extracted\ ^
    --output digitalmodel\data\orcaflex\ ^
    --dry-run
```

### Enrichment lookups performed

| Object | OrcaFlex field | worldenergydata lookup | Result field |
|--------|---------------|----------------------|--------------|
| Line | OD (m→in) | `DrillingRiserLoader.filter_by_size(od_in)` | `component_type`, `grade_range`, `api_standard` |
| Line | OD + WT | `PipelineSpecLookup.match_od_wt(od_m, wt_m)` | `nps_in`, `schedule`, `grade_range` |
| Vessel | type hint from context | BSEE rig fleet `.bin` | `vessel_class`, `water_depth_rating_m`, `dp_class` |

### Enriched YAML output example (line object)

```yaml
lines:
- component_type: marine_drilling_riser_joint
  nps_in: 21.0
  public_match:
    grade_range: [G105, S135]
    api_standard: API-STD-16F
    source: worldenergydata.vessel_fleet.DrillingRiserLoader
  dat_properties:      # numeric props from .dat — unchanged
    OD: [0.5334]
    WallThickness: [0.025]
    Length: [15.24, 15.24, 15.24]
    CDt: 0.01
    CDn: 1.0
  # name: stripped (client-specific)
```

### Enriched YAML output example (vessel object)

```yaml
vessels:
- vessel_class: drillship
  water_depth_rating_m: 3658
  dp_class: DP3
  public_source: worldenergydata.vessel_fleet.BSEE_rig_fleet
  dat_properties:
    InitialX: 0.0
    InitialY: 0.0
    InitialZ: 0.0
  # name: stripped
```

## Stage 3 — Clean + Commit

```cmd
bash scripts/legal/legal-sanity-scan.sh digitalmodel/data/orcaflex/
cd digitalmodel
git add data/orcaflex/
git commit -m "data(orcaflex): enriched fixtures from public vessel/riser databases"
```

## Priority Extraction Order

| Project | .dat count | Standards | worldenergydata lookup |
|---------|-----------|-----------|------------------------|
| `0000 Drilling Riser Dev/Latest` | 31 | DNV-OS-F201 | DrillingRiserLoader (21" joints) |
| `31290 WellHead Fatigue/BOP on Wellhead` | 240 | API-RP-2A-WSD | DrillingRiserLoader (BOP) |
| `611 Mecor S Lay/Reference` | 3 | DNV-OS-F101 | PipelineSpecLookup (pipe OD) |
| `5 - OrcaFlex API Check` | 1 | — | minimal fixture |

## worldenergydata Database Status

| Dataset | Status | Location |
|---------|--------|----------|
| `drilling_riser_components.csv` | 24 rows (partial) | `data/modules/vessel_fleet/curated/` |
| `rig_fleet_full.bin` | 2,320 rigs (Feb 2026) | `data/modules/bsee/.local/rig_fleet/` |
| `construction_vessels.csv` | missing — see WRK-593 | `data/modules/vessel_fleet/curated/` |
| `api_5l_pipe_schedule.csv` | missing — see WRK-594 | `data/modules/pipeline/` |

## Key worldenergydata API Calls

```python
from worldenergydata.vessel_fleet import DrillingRiserLoader

loader = DrillingRiserLoader()
# Match riser joint by OD
joints = loader.filter_by_size(od_in=21.0)

# Get all riser joints
all_joints = loader.get_riser_joints()

# Get BOPs
bops = loader.get_bops()
```

```python
# Pipeline spec lookup (after WRK-594)
from worldenergydata.bsee.pipeline import PipelineSpecLookup

lookup = PipelineSpecLookup()
spec = lookup.match_od_wt(od_m=0.2731, wt_m=0.012)
# → {nps_in: 10.75, schedule: "XS", grade_range: ["X60", "X65"], ...}
```

## Blocked By

- WRK-593: expand drilling_riser_components.csv + add construction_vessels.csv
- WRK-594: create api_5l_pipe_schedule.csv + PipelineSpecLookup class
