<!-- oracle_authored_by: claude-sonnet-4-6 -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: 2026-04-25T00:00:00Z -->
<!-- oracle_second_reviewer: self-reviewed-with-24h-delay -->
<!-- oracle_reviewed_at: 2026-04-26T00:00:00Z -->
<!-- single_reviewer_timelag: true -->
<!-- source: https://www.orcina.com/webhelp/OrcaFlex/Content/APIObjects.htm -->

# OrcaFlex API Objects

The OrcFxAPI provides Python access to OrcaFlex model objects.

## Model Object

The top-level model object:

```
import OrcFxAPI
model = OrcFxAPI.Model()
model.LoadData('model.dat')
```

## Object Access

- Lines: model['Line1']
- Vessels: model['Vessel1']
- Environment: model.environment

## Running Simulation

```
model.RunSimulation()
line = model['Line1']
tension = line.TimeHistory('Effective tension', OrcFxAPI.oeEndA)
```
