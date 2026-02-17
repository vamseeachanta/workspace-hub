# Vessel Hull Models Module - Installation Barge 3D Geometry Acquisition

> **Spec:** vessel-hull-models
> **Module:** modules/vessel_hull_models
> **Created:** 2026-01-19
> **Status:** Planning
> **Version:** 1.0.0

---

## Executive Summary

Create a module to acquire, store, and visualize installation barge hull geometries in .obj format. The module will combine data from multiple sources: commercial 3D repositories, parametric hull generation from vessel specifications, and integration with existing marine_safety vessel metadata.

---

## 1. Overview

### Goal
Build a data pipeline to obtain 3D hull models (.obj format) for offshore installation vessels operating in the Gulf of Mexico and globally, enabling visualization and analysis capabilities.

### Target Vessels
| Category | Examples | Priority |
|----------|----------|----------|
| Heavy Lift Crane Vessels | Sleipnir, Thialf, Saipem 7000 | High |
| Pipelay Vessels | Constellation, Seven Borealis | High |
| Single-Lift Mega-Vessels | Pioneering Spirit | Medium |
| Platform Supply Vessels (PSVs) | Generic fleet | Medium |
| Anchor Handling Tug Supply (AHTS) | Generic fleet | Low |

### Deliverables
1. **Data acquisition pipeline** for 3D hull models
2. **Hull model database** with .obj files and metadata
3. **Visualization module** for interactive 3D rendering
4. **Integration layer** with existing marine_safety vessel data

---

## 2. Data Sources Strategy

### 2.1 Primary Sources (Commercial 3D Repositories)

| Source | Access | Format | Cost | Quality |
|--------|--------|--------|------|---------|
| **CGTrader** | Freemium | OBJ native | Free-$200/model | Variable |
| **SketchFab** | Freemium | OBJ export | Free-$50/model | Artistic |
| **TurboSquid** | Commercial | OBJ native | $15-150/model | Professional |
| **GrabCAD** | Community | STEP→OBJ | Free | Engineering |

**Approach:** Programmatic search and download via APIs where available; manual curation for high-priority vessels.

### 2.2 Secondary Source (Parametric Hull Generation)

Generate synthetic hull models from vessel specifications:

**Input Data:**
- MarineTraffic/VesselFinder dimensions (LOA, beam, draft)
- AIS vessel type classifications
- Displacement/tonnage data

**Generation Method:**
- Parent hull form selection based on vessel type
- Parametric scaling using naval architecture formulas
- Export to OBJ via mesh conversion

**Tools:**
- `trimesh` - Python mesh manipulation library
- `numpy-stl` - STL/OBJ file handling
- Custom parametric hull generator (naval architecture algorithms)

### 2.3 Tertiary Source (Existing Vessel Metadata)

Leverage `marine_safety` module data:
- Canadian TSB vessel.csv (hull material, dimensions, builder)
- LNG vessel database (`data/modules/lngc/`)
- Cross-reference with 3D model acquisitions

---

## 3. Technical Architecture

### 3.1 Module Structure

```
src/worldenergydata/modules/vessel_hull_models/
├── __init__.py
├── config.py                    # Module configuration
├── cli.py                       # Command-line interface
│
├── acquisition/                 # Data acquisition layer
│   ├── __init__.py
│   ├── repository_clients/      # 3D repository API clients
│   │   ├── cgtrader.py
│   │   ├── sketchfab.py
│   │   └── grabcad.py
│   ├── vessel_specs.py          # MarineTraffic/VesselFinder integration
│   └── parametric_generator.py  # Synthetic hull generation
│
├── data/                        # Data management
│   ├── __init__.py
│   ├── models.py                # SQLModel definitions
│   ├── repository.py            # Data access layer
│   └── cache/                   # Local hull model cache
│
├── geometry/                    # 3D geometry processing
│   ├── __init__.py
│   ├── obj_parser.py            # OBJ file parsing/validation
│   ├── mesh_operations.py       # Mesh manipulation (trimesh)
│   ├── format_converter.py      # STEP/STL → OBJ conversion
│   └── hull_primitives.py       # Parametric hull shapes
│
├── visualization/               # Rendering and display
│   ├── __init__.py
│   ├── plotly_3d.py             # Plotly mesh3d visualization
│   ├── html_renderer.py         # Standalone HTML exports
│   └── templates/               # Jinja2 HTML templates
│
└── reports/                     # Report generation
    ├── __init__.py
    ├── fleet_report.py          # Multi-vessel fleet reports
    └── vessel_card.py           # Single vessel detail cards
```

