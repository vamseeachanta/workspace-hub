---
title: "WRK-114: Hull Panel Collection and Catalog"
description: "Collect, inventory, and catalog hull panel geometries from 5 source directories into a consolidated, searchable catalog in digitalmodel"
version: "1.0"
module: hydrodynamics/hull_library
session:
  id: wrk-114-plan
  agent: claude-opus-4.6
review:
  cross_review: pending
  iterations: 0
---

# WRK-114: Hull Panel Collection and Catalog

## Context

Hull panel meshes for diffraction/hydrodynamic analysis are scattered across 5 directories in different repos. Engineers must know which hulls exist, where they are, what format, and what dimensions — to pick a geometry and optionally scale it for a new vessel. No consolidated inventory exists today.

**Goal**: Create a machine-readable catalog (YAML + CSV) of all hull panels across the workspace, copy a curated set of representative GDF files into `digitalmodel/data/hull_library/panels/`, and document scaling approaches.

**Design principle**: Catalog-first, not copy-first. Most files stay in their source location and are referenced by path. Only small representative GDF files (<5 MB) are copied into the canonical directory.

## Source Inventory Summary

| Source | Location | Files | Formats | Hull Types |
|--------|----------|-------|---------|------------|
| a) OrcaWave | `digitalmodel/docs/modules/orcawave/` | 86 GDF/OWD | GDF, OWD, YAML | Cylinders, spheres, ellipsoids, barges, semi-subs, spars, FPSO, ships |
| b) Hull collection | `acma-projects/_hulls/` | 8 files | .3dm, .xlsx, .pdf | Aframax tanker, 3 semi-sub types (Q4000, SDP 3500, Uncle John) |
| c) Rock Oil Field | `rock-oil-field/s7/analysis_general/` | 3 files | .rao, .hst, .dat | Training vessel, Seven Seas mesh |
| d) AQWA FST/LNGC | `acma-projects/B1522/ctr-7/_src/aqwa/rev_a08/` | 135 files | AQWA DAT/DECK | FST (~204m), LNGC (125/180 km3) |
| e) Saipem FPSO | `saipem/yellowtail/code/rev2/03_Vessels_host/` | ~18 YAML | OrcaFlex YAML | FPSO variants (dims only, no panels) |

**Estimated catalog**: ~40-46 entries. **Copied GDF files**: ~12-15, total ~5-10 MB.

## Existing Infrastructure to Reuse

| Component | File | Use |
|-----------|------|-----|
| `GDFHandler.read()` | `digitalmodel/.../bemrosetta/mesh/gdf_handler.py` | Parse GDF → PanelMesh (panel count, vertices, bounding box) |
| `DATHandler.read()` | `digitalmodel/.../bemrosetta/mesh/dat_handler.py` | Parse AQWA DAT → PanelMesh (auto-detects AQWA deck format) |
| `HullType` enum | `digitalmodel/.../hull_library/profile_schema.py` | Extend with SPAR, FPSO, CYLINDER, etc. |
| `HullCatalog` pattern | `digitalmodel/.../hull_library/catalog.py` | Follow same Pydantic + YAML pattern |
| Seed profiles | `digitalmodel/data/hull_library/profiles/` | unit_box.yaml, generic_barge.yaml, generic_tanker.yaml |
| GDF parser (worldenergydata) | `worldenergydata/.../vessel_hull_models/geometry/gdf_parser.py` | Alternative parser with OBJ export (Tier 1) |

## Implementation Plan

### Phase 1: Data Model and Schema (~150 lines new code)

**1.1 Extend `HullType` enum**
- File: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/profile_schema.py`
- Add: `SPAR`, `CYLINDER`, `SPHERE`, `ELLIPSOID`, `FPSO`, `LNGC` values
- Backward-compatible (additive only)

**1.2 Create `panel_catalog.py`** (NEW)
- File: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/panel_catalog.py`
- Classes:
  - `PanelFormat(str, Enum)` — GDF, AQWA_DAT, OWD, OBJ, RHINO_3DM, ORCAFLEX_YAML, YAML_PROFILE
  - `PanelCatalogEntry(BaseModel)` — hull_id, hull_type, name, source, panel_format, file_path, panel_count, vertex_count, symmetry, length_m, beam_m, draft_m, displacement_t, description, loading_condition, tags
  - `PanelCatalog(BaseModel)` — version, updated, entries list, `from_yaml()`, `to_yaml()`, `to_csv()` methods

