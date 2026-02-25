# OrcaFlex .dat → YAML Pipeline (WRK-589)

Converts binary OrcaFlex `.dat` model files to portable YAML test fixtures
for use in `digitalmodel`.

## Pipeline Overview

```
Stage 1  acma-ansys05  .dat → OrcFxAPI extract → raw YAML → client_projects staging
Stage 2  ace-linux-1   raw YAML → anonymize string fields → legal scan
Stage 3  ace-linux-1   clean YAML → digitalmodel/data/orcaflex/
```

## Stage 1 — Extraction (acma-ansys05, Windows)

Requires OrcaFlex Python API (`pip install OrcFxAPI` with valid license).

```cmd
python scripts\data\orcaflex\dat-to-yaml.py ^
    --input "\\ace-linux-2\dde\Orcaflex\0000 Drilling Riser Development\Latest" ^
    --output "client_projects\data\raw\orcaflex-extracted\drilling-riser-development" ^
    --project drilling-riser-development
```

Then commit the raw YAMLs to `client_projects` and push.

## Stage 2+3 — Anonymize + Import (ace-linux-1)

```bash
cd /mnt/local-analysis/workspace-hub

# Pull latest staging data
git -C client_projects pull

# Preview anonymization
python3 scripts/data/orcaflex/anonymize-import.py \
    --input client_projects/data/raw/orcaflex-extracted/ \
    --output digitalmodel/data/orcaflex/ \
    --dry-run

# Run for real
python3 scripts/data/orcaflex/anonymize-import.py \
    --input client_projects/data/raw/orcaflex-extracted/ \
    --output digitalmodel/data/orcaflex/

# Legal scan + commit
bash scripts/legal/legal-sanity-scan.sh
cd digitalmodel && git add data/orcaflex/ && git commit -m "data(orcaflex): extracted model fixtures WRK-589"
```

## Output Structure

```
digitalmodel/data/orcaflex/
├── drilling-riser-development/
│   ├── Main_Run_Drilling_Riser.yaml
│   ├── ...
├── wellhead-bop-fatigue/
│   ├── BOP_Wellhead.yaml
│   └── ...
└── s-lay-reference/
    └── Reference_Model.yaml
```

## Anonymization Rules

String fields anonymized (original → generic label):
- `name` (object name) → `Obj1`, `Obj2`, ...
- `LineType` → `LineType1`, ...
- `VesselType` → `VesselType1`, ...

All numeric fields (geometry, material properties, load cases) preserved as-is.
An `_anonymize_log.yaml` file records each substitution for auditability.

## Priority Extraction Order

| Project | Files | Standards | Notes |
|---------|-------|-----------|-------|
| `0000 Drilling Riser Development/Latest` | 31 | DNV-OS-F201 | Start here |
| `31290 WellHead Fatigue/BOP on Wellhead` | 240 | API-RP-2A-WSD | Large batch |
| `611 Mecor S Lay/Reference` | 3 | DNV-OS-F101 | Minimal S-lay fixture |
| `5 - OrcaFlex API Check` | 1 | — | API test fixture |
