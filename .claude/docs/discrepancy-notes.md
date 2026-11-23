# Discrepancy Notes Convention

## Purpose

Track dimension, material, boundary condition, and load conflicts found during engineering analysis. Notes are grep-parseable and labels enable GitHub Projects filtering.

## GitHub Labels

| Label | Use |
|-------|-----|
| `discrepancy` | Broad catch-all |
| `discrepancy:dims` | Dimension conflicts between sources |
| `discrepancy:material` | Material or specification conflicts |
| `discrepancy:bc` | Boundary condition conflicts |
| `discrepancy:load` | Load assumption conflicts |

## Comment Convention

### Format

```
DISC[CAT]: description
```

- `CAT` = `DIM`, `MAT`, `BC`, or `LOAD`
- Add `|BLOCK` suffix for blocking items: `DISC[CAT|BLOCK]: description`

### Examples

```
DISC[DIM]: tube OD = 1.75" per photo but 1.5" in model
DISC[MAT]: drawing calls 6061-T6 but BOM lists 6063-T5
DISC[BC|BLOCK]: fixed support assumed at base — need confirmation of actual anchorage
DISC[LOAD]: wind load uses 100 mph but site spec says 120 mph
```

## Searching

```bash
# All discrepancies in a file
grep -n 'DISC\[' file.md

# Only blocking items
grep -n 'DISC\[.*|BLOCK\]' file.md

# By category
grep -n 'DISC\[DIM' file.md

# Across issues via gh
gh issue list --label discrepancy:dims
```

## Workflow

1. Apply relevant `discrepancy:*` label to the GitHub issue
2. Post `DISC[CAT]:` notes as issue comments (one per conflict)
3. When resolved, reply to the note with resolution and strike through the original