**1.3 Update `__init__.py`**
- File: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/__init__.py`
- Add exports: `PanelFormat`, `PanelCatalogEntry`, `PanelCatalog`

**1.4 Tests** (NEW)
- File: `digitalmodel/tests/hydrodynamics/hull_library/test_panel_catalog.py` (~120 lines)
- Tests: entry validation, enum values, YAML round-trip, CSV export, hull_id uniqueness

### Phase 2: Inventory Scanner (~250 lines new code)

**2.1 Create `panel_inventory.py`** (NEW)
- File: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/panel_inventory.py`
- Functions:
  - `scan_gdf_directory(base_dir, source_id) -> list[PanelCatalogEntry]` — uses `GDFHandler.read()` to extract panel count, bounding box dimensions
  - `scan_aqwa_dat_directory(base_dir, source_id) -> list[PanelCatalogEntry]` — uses `DATHandler.read()` for AQWA files
  - `scan_orcaflex_vessels(base_dir, source_id) -> list[PanelCatalogEntry]` — parses OrcaFlex YAML for vessel dimensions
  - `scan_metadata_hulls(base_dir) -> list[PanelCatalogEntry]` — catalogs non-parseable files (.3dm, .xlsx) by filename metadata
  - `build_full_catalog(source_config) -> PanelCatalog` — orchestrates all scanners

**2.2 Source scanning strategy**

| Source | Scanner | Parsing | What's extracted |
|--------|---------|---------|-----------------|
| a) OrcaWave GDF | `scan_gdf_directory` | `GDFHandler.read()` | panel_count, vertices, bounding box → L/B/T |
| b) _hulls | `scan_metadata_hulls` | Filename only | hull_type, name, format (panel_count=None) |
| c) rock-oil-field | `scan_metadata_hulls` | Filename only | hull_type, format, notes |
| d) AQWA DAT | `scan_aqwa_dat_directory` | `DATHandler.read()` | panel_count, vertices, bounding box |
| e) yellowtail YAML | `scan_orcaflex_vessels` | YAML parse | length, beam, draft from vessel definition |

**2.3 Tests** (NEW)
- File: `digitalmodel/tests/hydrodynamics/hull_library/test_panel_inventory.py` (~200 lines)
- Tests: scan barge.gdf, scan spar.gdf, handle missing dir, hull_id uniqueness, catalog non-empty

### Phase 3: Consolidate Representative GDF Panels

**3.1 Directory structure** (NEW)
```
digitalmodel/data/hull_library/
  panels/                              # NEW subdirectory
    primitives/
      cylinder_r10_d50.gdf             # from L00 validation 3.3
      sphere_r5.gdf                    # from L00 validation 3.2
      ellipsoid_96p.gdf               # from L00 validation 2.8
      pyramid_zc08.gdf                 # from L00 validation 2.7
    barges/
      barge_100x20x10.gdf             # from test-configs/geometry
      unit_box.gdf                     # from L01 benchmark
    semi_subs/
      oc4_semisub.gdf                  # from L02 example
      l03_centre_column.gdf            # from L03 example
      l03_outer_column.gdf             # from L03 example
    spars/
      spar_r10_d50.gdf                 # from test-configs/geometry
    ships/
      l01_vessel_385p.gdf              # from L01 default vessel
  catalog/                             # NEW subdirectory
    hull_panel_catalog.yaml            # machine-readable catalog
    hull_panel_catalog.csv             # summary for quick reference
```

**3.2 Copy criteria**

| Criterion | Action |
|-----------|--------|
| GDF file < 5 MB from source a (OrcaWave) | Copy to `panels/`, sanitize header |
| GDF file > 5 MB (e.g., sea_cypress 2.0M) | Reference in catalog only |
| AQWA DAT files (source d) | Reference in catalog only (too large, complex) |
| Binary formats (.3dm, .dat OrcaFlex) | Reference in catalog, metadata only |
| OrcaFlex YAML (source e) | Reference in catalog, dimensions only |

**3.3 GDF header sanitization**
- Read line 1 of each copied GDF
- Check against legal deny list patterns
- Replace any client-specific text with generic description
- Source a files are standard validation cases — expected to be clean

**3.4 Consolidation script** (NEW)
- File: `digitalmodel/scripts/consolidate_panels.py` (~100 lines)
- One-time script: copies selected GDFs, sanitizes headers, runs `build_full_catalog()`, writes YAML + CSV

### Phase 4: Scaling Documentation

