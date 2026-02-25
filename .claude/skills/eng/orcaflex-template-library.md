# OrcaFlex Template Library Skill

Zero-config lookup of canonical Jinja2 templates for OrcaFlex model generation.
Returns raw template content or rendered output for any recognised structure type,
including common domain aliases such as "riser" and "mooring".

Skill name: `orcaflex_template_library`

## Invocation

```python
from digitalmodel.workflows.agents.orcaflex.template_library import (
    get_orcaflex_template,
    list_structure_types,
    get_all_templates,
)

# Retrieve raw template content
result = get_orcaflex_template("general")
print(result["content"])          # raw Jinja2 source
print(result["template_path"])    # absolute path on disk

# Use an alias
result = get_orcaflex_template("riser")   # resolves to "lines"
print(result["structure_type"])   # "lines"

# Render with context variables
context = {
    "project_name": "DEEPWATER_SPAR",
    "generation_date": "2026-01-15",
    "stage_duration_buildup": 10,
    "stage_duration_simulation": 3600,
    "statics_min_damping": 5,
    "dynamics_solution_method": "Implicit time domain",
}
result = get_orcaflex_template("general", render=True, context=context)
print(result["rendered"])         # fully rendered YAML string

# Discovery
all_types = list_structure_types()   # 8 canonical + 5 aliases
all_meta  = get_all_templates()      # list of 8 metadata dicts (no content)
```

## API Reference

### `get_orcaflex_template(structure_type, render=False, context=None) -> dict`

Returns a dictionary with keys:

| Key | Type | Description |
|---|---|---|
| `structure_type` | `str` | Resolved canonical type (alias expanded) |
| `template_file` | `str` | Jinja2 template filename |
| `template_path` | `str` | Absolute path to the template file |
| `content` | `str` | Raw Jinja2 template content |
| `rendered` | `str \| None` | Rendered YAML when `render=True` and `context` provided; `None` otherwise |

Raises `ValueError` for unknown structure types.

### `list_structure_types() -> list[str]`

Returns all supported type strings — 8 canonical types plus 5 aliases.
Useful for discovery and validation before calling `get_orcaflex_template`.

### `get_all_templates() -> list[dict]`

Returns a list of 8 metadata dicts (one per canonical type), each with
`structure_type`, `template_file`, and `template_path`. Does not include
template content — use `get_orcaflex_template` for content.

## Structure Type Catalogue

### Canonical Types (8)

| Type | Template File | Description |
|---|---|---|
| `general` | `01_general.yml.j2` | Simulation stage durations, statics, dynamics settings |
| `environment` | `02_environment.yml.j2` | Water depth and environmental parameters |
| `vessel` | `04_vessel_wrapper.yml.j2` | Vessel type definition (hull, RAO, AMD references) |
| `vessel_instance` | `05_vessel_inst_wrapper.yml.j2` | Vessel instance placement and heading |
| `line_types` | `06_line_types.yml.j2` | Line type definitions (diameter, EA, mass/length) |
| `lines` | `07_lines_wrapper.yml.j2` | Line objects (mooring lines, risers, tethers) |
| `buoys` | `08_buoys_wrapper.yml.j2` | Buoy objects (6D buoys, CALM buoys) |
| `groups` | `09_groups.yml.j2` | Object grouping for post-processing |

### Aliases (5)

| Alias | Resolves To | Rationale |
|---|---|---|
| `riser` | `lines` | Risers are modelled as OrcaFlex Lines |
| `mooring` | `lines` | Mooring lines are OrcaFlex Lines |
| `catenary` | `lines` | Catenary mooring is an OrcaFlex Line |
| `tether` | `lines` | Tethers (TLP) are OrcaFlex Lines |
| `hull` | `vessel` | Hull geometry is part of the Vessel object |

## Error Conditions

`ValueError` is raised (never silently swallowed) for:
- Unrecognised structure type not in canonical types or aliases
- Empty string input

## Zero-config Guarantee

No environment variables, network access, or external data files required.
Templates ship with the `digitalmodel` package under:
`digitalmodel/workflows/agents/orcaflex/templates/base_files/`

## Module Location

- Implementation: `digitalmodel/src/digitalmodel/workflows/agents/orcaflex/template_library.py`
- Tests: `digitalmodel/tests/workflows/agents/orcaflex/test_template_library.py`
- Templates: `digitalmodel/src/digitalmodel/workflows/agents/orcaflex/templates/base_files/`