### 3.2 Data Model

```python
# models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class VesselHullModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Vessel identification
    imo_number: Optional[str] = Field(index=True)
    mmsi: Optional[str]
    vessel_name: str = Field(index=True)
    vessel_type: str  # crane_vessel, pipelay, ahts, psv, etc.

    # Hull dimensions (meters)
    length_overall: float
    beam: float
    depth: float
    draft: float
    displacement: Optional[float]  # tonnes

    # 3D model metadata
    obj_file_path: str
    source: str  # cgtrader, sketchfab, parametric, etc.
    source_url: Optional[str]
    model_quality: str  # engineering, professional, artistic, synthetic
    vertex_count: int
    face_count: int
    file_size_bytes: int

    # Timestamps
    acquired_at: datetime
    last_validated: Optional[datetime]

    # Cross-references
    marine_safety_vessel_id: Optional[int]  # FK to marine_safety.vessel
```

### 3.3 Dependencies

```toml
# pyproject.toml additions
[project.dependencies]
trimesh = ">=4.0.0"        # Mesh processing
numpy-stl = ">=3.0.0"      # STL/OBJ handling
plotly = ">=5.18.0"        # 3D visualization (existing)
httpx = ">=0.25.0"         # Async HTTP client
pydantic = ">=2.0.0"       # Data validation (existing)
sqlmodel = ">=0.0.14"      # Database ORM (existing)
jinja2 = ">=3.1.0"         # HTML templates (existing)
```

---

## 4. Implementation Tasks

### Phase 1: Foundation (Week 1)
- [ ] 1.1 Create module directory structure
- [ ] 1.2 Define SQLModel data models
- [ ] 1.3 Implement OBJ file parser with validation
- [ ] 1.4 Write unit tests for geometry processing
- [ ] 1.5 Set up database migrations

### Phase 2: Acquisition Pipeline (Week 2)
- [ ] 2.1 Implement CGTrader search/download client
- [ ] 2.2 Implement SketchFab API client
- [ ] 2.3 Build MarineTraffic vessel specs fetcher
- [ ] 2.4 Create acquisition CLI commands
- [ ] 2.5 Write integration tests for API clients

### Phase 3: Parametric Generation (Week 3)
- [ ] 3.1 Research standard hull form coefficients
- [ ] 3.2 Implement parent hull form library
- [ ] 3.3 Build parametric scaling algorithm
- [ ] 3.4 Create synthetic hull generator
- [ ] 3.5 Validate against known vessel dimensions

### Phase 4: Visualization (Week 4)
- [ ] 4.1 Implement Plotly mesh3d renderer
- [ ] 4.2 Create interactive HTML vessel viewer
- [ ] 4.3 Build fleet visualization dashboard
- [ ] 4.4 Add vessel comparison tool
- [ ] 4.5 Write visualization tests

### Phase 5: Integration & Reports (Week 5)
- [ ] 5.1 Integrate with marine_safety vessel data
- [ ] 5.2 Create vessel detail card reports
- [ ] 5.3 Build fleet summary report
- [ ] 5.4 Document API and CLI usage
- [ ] 5.5 End-to-end testing

---

## 5. Acquisition Workflow

### 5.1 Manual Curation (High-Priority Vessels)

```bash
# Search for specific vessel
uv run python -m worldenergydata.vessel_hull_models.cli search \
    --name "Sleipnir" \
    --sources cgtrader,sketchfab,turbosquid

# Download and register model
uv run python -m worldenergydata.vessel_hull_models.cli acquire \
    --source cgtrader \
    --model-id "offshore-crane-vessel-sleipnir" \
    --vessel-name "Sleipnir" \
    --imo "9781400"
```

### 5.2 Batch Parametric Generation

```bash
# Generate synthetic hulls from vessel database
uv run python -m worldenergydata.vessel_hull_models.cli generate \
    --vessel-type crane_vessel \
    --source marinetraffic \
    --output-dir data/modules/vessel_hull_models/synthetic/
```

### 5.3 Quality Validation

```bash
# Validate hull model geometry
uv run python -m worldenergydata.vessel_hull_models.cli validate \
    --file data/modules/vessel_hull_models/hulls/sleipnir.obj \
    --expected-loa 220 \
    --expected-beam 102 \
    --tolerance 0.05  # 5% tolerance
```

---

## 6. Visualization Output

### 6.1 Interactive 3D Viewer (Plotly)