**4.1 Hull scaling guide** (NEW)
- File: `digitalmodel/docs/modules/hull_library/hull_scaling_guide.md` (~100 lines)
- Two approaches:
  1. **Geometric scaling**: multiply all vertex coords by factor (uniform)
  2. **Parametric scaling**: scale L/B/T independently via axis-specific factors
- References existing `HullVariation.scale_factors` in `catalog.py`
- Notes: re-panelization may be needed after non-uniform scaling for solver accuracy

### Phase 5: Legal Compliance

- Sources b, d, e are in client project directories
- **No files are copied** from these sources (catalog-only references)
- Copied GDF files (source a) are industry standard validation geometries
- Sanitize GDF header line 1 for any copied files
- Run `./scripts/legal/legal-sanity-scan.sh --repo=digitalmodel --diff-only` before commit

### Phase 6: Integration Tests (~150 lines)

**6.1 Test file** (NEW)
- File: `digitalmodel/tests/hydrodynamics/hull_library/test_panel_integration.py`
- Tests:
  - `test_catalog_yaml_loads` — generated catalog is valid YAML, loads into PanelCatalog
  - `test_all_gdf_entries_have_panel_count` — every GDF entry has non-null panel_count
  - `test_copied_gdf_files_exist` — every entry pointing to `panels/` has a real file
  - `test_gdf_files_parseable` — every GDF in `panels/` parses via GDFHandler
  - `test_catalog_hull_ids_unique` — no duplicate hull_ids
  - `test_at_least_one_hull_per_major_type` — catalog covers barge, spar, semi_sub, ship
  - `test_no_legal_violations` — no deny-listed terms in catalog YAML

## File Change Summary

### New Files (7 source + 1 script + 1 doc + ~12-15 GDF copies + 2 catalog outputs)

| File | Est. Lines | Purpose |
|------|-----------|---------|
| `digitalmodel/src/.../hull_library/panel_catalog.py` | ~150 | PanelCatalogEntry, PanelCatalog, PanelFormat models |
| `digitalmodel/src/.../hull_library/panel_inventory.py` | ~250 | Source scanners, catalog builder |
| `digitalmodel/tests/.../hull_library/test_panel_catalog.py` | ~120 | Unit tests for data models |
| `digitalmodel/tests/.../hull_library/test_panel_inventory.py` | ~200 | Unit tests for inventory scanners |
| `digitalmodel/tests/.../hull_library/test_panel_integration.py` | ~150 | Integration tests |
| `digitalmodel/scripts/consolidate_panels.py` | ~100 | One-time consolidation script |
| `digitalmodel/docs/modules/hull_library/hull_scaling_guide.md` | ~100 | Scaling documentation |

### Modified Files (2)

| File | Change |
|------|--------|
| `digitalmodel/src/.../hull_library/profile_schema.py` | Add 6 values to `HullType` enum |
| `digitalmodel/src/.../hull_library/__init__.py` | Add 3 new exports |

### Generated Outputs

| File | Description |
|------|-------------|
| `digitalmodel/data/hull_library/catalog/hull_panel_catalog.yaml` | Full catalog (~40-46 entries) |
| `digitalmodel/data/hull_library/catalog/hull_panel_catalog.csv` | Summary CSV |
| `digitalmodel/data/hull_library/panels/{primitives,barges,semi_subs,spars,ships}/*.gdf` | ~12-15 curated GDF files |

## Verification

1. **Unit tests**: `PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/hydrodynamics/hull_library/test_panel_catalog.py tests/hydrodynamics/hull_library/test_panel_inventory.py -v --tb=short --noconftest`
2. **Integration tests**: `PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/hydrodynamics/hull_library/test_panel_integration.py -v --tb=short --noconftest`
3. **Existing tests still pass**: `PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/hydrodynamics/hull_library/ -v --tb=short --noconftest`
4. **Legal scan**: `./scripts/legal/legal-sanity-scan.sh --repo=digitalmodel --diff-only`
5. **Manual check**: Open `hull_panel_catalog.yaml`, verify entries for all 5 sources, spot-check dimensions

## Risks

| Risk | Mitigation |
|------|------------|
| AQWA DAT parse failure on some files | Skip entries that fail, log warning, catalog with metadata only |
| Sea Cypress GDF is 2.0 MB (close to 5 MB limit) | Include in `panels/fpso/` — still under threshold |
| `.3dm` (Rhino) not parseable | Catalog with known metadata from filenames; panel_count=None |
| OrcaFlex YAML vessel definition structure varies | Try/except per field, catalog what's available |
