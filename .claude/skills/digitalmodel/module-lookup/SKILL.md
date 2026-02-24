# digitalmodel Module Lookup Skill

Query the digitalmodel module registry (`specs/module-registry.yaml`) to discover
which modules can perform a given engineering task, implement a specific standard,
or have a given capability — without reading any source code.

## Registry Location

```
digitalmodel/specs/module-registry.yaml
```

## Invocation Patterns

### 1. Query by Capability (natural language)

```python
import yaml
from pathlib import Path

REGISTRY = Path("digitalmodel/specs/module-registry.yaml")

def find_by_capability(keyword: str) -> list[dict]:
    """Return all modules whose capabilities mention the keyword."""
    data = yaml.safe_load(REGISTRY.read_text())
    keyword = keyword.lower()
    return [
        m for m in data["modules"]
        if any(keyword in cap.lower() for cap in m.get("capabilities", []))
        or keyword in m.get("description", "").lower()
    ]

# Examples
find_by_capability("cathodic protection")
find_by_capability("rainflow")
find_by_capability("plate buckling")
find_by_capability("wall thickness")
```

### 2. Query by Standard

```python
def find_by_standard(standard_id: str) -> list[dict]:
    """Return modules that reference a standard, with implementation status."""
    data = yaml.safe_load(REGISTRY.read_text())
    standard_id = standard_id.upper()
    results = []
    for m in data["modules"]:
        for std in m.get("standards", []):
            if standard_id in std["id"].upper():
                results.append({
                    "module_id": m["id"],
                    "path": m["path"],
                    "status": std["status"],
                    "maturity": m["maturity"],
                    "description": m["description"],
                })
    return results

# Examples
find_by_standard("DNV-ST-F101")
find_by_standard("API-579")
find_by_standard("BS-7910")
find_by_standard("DNVGL-RP-C203")
```

### 3. Query by Maturity Level

```python
def find_by_maturity(level: str) -> list[dict]:
    """Return all modules at a given maturity level.

    level: 'production' | 'stable' | 'beta' | 'stub'
    """
    data = yaml.safe_load(REGISTRY.read_text())
    return [m for m in data["modules"] if m.get("maturity") == level]

find_by_maturity("production")
```

### 4. Look Up a Module by ID

```python
def get_module(module_id: str) -> dict | None:
    """Retrieve full module record by id (e.g. 'structural/fatigue')."""
    data = yaml.safe_load(REGISTRY.read_text())
    for m in data["modules"]:
        if m["id"] == module_id:
            return m
    return None

get_module("asset_integrity")
get_module("hydrodynamics/diffraction")
```

### 5. List All Modules with Gaps

```python
def modules_with_gaps() -> list[dict]:
    """Return modules that have documented capability gaps."""
    data = yaml.safe_load(REGISTRY.read_text())
    return [m for m in data["modules"] if m.get("gaps")]
```

## Schema Reference

Each registry entry contains:

| Field | Type | Description |
|---|---|---|
| `id` | str | Unique slug (e.g. `structural/fatigue`) |
| `path` | str | Relative path from repo root |
| `description` | str | One-paragraph human-readable summary |
| `maturity` | str | `production` / `stable` / `beta` / `stub` |
| `capabilities` | list[str] | Concrete things this module can compute |
| `standards` | list[{id, clause?, status}] | Standards referenced; status: `implemented` / `partial` / `gap` / `unknown` |
| `inputs` | list[{name, type, unit?}] | Optional: key inputs |
| `outputs` | list[{name, type, description?}] | Optional: key outputs |
| `gaps` | list[str] | Known limitations or missing features |
| `test_coverage` | str | `high` / `medium` / `low` / `unknown` / `none` |
| `related_wrk` | list[str] | WRK ticket IDs (e.g. `WRK-311`) |

## Agent Prompt Templates

### "Which module handles X?"
```
Load digitalmodel/specs/module-registry.yaml and search capabilities/description
for "<X>". Return module id, path, maturity, and relevant capabilities.
```

### "Is standard Y implemented?"
```
Load digitalmodel/specs/module-registry.yaml and search standards[].id for "<Y>".
Return module id, path, implementation status, and any documented gaps.
```

### "I need to calculate Z — where do I start?"
```
1. Call find_by_capability("<Z keyword>") on the registry.
2. Filter to maturity in [production, stable].
3. Return top 3 results with id, path, capabilities, and inputs/outputs.
```

## CLI Integration

The registry is also queryable via the readiness script:

```bash
bash scripts/readiness/query-docs.sh --capability "cathodic protection"
bash scripts/readiness/query-docs.sh --standard "DNV-ST-F101"
```

## Module Count Summary (as of 2026-02-24)

| Category | Count |
|---|---|
| structural | 7 |
| subsea | 6 |
| hydrodynamics | 8 |
| marine_ops | 5 |
| asset_integrity | 1 |
| specialized | 6 |
| data_systems | 5 |
| infrastructure | 8 |
| workflows | 5 |
| signal_processing | 2 |
| production_engineering | 1 |
| solvers | 6 |
| gis | 1 |
| field_development | 1 |
| well | 2 |
| benchmarks | 1 |
| visualization | 1 |
| **Total** | **70** |
