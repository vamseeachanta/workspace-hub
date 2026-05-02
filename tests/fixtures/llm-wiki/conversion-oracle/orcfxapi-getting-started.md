<!-- oracle_authored_by: claude-sonnet-4-6 -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: 2026-04-25T00:00:00Z -->
<!-- oracle_second_reviewer: self-reviewed-with-24h-delay -->
<!-- oracle_reviewed_at: 2026-04-26T00:00:00Z -->
<!-- single_reviewer_timelag: true -->
<!-- source: https://www.orcina.com/webhelp/OrcFxAPI/Content/GettingStarted.htm -->

# Getting Started with OrcFxAPI

OrcFxAPI is the Python interface to OrcaFlex.

## Installation

Install via pip:

```
pip install OrcFxAPI
```

## Quick Start

- Import the module
- Open a model file
- Run the simulation
- Extract results

```
import OrcFxAPI
model = OrcFxAPI.Model('example.dat')
model.RunSimulation()
```
