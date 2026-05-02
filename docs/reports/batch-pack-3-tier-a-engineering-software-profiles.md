---
title: Batch Pack 3 Tier A — Engineering Software Profiles
issue: 2380
plan: docs/plans/2026-04-23-issue-2380-batch-pack-3-tier-a-engineering-software-profiles.md
generated: 2026-04-24
candidates: 154
tier_a_engineering: 117
packages_after_collapse: 82
extend_only: 4
create: 78
scope: offline classification and wiki-ready stub authoring; NO writes under knowledge/wikis/
---

# Batch Pack 3 Tier A — Engineering Software Profiles

This report lists wiki-ready package profiles derived offline from the `notes` fields of 
`type in [github_repo, tool]` entries in `data/document-index/online-resource-registry.yaml`. 
Per plan (issue #2380), no network calls, no cloning, no downloads, and no modifications to 
`knowledge/wikis/**` are performed in this wave — downstream consumers (#2039) will ingest these stubs.

## Summary

- Total candidates (github_repo + tool): **154**
- Tier A (meaningful notes + capability keywords): **128**
- Excluded non-engineering from Tier A: **11**
- Engineering Tier A (post-filter): **117**
- Package roots after collapsing repo/docs twins: **82**
- Extend-only (exact match to existing wiki entity): **4**
- Create (net-new wiki entity): **78**
- Tier B deferred (sparse notes): **26**

## Accounting gate (by registry rows, not packages)

Package counts collapse repo/docs twins, so extend/create numbers above differ from the row counts below.
The 154 candidate rows must equal the sum of all member rows across every bucket:

- extend-only member rows: **4** (from 4 packages)
- create member rows: **113** (from 78 packages)
- tier_b_deferred: **26**
- excluded_non_engineering: **11**

`4 + 113 + 26 + 11 = 154` (must equal **154**)

---

## Create — net-new package profiles (wiki-ready stubs)

78 packages below are net-new to `knowledge/wikis/engineering/wiki/entities/`. 
Each stub is grouped by canonical package root (repo/docs/huggingface twins collapsed).


### Aalto University — Lecture Notes on Basic Naval Architecture (2021, CC BY)

- **slug:** `aalto-university-lecture-notes-on-basic-naval-architecture-2021-cc-by`
- **domain:** naval_architecture
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/aalto-university-lecture-notes-on-basic-naval-architecture-2021-cc-by.md`
- **member rows (1):** `aaltodoc_aalto_fi_items_8562f849_caf4_48af_9340_b981be1f64c4_60a705`
- **urls:**
  - https://aaltodoc.aalto.fi/items/8562f849-caf4-48af-9340-b981be1f64c4
- **notes (aggregated from member rows):**
  ```
  [aaltodoc_aalto_fi_items_8562f849_caf4_48af_9340_b981be1f64c4_60a705] Spyros Hirdaris. 160 pages. Ship design spiral, resistance estimation (Holtrop).
  ```

### AISHub Free Vessel Tracking API

- **slug:** `aishub-free-vessel-tracking-api`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/aishub-free-vessel-tracking-api.md`
- **member rows (1):** `aishub_api`
- **urls:**
  - https://www.aishub.net/api
- **notes (aggregated from member rows):**
  ```
  [aishub_api] Free AIS data sharing service. JSON/XML/CSV API for real-time vessel positions globally. Access requires user to stream live AIS data to AISHub. Relevant to marine operations planning, vessel tracking near offshore installations, and incident proximity analysis.
  ```

### aisstream.io WebSocket AIS Feed

- **slug:** `aisstream-io-websocket-ais-feed`
- **domain:** naval_architecture
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/aisstream-io-websocket-ais-feed.md`
- **member rows (1):** `aisstream_websocket`
- **urls:**
  - https://aisstream.io/
- **notes (aggregated from member rows):**
  ```
  [aisstream_websocket] Free WebSocket API for global real-time AIS data streaming. Vessel positions, identity, port calls. Open-source GitHub codebase. Low-latency streaming format suits event-driven agent architectures. No data contribution required unlike AISHub.
  ```

### AMPP / NACE Knowledge Hub

- **slug:** `ampp-nace-knowledge-hub`
- **domain:** materials
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/ampp-nace-knowledge-hub.md`
- **member rows (1):** `ampp_knowledge_hub`
- **urls:**
  - https://www.ampp.org/technical-research/impact/corrosion-basics
- **notes (aggregated from member rows):**
  ```
  [ampp_knowledge_hub] AMPP Knowledge Hub (2025) unifies NACE and AMPP content. Non-members access Corrosion Basics and some open articles. CORROSION journal has selective OA. Standards (SP0169 pipeline CP, SP0176 offshore CP) require purchase. Relevant to cathodic protection and corrosion modules.
  ```

### BASE (Bielefeld Academic Search Engine)

- **slug:** `base-bielefeld-academic-search-engine`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/base-bielefeld-academic-search-engine.md`
- **member rows (1):** `base_bielefeld`
- **urls:**
  - https://api.base-search.net/
- **notes (aggregated from member rows):**
  ```
  [base_bielefeld] 12,000+ content providers, 400M+ documents. OAI-PMH harvesting. HTTP API for non-commercial use. Covers grey literature, theses, and repositories not in commercial databases. Useful for offshore engineering theses and institutional preprints.
  ```

### Basilisk

- **slug:** `basilisk`
- **domain:** cfd
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/basilisk.md`
- **member rows (2):** `github_com_comphy_lab_basilisk_c_ee8eb3`, `basilisk_fr_a025bf`
- **urls:**
  - https://basilisk.fr/
  - https://github.com/comphy-lab/basilisk-C
- **notes (aggregated from member rows):**
  ```
  [github_com_comphy_lab_basilisk_c_ee8eb3] C-based with scripting via its own language. Output in VTK format for Python post-processing. Successor to Gerris; well suited for free-surface problems that complement OpenFOAM.
  
  [basilisk_fr_a025bf] C-based with scripting via its own language. Output in VTK format for Python post-processing. Successor to Gerris; well suited for free-surface problems that complement OpenFOAM.
  ```

### CalculiX

- **slug:** `calculix`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/calculix.md`
- **member rows (2):** `calculix_de_10b661`, `dhondt_de_533f1e`
- **urls:**
  - https://www.calculix.de/
  - https://www.dhondt.de/
- **notes (aggregated from member rows):**
  ```
  [calculix_de_10b661] Drive via subprocess from Python using pycalculix or custom wrappers. PrePoMax provides GUI pre/post-processing. Input deck generation can be scripted from digitalmodel geometry modules.
  
  [dhondt_de_533f1e] Drive via subprocess from Python using pycalculix or custom wrappers. PrePoMax provides GUI pre/post-processing. Input deck generation can be scripted from digitalmodel geometry modules.
  ```

### Capytaine

- **slug:** `capytaine`
- **domain:** hydrodynamics
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/capytaine.md`
- **member rows (2):** `github_com_capytaine_capytaine_2896ad`, `capytaine_github_io_stable_9f853c`
- **urls:**
  - https://capytaine.github.io/stable/
  - https://github.com/capytaine/capytaine
- **notes (aggregated from member rows):**
  ```
  [github_com_capytaine_capytaine_2896ad] pip-installable, native Python API. Outputs directly to xarray datasets. Results feed into OpenFAST/RAFT/WEC-Sim for time/frequency-domain analysis. NREL-funded development ensures alignment with OpenFAST ecosystem.
  
  [capytaine_github_io_stable_9f853c] pip-installable, native Python API. Outputs directly to xarray datasets. Results feed into OpenFAST/RAFT/WEC-Sim for time/frequency-domain analysis. NREL-funded development ensures alignment with OpenFAST ecosystem.
  ```

### Carbon Intensity API (UK National Grid)

- **slug:** `carbon-intensity-api-uk-national-grid`
- **domain:** sustainability
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/carbon-intensity-api-uk-national-grid.md`
- **member rows (1):** `carbon_intensity_uk`
- **urls:**
  - https://www.carbonintensity.org.uk/
- **notes (aggregated from member rows):**
  ```
  [carbon_intensity_uk] UK National Grid ESO real-time and forecast carbon intensity (gCO2/kWh). REST API, no auth. Useful for Scope 2 emissions calculations for UK grid-connected onshore processing and LNG facilities.
  ```

### Carbon Monitor Near-Real-Time CO2 Emissions

- **slug:** `carbon-monitor-near-real-time-co2-emissions`
- **domain:** sustainability
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/carbon-monitor-near-real-time-co2-emissions.md`
- **member rows (1):** `carbon_monitor`
- **urls:**
  - https://carbonmonitor.org/
- **notes (aggregated from member rows):**
  ```
  [carbon_monitor] Daily CO2 emission estimates since Jan 2019. Power generation (31 countries, hourly), industry, ground transport (416 cities), aviation, buildings (206 countries). Published in Nature Scientific Data. Carbon Monitor Cities: 1500-city dataset. 2025 preliminary: +0.6% YoY. No formal API; CSV download.
  ```

### Climate TRACE Facility-Level Emissions (Beta API)

- **slug:** `climate-trace-facility-level-emissions-beta-api`
- **domain:** sustainability
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/climate-trace-facility-level-emissions-beta-api.md`
- **member rows (1):** `climate_trace_api`
- **urls:**
  - https://climatetrace.org/data
- **notes (aggregated from member rows):**
  ```
  [climate_trace_api] 352M+ asset-level emissions (release v5.3.0, Jan 2025, through Nov 2025). Monthly source-level emissions for O&G sectors 2021-2025. Beta REST API: sector/owner/location search and aggregated country queries. CSV regional download available. Low volume recommended for API use.
  ```

### Code_Aster

- **slug:** `code-aster`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/code-aster.md`
- **member rows (2):** `code_aster_org_4b2dab`, `code_aster_org_1ee234`
- **urls:**
  - https://code-aster.org/
  - https://www.code-aster.org/
- **notes (aggregated from member rows):**
  ```
  [code_aster_org_4b2dab] Salome-Meca bundles geometry + meshing + solving. Python command files (.comm) can be generated programmatically. Pairs with Salome for geometry import from CAD models.
   | EDF (France) open-source FEM code. Large-scale structural, thermal, and seismic analysis. Strong nuclear/offshore heritage. Python scripting interface. Salome-Meca bundle provides pre/post processing. Mature industrial code with extensive verification. Relevant to topside structural and thermal fatigue.
  
  [code_aster_org_1ee234] Salome-Meca bundles geometry + meshing + solving. Python command files (.comm) can be generated programmatically. Pairs with Salome for geometry import from CAD models.
  ```

### CORE.ac.uk Open Research Aggregator

- **slug:** `core-ac-uk-open-research-aggregator`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/core-ac-uk-open-research-aggregator.md`
- **member rows (1):** `core_ac_uk`
- **urls:**
  - https://core.ac.uk/
- **notes (aggregated from member rows):**
  ```
  [core_ac_uk] 402M open access articles from 14,000+ repositories. Strong UK coverage (Cranfield, Imperial, Strathclyde offshore engineering). REST API with real-time metadata and full-text access. Unique for institutional repositories not indexed in commercial databases.
  ```

### Dask

- **slug:** `dask`
- **domain:** data_science
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/dask.md`
- **member rows (2):** `github_com_dask_dask_70ea2c`, `dask_org_503161`
- **urls:**
  - https://dask.org/
  - https://github.com/dask/dask
- **notes (aggregated from member rows):**
  ```
  [github_com_dask_dask_70ea2c] Drop-in parallel replacement for pandas/NumPy. Dask DataFrames partition large worldenergydata CSV/Parquet files. Dask arrays enable large-scale matrix operations in digitalmodel FEA.
  
  [dask_org_503161] Drop-in parallel replacement for pandas/NumPy. Dask DataFrames partition large worldenergydata CSV/Parquet files. Dask arrays enable large-scale matrix operations in digitalmodel FEA.
  ```

### DWSIM

- **slug:** `dwsim`
- **domain:** pipeline
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/dwsim.md`
- **member rows (2):** `github_com_danwbr_dwsim_04373d`, `dwsim_org_0ccbbd`
- **urls:**
  - https://dwsim.org/
  - https://github.com/DanWBR/dwsim
- **notes (aggregated from member rows):**
  ```
  [github_com_danwbr_dwsim_04373d] .NET/Mono based; limited direct Python integration. Can be driven via COM automation or CLI. Consider coupling with assetutilities for property calculations. Thermodynamic packages useful as reference data.
  
  [dwsim_org_0ccbbd] .NET/Mono based; limited direct Python integration. Can be driven via COM automation or CLI. Consider coupling with assetutilities for property calculations. Thermodynamic packages useful as reference data.
  ```

### EDGAR 2025 Greenhouse Gas Emissions Database

- **slug:** `edgar-2025-greenhouse-gas-emissions-database`
- **domain:** sustainability
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/edgar-2025-greenhouse-gas-emissions-database.md`
- **member rows (1):** `edgar_2025`
- **urls:**
  - https://edgar.jrc.ec.europa.eu/
- **notes (aggregated from member rows):**
  ```
  [edgar_2025] EU JRC EDGAR_2025_GHG: 1970-2024 data (published 2025). CO2, CH4, N2O, F-gases per sector/country. IPCC methodology Tier 1/2. Available via JRC Data Catalogue and World Bank Data 360. Structured NetCDF/CSV download. Reference dataset for national inventory cross-checking. URL verified live 2026-04-16; prior 404 was likely a transient issue or WAF block.
  ```

### EIA Weekly Petroleum Status Report Feed

- **slug:** `eia-weekly-petroleum-status-report-feed`
- **domain:** oil_and_gas
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/eia-weekly-petroleum-status-report-feed.md`
- **member rows (1):** `eia_petroleum_weekly`
- **urls:**
  - https://www.eia.gov/petroleum/supply/weekly/
- **notes (aggregated from member rows):**
  ```
  [eia_petroleum_weekly] Weekly US crude oil and petroleum product inventories, imports, exports, production. Published every Wednesday (delayed by one day if federal holiday). Data available via EIA API v2 under petroleum/supply series. RSS feed available. Relevant for production forecasting and market context modules.
  ```

### FEniCSx (DOLFINx)

- **slug:** `fenicsx-dolfinx`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/fenicsx-dolfinx.md`
- **member rows (2):** `github_com_fenics_dolfinx_4b2031`, `fenicsproject_org_903758`
- **urls:**
  - https://fenicsproject.org/
  - https://github.com/FEniCS/dolfinx
- **notes (aggregated from member rows):**
  ```
  [github_com_fenics_dolfinx_4b2031] Native Python API makes it straightforward to wrap inside digitalmodel modules. DOLFINx meshes can be generated from Gmsh or Salome geometry pipelines. Results exportable to XDMF/VTK for post-processing.
  
  [fenicsproject_org_903758] Native Python API makes it straightforward to wrap inside digitalmodel modules. DOLFINx meshes can be generated from Gmsh or Salome geometry pipelines. Results exportable to XDMF/VTK for post-processing.
   | FEniCSx v0.10 released October 2025. DOLFINx provides C++ and Python API for PDE-based FEM. Complex number support, wide cell types, parallel MPI. Suited to custom constitutive models and coupled physics such as cathodic protection modelling.
  ```

### Fiona

- **slug:** `fiona`
- **domain:** pipeline
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/fiona.md`
- **member rows (1):** `github_com_toblerity_fiona_ff37ff`
- **urls:**
  - https://github.com/Toblerity/Fiona
- **notes (aggregated from member rows):**
  ```
  [github_com_toblerity_fiona_ff37ff] Pythonic wrapper around OGR. Used as I/O backend by GeoPandas. Useful for streaming large spatial datasets that don't fit in memory.
  ```

### Fluids

- **slug:** `fluids`
- **domain:** pipeline
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/fluids.md`
- **member rows (1):** `github_com_calebbell_fluids_d20262`
- **urls:**
  - https://github.com/CalebBell/fluids
- **notes (aggregated from member rows):**
  ```
  [github_com_calebbell_fluids_d20262] pip-installable, pure Python. Works with thermo library for fluid properties. Comprehensive correlation library that can validate digitalmodel's pipeline calculation modules.
  ```

### FreeCAD

- **slug:** `freecad`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/freecad.md`
- **member rows (2):** `github_com_freecad_freecad_e35a7d`, `freecad_org_0c7f6c`
- **urls:**
  - https://github.com/FreeCAD/FreeCAD
  - https://www.freecad.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_freecad_freecad_e35a7d] Complete Python scripting via FreeCAD module. Can be run headless for batch geometry generation. Exports STEP/IGES for downstream FEA. Built on OpenCASCADE kernel.
  
  [freecad_org_0c7f6c] Complete Python scripting via FreeCAD module. Can be run headless for batch geometry generation. Exports STEP/IGES for downstream FEA. Built on OpenCASCADE kernel.
  ```

### GeoPandas

- **slug:** `geopandas`
- **domain:** oil_and_gas
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/geopandas.md`
- **member rows (2):** `github_com_geopandas_geopandas_765c63`, `geopandas_org_bd5fb8`
- **urls:**
  - https://geopandas.org/
  - https://github.com/geopandas/geopandas
- **notes (aggregated from member rows):**
  ```
  [github_com_geopandas_geopandas_765c63] Extends pandas with geometry column. Direct integration with worldenergydata DataFrames. Spatial indexing via rtree/pygeos. Outputs to GeoParquet for efficient storage.
  
  [geopandas_org_bd5fb8] Extends pandas with geometry column. Direct integration with worldenergydata DataFrames. Spatial indexing via rtree/pygeos. Outputs to GeoParquet for efficient storage.
  ```

### GetFEM

- **slug:** `getfem`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/getfem.md`
- **member rows (1):** `getfem_org_045775`
- **urls:**
  - https://getfem.org/
- **notes (aggregated from member rows):**
  ```
  [getfem_org_045775] Python interface via getfem module. Can be combined with Gmsh for meshing. LGPL license allows library linking without copyleft restrictions on calling code.
  ```

### Gmsh

- **slug:** `gmsh`
- **domain:** cad
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/gmsh.md`
- **member rows (1):** `gitlab_onelab_info_gmsh_gmsh_103731`
- **urls:**
  - https://gitlab.onelab.info/gmsh/gmsh
- **notes (aggregated from member rows):**
  ```
  [gitlab_onelab_info_gmsh_gmsh_103731] pip-installable Python API (gmsh module). Scriptable mesh generation from digitalmodel geometry. Outputs MSH, VTK, MED, and other formats. Linking exception allows use as a library without full GPL propagation.
  ```

### Gmsh 3D Mesh Generator

- **slug:** `gmsh-3d-mesh-generator`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/gmsh-3d-mesh-generator.md`
- **member rows (1):** `gmsh`
- **urls:**
  - https://gmsh.info/
- **notes (aggregated from member rows):**
  ```
  [gmsh] 3D FEM mesh generator with built-in pre/post processing. Latest v4.15.1 (February 2026). Python, C++, C, Julia, Fortran API. Parametric geometry, structured/unstructured/hybrid meshes, high-order elements, STL remeshing. pip install gmsh. Integrates with FEniCS, OpenFOAM, scikit-gmsh wrapper.
  ```

### https://www.dnv.com/oilgas/download/dnv-rp-c205-environmental-conditions-and-environmental-loads.html

- **slug:** `https-www-dnv-com-oilgas-download-dnv-rp-c205-environmental-conditions-and-environmental-loads-html`
- **domain:** oil_and_gas
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/https-www-dnv-com-oilgas-download-dnv-rp-c205-environmental-conditions-and-environmental-loads-html.md`
- **member rows (1):** `dnv_com_oilgas_download_dnv_rp_c205_environmental_conditions_312208`
- **urls:**
  - https://www.dnv.com/oilgas/download/dnv-rp-c205-environmental-conditions-and-environmental-loads.html
- **notes (aggregated from member rows):**
  ```
  [dnv_com_oilgas_download_dnv_rp_c205_environmental_conditions_312208] DNV-RP-C205 Environmental loads for AQWA analysis [aqwa agent]
  ```

### IEA Global Methane Tracker 2025

- **slug:** `iea-global-methane-tracker-2025`
- **domain:** sustainability
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/iea-global-methane-tracker-2025.md`
- **member rows (1):** `iea_methane_tracker`
- **urls:**
  - https://www.iea.org/data-and-statistics/data-tools/methane-tracker-data-explorer
- **notes (aggregated from member rows):**
  ```
  [iea_methane_tracker] Country and regional energy sector methane emissions, updated annually. 2025 update: country-level historical data, open-access abatement model, satellite + measurement-campaign data. Downloadable dataset CSV/Excel. No API documented. Critical for upstream O&G ESG reporting modules.
  ```

### IPCC WG1 Interactive Atlas (CMIP6 Projections)

- **slug:** `ipcc-wg1-interactive-atlas-cmip6-projections`
- **domain:** sustainability
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/ipcc-wg1-interactive-atlas-cmip6-projections.md`
- **member rows (1):** `ipcc_interactive_atlas`
- **urls:**
  - https://interactive-atlas.ipcc.ch/
- **notes (aggregated from member rows):**
  ```
  [ipcc_interactive_atlas] AR6 WG1 Interactive Atlas: CMIP5, CMIP6, CORDEX projections. 22 climate variables and indices. DataLab (Python/R) for programmatic analysis. IPCC-WGI/Atlas GitHub repo provides code and reference grids. Copernicus Interactive Climate Atlas (updated May 2025) is an alternative interface. CMIP6 projections also in Copernicus CDS.
  ```

### Kratos Multiphysics

- **slug:** `kratos-multiphysics`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/kratos-multiphysics.md`
- **member rows (2):** `github_com_kratosmultiphysics_kratos_a02f32`, `kratosmultiphysics_github_io_kratos_0de0d3`
- **urls:**
  - https://github.com/KratosMultiphysics/Kratos
  - https://kratosmultiphysics.github.io/Kratos/
- **notes (aggregated from member rows):**
  ```
  [github_com_kratosmultiphysics_kratos_a02f32] Extensive Python interface; pip-installable. Modular application design aligns with digitalmodel's module architecture. BSD license allows commercial integration.
  
  [kratosmultiphysics_github_io_kratos_0de0d3] Extensive Python interface; pip-installable. Modular application design aligns with digitalmodel's module architecture. BSD license allows commercial integration.
  ```

### lasio (LAS File I/O for Well Logs)

- **slug:** `lasio-las-file-i-o-for-well-logs`
- **domain:** data_science
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/lasio-las-file-i-o-for-well-logs.md`
- **member rows (1):** `lasio`
- **urls:**
  - https://github.com/kinverarity1/lasio
- **notes (aggregated from member rows):**
  ```
  [lasio] Python 3.7+ library for reading/writing LAS 1.2 and 2.0 files (borehole logs). Pandas DataFrame integration. Active releases (v0.32). Companion library welly adds curve/well/project management. Critical for well log data ingestion in worldenergydata.
  ```

### Maritime Optima — Sea Routes and Anti-Shipping Activity Analysis

- **slug:** `maritime-optima-sea-routes-and-anti-shipping-activity-analysis`
- **domain:** naval_architecture
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/maritime-optima-sea-routes-and-anti-shipping-activity-analysis.md`
- **member rows (1):** `maritime_optima_insights`
- **urls:**
  - https://maritimeoptima.com/insights/how-are-sea-routes-affected-by-events-and-anti-shipping-activities
- **notes (aggregated from member rows):**
  ```
  [maritime_optima_insights] Maritime Optima insights article on how geopolitical events and anti-shipping activities (e.g., Houthi Red Sea attacks, Strait of Hormuz disruptions) alter global sea routes. Maritime Optima platform provides voyage analytics, port call data, and route risk scoring. Relevant to marine ops risk, vessel routing decisions, offshore installation supply chain impact analysis, and freight market context. Full platform API available (commercial); the insights series documents real-world routing shifts useful as reference cases.
  ```

### MoorDyn Lumped-Mass Mooring Model

- **slug:** `moordyn-lumped-mass-mooring-model`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/moordyn-lumped-mass-mooring-model.md`
- **member rows (1):** `moordyn`
- **urls:**
  - https://github.com/FloatingArrayDesign/MoorDyn
- **notes (aggregated from member rows):**
  ```
  [moordyn] Lumped-mass dynamic mooring line model. Python package (moordyn on PyPI), 2025 updates. Shared library for coupling with structural codes. Used for floating wind and FPSO mooring dynamics. Addresses gap in mooring_analysis module (WRK-383 gap item).
  ```

### MoorPy (NREL Quasi-Static Mooring)

- **slug:** `moorpy-nrel-quasi-static-mooring`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/moorpy-nrel-quasi-static-mooring.md`
- **member rows (1):** `moorpy_nrel`
- **urls:**
  - https://github.com/NREL/MoorPy
- **notes (aggregated from member rows):**
  ```
  [moorpy_nrel] NREL Python library for quasi-static mooring design. Line tension, catenary shape, system stiffness matrices. Part of WETO software stack. OSTI biblio 1810090. Pairs with MoorDyn for dynamic analysis. Both fill the mooring_analysis module gap identified in WRK-383.
  ```

### MOOSE

- **slug:** `moose`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/moose.md`
- **member rows (2):** `github_com_idaholab_moose_14e2d1`, `mooseframework_inl_gov_42a9af`
- **urls:**
  - https://github.com/idaholab/moose
  - https://mooseframework.inl.gov/
- **notes (aggregated from member rows):**
  ```
  [github_com_idaholab_moose_14e2d1] Python utilities for input generation and post-processing. Physics modules (PorousFlow, TensorMechanics) map to ACE engineering domains. Input files can be templated from digitalmodel parameters.
  
  [mooseframework_inl_gov_42a9af] Python utilities for input generation and post-processing. Physics modules (PorousFlow, TensorMechanics) map to ACE engineering domains. Input files can be templated from digitalmodel parameters.
   | Idaho National Laboratory multiphysics FEM. Primary domain: nuclear, but strong geomechanics and thermal-structural modules. Python-controllable. Suited to coupled thermo-hydro-mechanical problems in wellbore and reservoir contexts.
  ```

### MRST

- **slug:** `mrst`
- **domain:** oil_and_gas
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/mrst.md`
- **member rows (2):** `github_com_sintef_appliedcompsci_mrst_b3f60d`, `sintef_no_projectweb_mrst_03c6da`
- **urls:**
  - https://github.com/SINTEF-AppliedCompSci/MRST
  - https://www.sintef.no/projectweb/mrst/
- **notes (aggregated from member rows):**
  ```
  [github_com_sintef_appliedcompsci_mrst_b3f60d] MATLAB/Octave-based; no direct Python API. Can be called from Python via Oct2Py bridge. Results exportable to formats readable by pandas/xarray. Consider OPM Flow for production Python integration instead.
  
  [sintef_no_projectweb_mrst_03c6da] MATLAB/Octave-based; no direct Python API. Can be called from Python via Oct2Py bridge. Results exportable to formats readable by pandas/xarray. Consider OPM Flow for production Python integration instead.
  ```

### NASA Prognostics Center of Excellence Data Repository

- **slug:** `nasa-prognostics-center-of-excellence-data-repository`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/nasa-prognostics-center-of-excellence-data-repository.md`
- **member rows (1):** `nasa_pcoe_data`
- **urls:**
  - https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/
- **notes (aggregated from member rows):**
  ```
  [nasa_pcoe_data] IMS bearing run-to-failure dataset (3 tests, 20 kHz, 4 bearings) and FEMTO/PRONOSTIA bearing dataset. Reference benchmarks for RUL prediction ML models. Also: battery, turbofan engine, electronics degradation. Relevant to predictive maintenance for rotating offshore equipment. Data at data.nasa.gov and Kaggle mirror.
  ```

### Nektar++

- **slug:** `nektar`
- **domain:** cfd
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/nektar.md`
- **member rows (2):** `gitlab_nektar_info_nektar_nektar_62fddc`, `nektar_info_394a79`
- **urls:**
  - https://gitlab.nektar.info/nektar/nektar
  - https://www.nektar.info/
- **notes (aggregated from member rows):**
  ```
  [gitlab_nektar_info_nektar_nektar_62fddc] Python bindings available. NekMesh utility for high-order mesh generation from CAD. MIT license allows unrestricted integration with ACE codebase.
  
  [nektar_info_394a79] Python bindings available. NekMesh utility for high-order mesh generation from CAD. MIT license allows unrestricted integration with ACE codebase.
  ```

### Netgen/NGSolve

- **slug:** `netgen-ngsolve`
- **domain:** cad
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/netgen-ngsolve.md`
- **member rows (2):** `github_com_ngsolve_ngsolve_288b5d`, `ngsolve_org_fd5181`
- **urls:**
  - https://github.com/NGSolve/ngsolve
  - https://ngsolve.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_ngsolve_ngsolve_288b5d] pip-installable. Jupyter notebook integration for interactive analysis. Python-first workflow matches digitalmodel's design philosophy. LGPL license allows library use.
  
  [ngsolve_org_fd5181] pip-installable. Jupyter notebook integration for interactive analysis. Python-first workflow matches digitalmodel's design philosophy. LGPL license allows library use.
  ```

### NOAA CO-OPS Real-Time Water Levels

- **slug:** `noaa-co-ops-real-time-water-levels`
- **domain:** hydrodynamics
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/noaa-co-ops-real-time-water-levels.md`
- **member rows (1):** `noaa_coops_realtime`
- **urls:**
  - https://tidesandcurrents.noaa.gov/
- **notes (aggregated from member rows):**
  ```
  [noaa_coops_realtime] Real-time water levels, tide predictions, currents at NOAA gauge stations. Derived Product API: extreme water level probabilities, SLR projections. JSON, CSV, XML, NetCDF output. Python py_noaa on GitHub. Critical for marine operations and tidal window planning.
  ```

### OceanWave3D

- **slug:** `oceanwave3d`
- **domain:** hydrodynamics
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/oceanwave3d.md`
- **member rows (2):** `github_com_apengsigkarup_oceanwave3d_fortran90_adcbca`, `www2_compute_dtu_dk_apek_oceanwave3d_476a9d`
- **urls:**
  - http://www2.compute.dtu.dk/~apek/OceanWave3D/
  - https://github.com/apengsigkarup/OceanWave3D-Fortran90
- **notes (aggregated from member rows):**
  ```
  [github_com_apengsigkarup_oceanwave3d_fortran90_adcbca] Fortran 90 code; no Python API. Drive via subprocess and file I/O. Can couple with OpenFOAM via waves2Foam for combined wave generation and CFD. DTU-developed research tool.
  
  [www2_compute_dtu_dk_apek_oceanwave3d_476a9d] Fortran 90 code; no Python API. Drive via subprocess and file I/O. Can couple with OpenFOAM via waves2Foam for combined wave generation and CFD. DTU-developed research tool.
  ```

### OpenAIRE EXPLORE

- **slug:** `openaire-explore`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/openaire-explore.md`
- **member rows (1):** `openaire_explore`
- **urls:**
  - https://explore.openaire.eu/
- **notes (aggregated from member rows):**
  ```
  [openaire_explore] EU open science infrastructure. Aggregates publications, datasets, software from Horizon Europe-funded projects including offshore wind, green hydrogen, and subsea projects. API at api.openaire.eu. Links publications to datasets (ScholeXplorer). FAIR-compliant metadata. Key for EU-funded offshore engineering research discovery.
  ```

### OpenAIRE Research Graph API (EU Open Research)

- **slug:** `openaire-research-graph-api-eu-open-research`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/openaire-research-graph-api-eu-open-research.md`
- **member rows (1):** `openaire_api_agent`
- **urls:**
  - https://api.openaire.eu/
- **notes (aggregated from member rows):**
  ```
  [openaire_api_agent] REST API for EU Horizon Europe-funded research outputs. Covers offshore wind, hydrogen, subsea cable, and carbon capture. Links publications to datasets (ScholeXplorer). Metadata and full-text links. Useful for EU-funded offshore engineering preprints not in commercial databases.
  ```

### OpenCASCADE / PythonOCC

- **slug:** `opencascade-pythonocc`
- **domain:** cad
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/opencascade-pythonocc.md`
- **member rows (2):** `github_com_tpaviot_pythonocc_core_504a5b`, `dev_opencascade_org_e0222f`
- **urls:**
  - https://dev.opencascade.org/
  - https://github.com/tpaviot/pythonocc-core
- **notes (aggregated from member rows):**
  ```
  [github_com_tpaviot_pythonocc_core_504a5b] PythonOCC provides full Python bindings to OCCT. pip-installable via conda-forge. Geometry can feed directly into Gmsh for meshing and then to FEA solvers. LGPL allows library use without copyleft on application code.
  
  [dev_opencascade_org_e0222f] PythonOCC provides full Python bindings to OCCT. pip-installable via conda-forge. Geometry can feed directly into Gmsh for meshing and then to FEA solvers. LGPL allows library use without copyleft on application code.
  ```

### OpenFAST

- **slug:** `openfast`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/openfast.md`
- **member rows (1):** `github_com_openfast_openfast_28c94c`
- **urls:**
  - https://github.com/OpenFAST/openfast
- **notes (aggregated from member rows):**
  ```
  [github_com_openfast_openfast_28c94c] Python interface via openfast-python. HydroDyn and MoorDyn modules can be used standalone for general offshore hydrodynamic and mooring analysis. FAST.Farm extends to wind farm scale. Apache license allows commercial use.
  ```

### OpenSees

- **slug:** `opensees`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/opensees.md`
- **member rows (2):** `github_com_opensees_opensees_62c46f`, `opensees_berkeley_edu_9f7abb`
- **urls:**
  - https://github.com/OpenSees/OpenSees
  - https://opensees.berkeley.edu/
- **notes (aggregated from member rows):**
  ```
  [github_com_opensees_opensees_62c46f] OpenSeesPy provides full Python scripting. Can be combined with digitalmodel's geotechnical modules for integrated pile-soil analysis. Output compatible with NumPy/Pandas workflows.
  
  [opensees_berkeley_edu_9f7abb] OpenSeesPy provides full Python scripting. Can be combined with digitalmodel's geotechnical modules for integrated pile-soil analysis. Output compatible with NumPy/Pandas workflows.
  ```

### OpenSees (Seismic Structural/Geotechnical FEM)

- **slug:** `opensees-seismic-structural-geotechnical-fem`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/opensees-seismic-structural-geotechnical-fem.md`
- **member rows (1):** `opensees`
- **urls:**
  - https://opensees.berkeley.edu/
- **notes (aggregated from member rows):**
  ```
  [opensees] FEM framework for seismic response of structural and geotechnical systems. Strong Python API (OpenSeesPy). Relevant to jacket structure dynamic analysis and geotechnical pile modelling. Offshore community extensions exist. Homepage moved from opensees.github.io to opensees.berkeley.edu; docs at opensees.github.io/OpenSeesDocumentation/; source at github.com/OpenSees/OpenSees.
  ```

### OpenTURNS (Uncertainty and Reliability)

- **slug:** `openturns-uncertainty-and-reliability`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/openturns-uncertainty-and-reliability.md`
- **member rows (1):** `openturns`
- **urls:**
  - https://openturns.github.io/
- **notes (aggregated from member rows):**
  ```
  [openturns] Python/C++ platform for uncertainty analysis and reliability. Monte Carlo, FORM/SORM, Kriging, polynomial chaos expansion. Relevant to structural reliability and fatigue life UQ in offshore structures.
  ```

### OPM Flow

- **slug:** `opm-flow`
- **domain:** oil_and_gas
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/opm-flow.md`
- **member rows (2):** `github_com_opm_opm_simulators_ccde4a`, `opm_project_org_20cd50`
- **urls:**
  - https://github.com/OPM/opm-simulators
  - https://opm-project.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_opm_opm_simulators_ccde4a] Python bindings via opm-python. Eclipse input format compatibility means existing industry models work directly. ResInsight provides visualization. Data pipelines from worldenergydata can feed reservoir parameters.
  
  [opm_project_org_20cd50] Python bindings via opm-python. Eclipse input format compatibility means existing industry models work directly. ResInsight provides visualization. Data pipelines from worldenergydata can feed reservoir parameters.
  ```

### Orcina OrcaFlex Documentation

- **slug:** `orcina-orcaflex-documentation`
- **domain:** orcaflex
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/orcina-orcaflex-documentation.md`
- **member rows (1):** `orcina_com_softwareproducts_orcaflex_documentation_9eb495`
- **urls:**
  - https://www.orcina.com/resources/documentation/
- **notes (aggregated from member rows):**
  ```
  [orcina_com_softwareproducts_orcaflex_documentation_9eb495] OrcaFlex Python API documentation [orcaflex agent]. Old deep-link retired; Orcina consolidated docs at /resources/documentation/ with online help browser at /webhelp/OrcaFlex/.
  ```

### OSTI.gov (DOE Scientific and Technical Information)

- **slug:** `osti-gov-doe-scientific-and-technical-information`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/osti-gov-doe-scientific-and-technical-information.md`
- **member rows (1):** `osti_gov`
- **urls:**
  - https://www.osti.gov/
- **notes (aggregated from member rows):**
  ```
  [osti_gov] 4M+ records: DOE R&D reports, journal articles, datasets, software. OAI-PMH harvesting for full-text DOE reports. DOE 2024 public access plan mandates immediate open access to publications and underlying data. Covers offshore, energy, materials, environmental sciences. MoorPy and other NREL tools here.
  ```

### Palabos

- **slug:** `palabos`
- **domain:** cfd
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/palabos.md`
- **member rows (2):** `gitlab_com_unigespc_palabos_c8f759`, `palabos_unige_ch_012ffa`
- **urls:**
  - https://gitlab.com/unigespc/palabos
  - https://palabos.unige.ch/
- **notes (aggregated from member rows):**
  ```
  [gitlab_com_unigespc_palabos_c8f759] C++ library with Python bindings. Minimal external dependencies. Can couple with digitalmodel for pore-scale analysis in reservoir characterization workflows.
  
  [palabos_unige_ch_012ffa] C++ library with Python bindings. Minimal external dependencies. Can couple with digitalmodel for pore-scale analysis in reservoir characterization workflows.
  ```

### ParaView (Python)

- **slug:** `paraview-python`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/paraview-python.md`
- **member rows (2):** `github_com_kitware_paraview_73d952`, `paraview_org_680d50`
- **urls:**
  - https://github.com/Kitware/ParaView
  - https://www.paraview.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_kitware_paraview_73d952] pvpython for scripted visualization. ParaView Catalyst for in-situ rendering during simulations. Can be scripted from digitalmodel to generate automated reports with 3D views.
  
  [paraview_org_680d50] pvpython for scripted visualization. ParaView Catalyst for in-situ rendering during simulations. Can be scripted from digitalmodel to generate automated reports with 3D views.
  ```

### Polars

- **slug:** `polars`
- **domain:** data_science
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/polars.md`
- **member rows (2):** `github_com_pola_rs_polars_31eb79`, `pola_rs_7519fe`
- **urls:**
  - https://github.com/pola-rs/polars
  - https://pola.rs/
- **notes (aggregated from member rows):**
  ```
  [github_com_pola_rs_polars_31eb79] Drop-in replacement for pandas in data-heavy pipelines. Arrow-based interchange with pandas via .to_pandas() / .from_pandas(). Consider for worldenergydata ETL pipelines processing large BSEE/SODIR datasets.
  
  [pola_rs_7519fe] Drop-in replacement for pandas in data-heavy pipelines. Arrow-based interchange with pandas via .to_pandas() / .from_pandas(). Consider for worldenergydata ETL pipelines processing large BSEE/SODIR datasets.
  ```

### PyArrow

- **slug:** `pyarrow`
- **domain:** data_science
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/pyarrow.md`
- **member rows (2):** `github_com_apache_arrow_bb32ad`, `arrow_apache_org_f22228`
- **urls:**
  - https://arrow.apache.org/
  - https://github.com/apache/arrow
- **notes (aggregated from member rows):**
  ```
  [github_com_apache_arrow_bb32ad] Backend for pandas Parquet I/O and Polars data interchange. Dataset API for reading partitioned worldenergydata archives. Arrow Flight for potential data service architecture.
  
  [arrow_apache_org_f22228] Backend for pandas Parquet I/O and Polars data interchange. Dataset API for reading partitioned worldenergydata archives. Arrow Flight for potential data service architecture.
  ```

### PyFR

- **slug:** `pyfr`
- **domain:** cfd
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/pyfr.md`
- **member rows (2):** `github_com_pyfr_pyfr_6d763e`, `pyfr_org_ab7dfa`
- **urls:**
  - https://github.com/PyFR/PyFR
  - https://www.pyfr.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_pyfr_pyfr_6d763e] Pure Python driver with GPU backends. Gmsh mesh import supported. BSD license enables commercial use. Can complement OpenFOAM for cases requiring higher-order accuracy.
  
  [pyfr_org_ab7dfa] Pure Python driver with GPU backends. Gmsh mesh import supported. BSD license enables commercial use. Can complement OpenFOAM for cases requiring higher-order accuracy.
  ```

### PyProj

- **slug:** `pyproj`
- **domain:** oil_and_gas
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/pyproj.md`
- **member rows (2):** `github_com_pyproj4_pyproj_7a8674`, `pyproj4_github_io_pyproj_eb3197`
- **urls:**
  - https://github.com/pyproj4/pyproj
  - https://pyproj4.github.io/pyproj/
- **notes (aggregated from member rows):**
  ```
  [github_com_pyproj4_pyproj_7a8674] Underlies CRS handling in GeoPandas and Rasterio. Direct use for geodetic distance calculations between platforms, wells, and pipeline nodes.
  
  [pyproj4_github_io_pyproj_eb3197] Underlies CRS handling in GeoPandas and Rasterio. Direct use for geodetic distance calculations between platforms, wells, and pipeline nodes.
  ```

### PyVista

- **slug:** `pyvista`
- **domain:** visualization
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/pyvista.md`
- **member rows (2):** `github_com_pyvista_pyvista_3b1b2e`, `pyvista_org_75bcf2`
- **urls:**
  - https://github.com/pyvista/pyvista
  - https://pyvista.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_pyvista_pyvista_3b1b2e] pip-installable. Reads VTK, STL, PLY, OBJ formats. Direct NumPy array interface. Jupyter widget for interactive exploration. Pairs with all FEA/CFD solvers that output VTK.
  
  [pyvista_org_75bcf2] pip-installable. Reads VTK, STL, PLY, OBJ formats. Direct NumPy array interface. Jupyter widget for interactive exploration. Pairs with all FEA/CFD solvers that output VTK.
  ```

### QBlade (Community Edition)

- **slug:** `qblade-community-edition`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/qblade-community-edition.md`
- **member rows (1):** `qblade_org_5c9f5a`
- **urls:**
  - https://qblade.org/
- **notes (aggregated from member rows):**
  ```
  [qblade_org_5c9f5a] CLI-driven for batch simulations. Non-commercial license restricts commercial ACE use; Enterprise Edition (QBlade-EE) available for commercial projects. Evaluate alongside OpenFAST for offshore wind analysis needs.
  ```

### QGIS (Python API)

- **slug:** `qgis-python-api`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/qgis-python-api.md`
- **member rows (2):** `github_com_qgis_qgis_f63402`, `qgis_org_adc2fb`
- **urls:**
  - https://github.com/qgis/QGIS
  - https://qgis.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_qgis_qgis_f63402] PyQGIS scripting for automation. Processing algorithms callable from standalone scripts. Useful as visualization frontend for worldenergydata spatial outputs. Plugin ecosystem extendable.
  
  [qgis_org_adc2fb] PyQGIS scripting for automation. Processing algorithms callable from standalone scripts. Useful as visualization frontend for worldenergydata spatial outputs. Plugin ecosystem extendable.
  ```

### RAFT (Response Amplitudes of Floating Turbines)

- **slug:** `raft-response-amplitudes-of-floating-turbines`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/raft-response-amplitudes-of-floating-turbines.md`
- **member rows (1):** `github_com_wisdem_raft_d6ba8f`
- **urls:**
  - https://github.com/WISDEM/RAFT
- **notes (aggregated from member rows):**
  ```
  [github_com_wisdem_raft_d6ba8f] Pure Python with NumPy/SciPy. Uses Capytaine or HAMS for BEM data. Can serve as a fast screening tool before detailed OpenFAST time-domain simulations.
  ```

### Rasterio

- **slug:** `rasterio`
- **domain:** data_science
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/rasterio.md`
- **member rows (1):** `github_com_rasterio_rasterio_4d6080`
- **urls:**
  - https://github.com/rasterio/rasterio
- **notes (aggregated from member rows):**
  ```
  [github_com_rasterio_rasterio_4d6080] Pythonic wrapper over GDAL raster functionality. NumPy array interface for raster data. Integrates with xarray via rioxarray extension for multi-dimensional analysis.
  ```

### ResInsight

- **slug:** `resinsight`
- **domain:** oil_and_gas
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/resinsight.md`
- **member rows (2):** `github_com_opm_resinsight_8623bb`, `resinsight_org_616cf0`
- **urls:**
  - https://github.com/OPM/ResInsight
  - https://resinsight.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_opm_resinsight_8623bb] Python API (rips module) for scripted post-processing. Can read Eclipse EGRID/INIT/UNRST files. Embeddable in analysis pipelines alongside worldenergydata data extraction.
  
  [resinsight_org_616cf0] Python API (rips module) for scripted post-processing. Can read Eclipse EGRID/INIT/UNRST files. Embeddable in analysis pipelines alongside worldenergydata data extraction.
  ```

### SALib (Sensitivity Analysis Library)

- **slug:** `salib-sensitivity-analysis-library`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/salib-sensitivity-analysis-library.md`
- **member rows (1):** `salib`
- **urls:**
  - https://github.com/SALib/SALib
- **notes (aggregated from member rows):**
  ```
  [salib] Sobol, Morris, FAST, DGSM, PAWN, HDMR, fractional factorial sensitivity analysis. Active PyPI. Useful for UQ in fatigue, riser, mooring simulations. JOSS paper 10.21105/joss.00097.
  ```

### Salome-Meca

- **slug:** `salome-meca`
- **domain:** cad
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/salome-meca.md`
- **member rows (1):** `salome_platform_org_0b6416`
- **urls:**
  - https://www.salome-platform.org/
- **notes (aggregated from member rows):**
  ```
  [salome_platform_org_0b6416] Full Python scripting of geometry, meshing, and solver setup. Can be run headless. Salome geometry interops with Gmsh and other meshing tools. Large learning curve but comprehensive.
  ```

### SciPy

- **slug:** `scipy`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/scipy.md`
- **member rows (2):** `github_com_scipy_scipy_1731c9`, `scipy_org_c38aca`
- **urls:**
  - https://github.com/scipy/scipy
  - https://scipy.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_scipy_scipy_1731c9] Already a core dependency. Sparse matrix support essential for FEA assembly. Optimization routines used in design optimization workflows. Signal processing for time-series analysis.
  
  [scipy_org_c38aca] Already a core dependency. Sparse matrix support essential for FEA assembly. Optimization routines used in design optimization workflows. Signal processing for time-series analysis.
  ```

### Semantic Scholar Academic Graph API

- **slug:** `semantic-scholar-academic-graph-api`
- **domain:** cad
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/semantic-scholar-academic-graph-api.md`
- **member rows (1):** `semantic_scholar_api`
- **urls:**
  - https://api.semanticscholar.org/api-docs/
- **notes (aggregated from member rows):**
  ```
  [semantic_scholar_api] 200M+ papers all disciplines. RESTful API for paper search (year, field-of- study, OA filter), author queries, citation graphs. S2AG dataset downloadable monthly. Semantic Scholar MCP server available on lobehub for direct LLM integration. No auth for basic queries.
  ```

### SfePy

- **slug:** `sfepy`
- **domain:** structural
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/sfepy.md`
- **member rows (2):** `github_com_sfepy_sfepy_12fb39`, `sfepy_org_a3f6b3`
- **urls:**
  - https://github.com/sfepy/sfepy
  - https://sfepy.org/
- **notes (aggregated from member rows):**
  ```
  [github_com_sfepy_sfepy_12fb39] pip-installable, direct NumPy/SciPy integration. Problem definitions in Python dictionaries make it easy to embed in digitalmodel calculation chains.
  
  [sfepy_org_a3f6b3] pip-installable, direct NumPy/SciPy integration. Problem definitions in Python dictionaries make it easy to embed in digitalmodel calculation chains.
  ```

### Shapely

- **slug:** `shapely`
- **domain:** data_science
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/shapely.md`
- **member rows (1):** `github_com_shapely_shapely_84e4ee`
- **urls:**
  - https://github.com/shapely/shapely
- **notes (aggregated from member rows):**
  ```
  [github_com_shapely_shapely_84e4ee] Based on GEOS library. Direct NumPy integration via vectorized operations. Foundation geometry type for all GIS operations in the ACE ecosystem.
  ```

### SU2

- **slug:** `su2`
- **domain:** cfd
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/su2.md`
- **member rows (2):** `github_com_su2code_su2_b6c716`, `su2code_github_io_6ea1df`
- **urls:**
  - https://github.com/su2code/SU2
  - https://su2code.github.io/
- **notes (aggregated from member rows):**
  ```
  [github_com_su2code_su2_b6c716] Python wrapper (SU2_CFD) and mesh tools available. Can read Gmsh and CGNS meshes. Adjoint solver enables gradient-based optimization integrated into digitalmodel design workflows.
  
  [su2code_github_io_6ea1df] Python wrapper (SU2_CFD) and mesh tools available. Can read Gmsh and CGNS meshes. Adjoint solver enables gradient-based optimization integrated into digitalmodel design workflows.
   | Open-source multiphysics PDE solver and design optimization on unstructured meshes. Aerodynamic shape optimization, compressible/incompressible flows, electrodynamics, chemically reacting flows. C++ and Python. SU2 Foundation is a registered non-profit. Active GitHub development. Complements OpenFOAM for adjoint-based shape optimization tasks.
  ```

### The Well

- **slug:** `the-well`
- **domain:** hydrodynamics
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/the-well.md`
- **member rows (3):** `the_well`, `github_com_polymathicai_the_well_f7f69e`, `huggingface_co_collections_polymathic_ai_the_well_67e129f4ca_39bbd3`
- **urls:**
  - https://github.com/PolymathicAI/the_well
  - https://huggingface.co/collections/polymathic-ai/the-well-67e129f4ca23e0447395d74c
  - https://polymathic-ai.org/the_well/
- **notes (aggregated from member rows):**
  ```
  [the_well] 15 TB physics simulation dataset covering fluid dynamics, acoustics, MHD, reaction-diffusion, and astrophysics. CC BY 4.0 data license permits commercial use with attribution. HF streaming via WellDataset avoids bulk download. Pretrained FNO/TFNO/UNet baselines available per dataset on Hugging Face (updated March 2025). Smoke test passed on dev-secondary (uv, Python 3.11).
  
  [github_com_polymathicai_the_well_f7f69e] 15 TB physics simulation dataset covering fluid dynamics, acoustics, MHD, reaction-diffusion, and astrophysics. CC BY 4.0 data license permits commercial use with attribution. HF streaming via WellDataset avoids bulk download. Pretrained FNO/TFNO/UNet baselines available per dataset on Hugging Face (updated March 2025). Smoke test passed on dev-secondary (uv, Python 3.11).
  
  [huggingface_co_collections_polymathic_ai_the_well_67e129f4ca_39bbd3] 15 TB physics simulation dataset covering fluid dynamics, acoustics, MHD, reaction-diffusion, and astrophysics. CC BY 4.0 data license permits commercial use with attribution. HF streaming via WellDataset avoids bulk download. Pretrained FNO/TFNO/UNet baselines available per dataset on Hugging Face (updated March 2025). Smoke test passed on dev-secondary (uv, Python 3.11).
  ```

### Thermo

- **slug:** `thermo`
- **domain:** pipeline
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/thermo.md`
- **member rows (1):** `github_com_calebbell_thermo_cb4e92`
- **urls:**
  - https://github.com/CalebBell/thermo
- **notes (aggregated from member rows):**
  ```
  [github_com_calebbell_thermo_cb4e92] pip-installable, pure Python. Companion library fluids provides pipe flow calculations. Direct integration with pandas DataFrames for bulk property lookups.
  ```

### TWI Job Knowledge Series

- **slug:** `twi-job-knowledge-series`
- **domain:** materials
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/twi-job-knowledge-series.md`
- **member rows (1):** `twi_job_knowledge`
- **urls:**
  - https://www.twi-global.com/technical-knowledge/job-knowledge
- **notes (aggregated from member rows):**
  ```
  [twi_job_knowledge] Welding processes, inspection, materials, and joining technology knowledge base. Free for registered users. Technical Knowledge library includes FAQs, best practice guides on weld integrity, corrosion, and inspection. No API. Relevant to weld quality and fracture mechanics modules.
  ```

### USGS Earthquake Real-Time GeoJSON Feed

- **slug:** `usgs-earthquake-real-time-geojson-feed`
- **domain:** naval_architecture
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/usgs-earthquake-real-time-geojson-feed.md`
- **member rows (1):** `usgs_eq_geojson`
- **urls:**
  - https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
- **notes (aggregated from member rows):**
  ```
  [usgs_eq_geojson] Real-time GeoJSON feeds by time window and magnitude threshold. FDSN event API for historical queries. No auth. Relevant to offshore geohazard monitoring, seabed instability, and subsea infrastructure risk assessment.
  ```

### Vaex

- **slug:** `vaex`
- **domain:** data_science
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/vaex.md`
- **member rows (2):** `github_com_vaexio_vaex_819f43`, `vaex_io_e026f2`
- **urls:**
  - https://github.com/vaexio/vaex
  - https://vaex.io/
- **notes (aggregated from member rows):**
  ```
  [github_com_vaexio_vaex_819f43] HDF5 and Arrow backends for zero-copy data access. Useful for interactive exploration of large BSEE datasets. Note: community is smaller than Polars/Dask; evaluate long-term maintenance.
  
  [vaex_io_e026f2] HDF5 and Arrow backends for zero-copy data access. Useful for interactive exploration of large BSEE datasets. Note: community is smaller than Polars/Dask; evaluate long-term maintenance.
  ```

### wavespectra (Ocean Wave Spectra Library)

- **slug:** `wavespectra-ocean-wave-spectra-library`
- **domain:** hydrodynamics
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/wavespectra-ocean-wave-spectra-library.md`
- **member rows (1):** `wavespectra`
- **urls:**
  - https://github.com/wavespectra/wavespectra
- **notes (aggregated from member rows):**
  ```
  [wavespectra] xarray-based Python library for ocean wave spectral data. v4.4.2 (March 2025). 15+ format readers: WW3, SWAN, ERA5, NDBC. 60+ spectral parameter methods. Partitioning: PTM1-5, watershed, wave age. Directly fills wave_spectra gap in digitalmodel/hydrodynamics and metocean module (see WRK-383). MIT, 20 contributors.
  ```

### WEC-Sim

- **slug:** `wec-sim`
- **domain:** hydrodynamics
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/wec-sim.md`
- **member rows (2):** `github_com_wec_sim_wec_sim_bbb849`, `wec_sim_github_io_wec_sim_2d2c8b`
- **urls:**
  - https://github.com/WEC-Sim/WEC-Sim
  - https://wec-sim.github.io/WEC-Sim/
- **notes (aggregated from member rows):**
  ```
  [github_com_wec_sim_wec_sim_bbb849] MATLAB/Simulink-based; no direct Python API. Uses BEM data from Capytaine/HAMS/WAMIT. For Python-native workflows, consider using Capytaine + custom time-domain solvers or OpenFAST HydroDyn module instead.
  
  [wec_sim_github_io_wec_sim_2d2c8b] MATLAB/Simulink-based; no direct Python API. Uses BEM data from Capytaine/HAMS/WAMIT. For Python-native workflows, consider using Capytaine + custom time-domain solvers or OpenFAST HydroDyn module instead.
  ```

### Whitson+

- **slug:** `whitson`
- **domain:** oil_and_gas
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/whitson.md`
- **member rows (2):** `github_com_whitson_org_01e0c5`, `whitson_com_0238dd`
- **urls:**
  - https://github.com/whitson-org
  - https://whitson.com/
- **notes (aggregated from member rows):**
  ```
  [github_com_whitson_org_01e0c5] Python-native where available. Check individual repo licenses before integration. PVT calculations can feed into assetutilities fluid property modules. GitHub organization whitson-org no longer exists; Whitson is now a commercial SaaS platform at whitson.com with no public GitHub presence.
  
  [whitson_com_0238dd] Python-native where available. Check individual repo licenses before integration. PVT calculations can feed into assetutilities fluid property modules.
  ```

### Zenodo Research Repository

- **slug:** `zenodo-research-repository`
- **domain:** marine
- **status:** create (net-new wiki entity)
- **target path (downstream):** `knowledge/wikis/engineering/wiki/entities/zenodo-research-repository.md`
- **member rows (1):** `zenodo`
- **urls:**
  - https://zenodo.org/
- **notes (aggregated from member rows):**
  ```
  [zenodo] CERN/OpenAIRE repository. DOI-minted papers, datasets, software. REST API at zenodo.org/api/records. Hosts MoorPy, wavespectra, and many engineering datasets. Search by keyword: "offshore", "fatigue", "corrosion", "mooring". CC licences. Good for published datasets accompanying journal papers.
  ```

---

## Extend-only — exact matches to existing wiki entities

4 packages have an existing `entities/<slug>.md`. Downstream ingest should 
MERGE new fields (aggregated notes, URLs) without overwriting existing prose.

| Package root | Slug | Existing entity file | Members |
|---|---|---|---|
| BEMRosetta | `bemrosetta` | `knowledge/wikis/engineering/wiki/entities/bemrosetta-tool.md` | github_com_bemrosetta_bemrosetta_77615d |
| CadQuery | `cadquery` | `knowledge/wikis/engineering/wiki/entities/cadquery.md` | github_com_cadquery_cadquery_4e7f72 |
| OpenFOAM | `openfoam` | `knowledge/wikis/engineering/wiki/entities/openfoam-cfd.md` | gitlab_com_openfoam_core_openfoam_3e2868 |
| OpenFOAM (OpenCFD / ESI fork) | `openfoam-opencfd-esi-fork` | `knowledge/wikis/engineering/wiki/entities/openfoam-cfd.md` | openfoam_esi |
