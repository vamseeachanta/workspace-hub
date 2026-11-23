# BSEE Field Pipeline Skill

Zero-config agent-callable wrapper around the BSEE field production pipeline.
Returns structured monthly production data and summary statistics for any
Gulf of Mexico deepwater field — no API keys, environment variables, or config files required.

## Invocation

```python
from worldenergydata.bsee.skill import bsee_field_pipeline
result = bsee_field_pipeline("Atlantis")
```

Or via the package:

```python
from worldenergydata.bsee import bsee_field_pipeline
result = bsee_field_pipeline("Thunder Horse")
```

## Input

| Parameter | Type | Required | Description |
|---|---|---|---|
| `field_name` | `str` | Yes | BSEE field name, e.g. "Atlantis", "Thunder Horse", "Mars" |
| `parameters` | `list[str]` | No | Subset of `["oil_bbl", "gas_mcf", "water_bbl"]`; default: all three |
| `start` | `str` | No | Start date filter as `"YYYY-MM"` |
| `end` | `str` | No | End date filter as `"YYYY-MM"` |

Field name matching is case-insensitive.

## Output: `BseeFieldResult`

| Attribute | Type | Description |
|---|---|---|
| `.field_name` | `str` | Upper-cased BSEE field name |
| `.operator` | `str` | Primary operator name |
| `.data` | `pd.DataFrame` | Monthly production — columns: `year`, `month`, `oil_bbl`, `gas_mcf`, `water_bbl` |
| `.summary` | `dict` | Aggregated statistics (see below) |
| `.source` | `str` | Always `"bsee"` |

### Summary dict keys

| Key | Type | Description |
|---|---|---|
| `peak_oil_bbl` | `float` | Highest single-month oil production (bbl) |
| `cumulative_oil_bbl` | `float` | Total oil produced over the date range (bbl) |
| `decline_rate_pct` | `float` | Annualised exponential decline rate (%) |
| `first_date` | `str` | First data point as `"YYYY-MM"` |
| `last_date` | `str` | Last data point as `"YYYY-MM"` |

## Examples

```python
# Full result
result = bsee_field_pipeline("Atlantis")
print(result.field_name)          # "ATLANTIS"
print(result.operator)             # "BP Exploration & Production Inc."
print(result.data.head())
print(result.summary["peak_oil_bbl"])

# Oil-only, filtered date range
result = bsee_field_pipeline(
    "Mars",
    parameters=["oil_bbl"],
    start="2000-01",
    end="2010-12",
)

# Agent-style one-liner
from worldenergydata.bsee import bsee_field_pipeline
print(bsee_field_pipeline("Thunder Horse").summary)
```

## Zero-config guarantee

No API keys, environment variables, or config files required.
Uses cached/synthetic data when live BSEE binary files are unavailable.
Synthetic data covers realistic production profiles (ramp-up + exponential decline)
for known deepwater fields; unknown fields receive a sensible default profile.

## Module location

- Skill implementation: `worldenergydata/src/worldenergydata/bsee/skill.py`
- Skill name constant: `SKILL_NAME = "bsee_field_pipeline"`
- Tests: `worldenergydata/tests/unit/bsee/test_skill.py`