```python
# Example usage
from worldenergydata.vessel_hull_models.visualization import plotly_3d

fig = plotly_3d.render_vessel(
    obj_path="data/modules/vessel_hull_models/hulls/sleipnir.obj",
    title="SSCV Sleipnir - Hull Visualization",
    color_by="depth",  # depth-based coloring
    show_waterline=True
)
fig.write_html("reports/sleipnir_hull.html")
```

### 6.2 Fleet Comparison Dashboard

Interactive HTML dashboard comparing multiple vessel hulls:
- Side-by-side 3D views
- Dimension comparison table
- Hull form coefficient analysis
- Filterable by vessel type, operator, region

---

## 7. Critical Files to Modify/Create

| File | Action | Purpose |
|------|--------|---------|
| `src/worldenergydata/modules/vessel_hull_models/` | Create | New module directory |
| `src/worldenergydata/modules/vessel_hull_models/models.py` | Create | Data models |
| `src/worldenergydata/modules/vessel_hull_models/geometry/obj_parser.py` | Create | OBJ parsing |
| `src/worldenergydata/modules/vessel_hull_models/acquisition/` | Create | API clients |
| `src/worldenergydata/modules/vessel_hull_models/visualization/plotly_3d.py` | Create | 3D rendering |
| `data/modules/vessel_hull_models/` | Create | Data storage |
| `tests/modules/vessel_hull_models/` | Create | Test suite |
| `pyproject.toml` | Modify | Add dependencies |

---

## 8. Verification Plan

### 8.1 Unit Tests
```bash
uv run pytest tests/modules/vessel_hull_models/ -v --cov=src/worldenergydata/modules/vessel_hull_models
```

### 8.2 Integration Tests
- Verify OBJ file parsing for sample models
- Test API client connectivity (mocked for CI)
- Validate parametric hull generation accuracy

### 8.3 End-to-End Validation
1. Acquire 3 sample hull models from CGTrader/SketchFab
2. Generate 5 synthetic hulls from MarineTraffic specs
3. Render interactive HTML visualization
4. Verify vessel dimensions match within 5% tolerance

### 8.4 Manual Verification
- Visual inspection of 3D renders
- Cross-reference hull dimensions with published specs
- Validate waterline rendering accuracy

---

## 9. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits on 3D repositories | Medium | Implement caching, respect rate limits |
| Low availability of specific vessel models | High | Parametric generation as fallback |
| OBJ format inconsistencies | Medium | Robust parser with validation |
| Large file sizes for detailed models | Low | Mesh decimation, LOD support |
| Classification society data restrictions | High | Focus on publicly available sources |

---

## 10. Design Decisions (Confirmed)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Vessel Scope** | GOM Installation Vessels | Focus on Gulf of Mexico heavy lift, pipelay, and crane vessels (Heerema, Saipem, McDermott fleets) |
| **Accuracy Tolerance** | 5% | Dimensions within 5% of actual specs - suitable for visualization and analysis |
| **Licensing Strategy** | Free/Open Models Only | Prioritize SketchFab/GrabCAD free models with permissive licenses; generate synthetic for unavailable vessels |
| **Storage** | Local (data/modules/) | Consistent with existing module patterns |

### Target GOM Vessel Fleet

| Operator | Vessels | Type |
|----------|---------|------|
| Heerema | Sleipnir, Thialf | Heavy Lift Crane |
| Saipem | Saipem 7000, Constellation | Pipelay/Crane |
| McDermott | DLV 2000, Amazon | Derrick Lay |
| Allseas | Pioneering Spirit | Single-Lift |
| Subsea 7 | Seven Borealis | Pipelay |

### Acquisition Priority

1. **Tier 1 (Free models):** Search SketchFab, GrabCAD for existing free models
2. **Tier 2 (Synthetic):** Generate parametric hulls from MarineTraffic/VesselFinder specs
3. **Tier 3 (Skip):** Do not purchase commercial models

---

## 11. References

- [Trimesh Documentation](https://trimesh.org/)
- [Plotly 3D Mesh](https://plotly.com/python/3d-mesh/)
- [OBJ File Format Spec](https://en.wikipedia.org/wiki/Wavefront_.obj_file)
- [MarineTraffic API](https://www.marinetraffic.com/en/ais-api-services)
- [CGTrader API](https://www.cgtrader.com/pages/sell-3d-models/api)
- [Naval Architecture Hull Forms](https://www.sciencedirect.com/topics/engineering/hull-form)
