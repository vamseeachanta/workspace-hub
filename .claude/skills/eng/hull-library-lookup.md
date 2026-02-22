# Hull Library Lookup Skill

Zero-config nearest-neighbour hull form lookup by target vessel dimensions.
Returns the closest matching hull form with a similarity score and scaling
factors — no catalog files or external data required.

## Invocation

```python
from digitalmodel.hydrodynamics.hull_library.lookup import get_hull_form

match = get_hull_form({"loa_m": 250, "beam_m": 43, "draft_m": 11.5})
```

Or using the full class API:

```python
from digitalmodel.hydrodynamics.hull_library.lookup import HullLookup, HullLookupTarget

lookup = HullLookup()
target = HullLookupTarget(loa_m=260.0, beam_m=46.0, draft_m=14.0)
top3 = lookup.find_closest(target, n=3)
best = lookup.get_hull_form(target)
```

## Input

### Convenience function `get_hull_form`

| Key | Type | Required | Description |
|---|---|---|---|
| `loa_m` | `float` | Yes | Length overall (m) |
| `beam_m` | `float` | Yes | Beam / breadth (m) |
| `draft_m` | `float` | Yes | Draft (m) |
| `displacement_t` | `float` | No | Displacement (tonnes) — not used in scoring |

### `HullLookupTarget` dataclass

Same four fields as constructor arguments.

## Output: `HullMatch`

| Attribute | Type | Description |
|---|---|---|
| `.hull_id` | `str` | Identifier of the matched hull |
| `.similarity_score` | `float` | 0.0–1.0; 1.0 = exact dimensional match |
| `.scaling_factors` | `dict` | `{"loa": float, "beam": float, "draft": float}` — resize candidate to target |
| `.matched_entry` | `HullCatalogEntry | PanelCatalogEntry | dict` | Original catalog entry |
| `.source` | `str` | `"builtin"`, `"catalog"`, or `"panel_catalog"` |

## Algorithm

1. Normalise each dimension (loa, beam, draft) by a fleet-representative
   reference value to give equal weight to all three axes.
2. Compute the Euclidean distance in the normalised 3-D space.
3. Convert distance to a similarity score via `exp(-distance)`.
4. Rank candidates descending by score; return top-n.

Scaling factors are computed as `target / candidate` for each dimension,
giving the factors needed to resize the matched hull to the target.

## Catalog integration

Pass a `HullCatalog` or `PanelCatalog` to `HullLookup(catalog=...)` to
search production catalog entries. Falls back to the built-in eight-hull
set when no catalog is provided or the catalog has no entries with valid
dimensions.

```python
from digitalmodel.hydrodynamics.hull_library import PanelCatalog
from digitalmodel.hydrodynamics.hull_library.lookup import HullLookup, HullLookupTarget

catalog = PanelCatalog.from_yaml("data/panel_catalog.yaml")
lookup = HullLookup(catalog=catalog)
target = HullLookupTarget(loa_m=200.0, beam_m=32.0, draft_m=12.0)
best = lookup.get_hull_form(target)
```

## Built-in hull set

| Hull ID | LOA (m) | Beam (m) | Draft (m) | Type |
|---|---|---|---|---|
| BOX-50 | 50 | 12 | 2.0 | Small barge / utility |
| FST-100 | 100 | 18 | 5.5 | Fast supply / small ship |
| FST-150 | 150 | 25 | 7.0 | Supply / medium ship |
| SEMI-100 | 100 | 80 | 22.0 | Semi-submersible |
| LNGC-250 | 250 | 43 | 11.5 | LNG carrier |
| LNGC-300 | 300 | 50 | 13.0 | Large LNG carrier |
| FPSO-260 | 260 | 46 | 14.0 | FPSO |
| FPSO-320 | 320 | 60 | 18.0 | Large FPSO |

## Error handling

`ValueError` is raised when `loa_m`, `beam_m`, or `draft_m` are missing,
non-positive, or `None`.

A result is always returned for valid inputs — even for extreme or unusual
dimensions, the closest hull in the set is returned with a low score.

## Module location

- Implementation: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/lookup.py`
- Tests: `digitalmodel/tests/hydrodynamics/hull_library/test_lookup.py`
