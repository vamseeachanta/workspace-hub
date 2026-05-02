<!-- oracle_authored_by: claude-sonnet-4-6 -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: 2026-04-25T00:00:00Z -->
<!-- oracle_second_reviewer: self-reviewed-with-24h-delay -->
<!-- oracle_reviewed_at: 2026-04-26T00:00:00Z -->
<!-- single_reviewer_timelag: true -->
<!-- source: https://www.orcina.com/webhelp/OrcFxAPI/Content/DataAccess.htm -->

# Data Access

OrcFxAPI provides read and write access to all OrcaFlex model data.

## Reading Data

Object data is accessed as attributes:

```
line = model['Line1']
diameter = line.OD
length = line.Length[0]
```

## Writing Data

Data can be modified before running a simulation:

```
line.OD = 0.25
line.Length[0] = 500.0
model.RunSimulation()
```

## Data Types

OrcFxAPI supports the following data types for model properties:

```
float     # Real-valued properties
int       # Integer properties
str       # String properties
ndarray   # Array properties (numpy)
```
