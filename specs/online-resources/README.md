# Online Resources Catalog — WRK-391

**Generated:** 2026-02-24
**Catalog file:** `specs/online-resources/catalog.yaml`
**Total entries:** 83 resources across 9 categories

This catalog is a horizon-expanding discovery exercise — not an inventory of
familiar sources. It surfaces resources that fill capability gaps, enable agents
to reach beyond the local library, and identify unexplored adjacent domains.

---

## Category Summary

| Category | Count | Key Use |
|---|---|---|
| Open Data APIs | 17 | Live data for agents at task time |
| Open-Source Tools | 14 | Module dependencies and integrations |
| Professional Body Sources | 10 | Standards and engineering literature |
| Academic Repositories | 9 | Open-access research and datasets |
| Real-Time Operational Feeds | 8 | Live operational data for agents |
| AI / Agent Resources | 10 | MCP ecosystem and agent tooling |
| Sustainability / ESG / Carbon | 7 | Emerging adjacent domain |
| Engineering Standards Portals | 7 | Standards and regulatory portals |
| Physics / ML Datasets | 1 | The Well (WRK-393 evaluated) |

---

## Top 5 Resources Per Category

### Category 1 — Engineering Standards and Codes Portals

1. **DNV Rules and Standards Explorer** (`dnv_standards_explorer`) — Free full-text
   access to 650+ DNV rules. July 2025 edition in force. Amendment notifications built-in.
   Score: 5/5.

2. **API Standards Addenda and Errata Portal** (`api_addenda_errata`) — Free
   addenda and errata for all API standards. 2025 updates to API STD 620 and
   API Spec Q1. Essential for standards currency. Score: 5/5.

3. **IOGP Publications Library** (`iogp_publications`) — 200+ freely downloadable
   safety and process safety publications. The largest HSE incident database in
   the industry. Score: 5/5.

4. **IACS Unified Requirements and Blue Book** (`iacs_unified_requirements`) — All
   IACS URs and UIs freely downloadable including the complete Blue Book. Score: 4/5.

5. **NSTA UK National Data Repository** (`nsta_uk_ndr`) — 400+ GB of freely
   available UK North Sea exploration data. December 2025 carbon storage licensing
   round opened. Score: 4/5.

### Category 2 — Open Data APIs

1. **EIA Open Data API v2** (`eia_api_v2`) — Full RESTful API (v2.1.10, October 2025)
   covering all US energy data. Hierarchical dataset discovery. Free key required.
   Score: 5/5.

2. **SODIR / NPD FactPages REST API** (`sodir_factpages`) — Norwegian Continental
   Shelf data synchronised daily. REST/OData endpoints. 30,000+ public datasets.
   Score: 5/5.

3. **Copernicus Climate Data Store (CDS) API** (`copernicus_cds`) — ERA5 reanalysis
   1940-present with new ecmwf-datastores-client. CMIP6 projections also available.
   Score: 5/5.

4. **Copernicus Marine Service (CMEMS)** (`cmems_marine_service`) — Free global ocean
   physics, wave, and salinity products. Wave multi-year extended to 1967 in 2025.
   Score: 5/5.

5. **NOAA NDBC** (`noaa_ndbc`) — Real-time and historical buoy data via THREDDS/
   OPeNDAP. Python ndbc-api. Cloud-native Zarr via NOAA NODD. Score: 5/5.

### Category 3 — Open-Source Engineering Tool Ecosystems

1. **wavespectra** (`wavespectra`) — xarray-based wave spectra library, v4.4.2 (2025).
   15+ format readers, 60+ spectral methods. Directly fills the wave_spectra module
   gap in WRK-383. Score: 5/5.

2. **Gmsh 3D Mesh Generator** (`gmsh`) — v4.15.1, Python API, parametric geometry,
   high-order elements. Critical for FEA pre-processing across structural and
   hydrodynamic modules. Score: 4/5.

3. **MoorDyn** (`moordyn`) — Lumped-mass mooring dynamic model. Python package
   (PyPI, 2025 updates). Addresses the mooring_analysis module gap (WRK-383).
   Score: 4/5.

4. **MoorPy** (`moorpy_nrel`) — NREL quasi-static mooring design library. Stiffness
   matrices, catenary profiles. Pairs with MoorDyn. OSTI-published. Score: 4/5.

5. **lasio** (`lasio`) — LAS 1.2/2.0 file I/O for well logs. Active releases,
   pandas integration. Critical for well log ingestion in worldenergydata. Score: 4/5.

### Category 4 — Academic and Research Paper Repositories

1. **Semantic Scholar Academic Graph API** (`semantic_scholar_api`) — 200M+ papers.
   RESTful API with open-access filter. No auth for basic use. MCP server available
   for direct LLM integration. Score: 4/5.

2. **Zenodo** (`zenodo`) — DOI-minted research repository. REST API at /api/records.
   Hosts MoorPy, wavespectra, engineering datasets. Score: 4/5.

3. **OSTI.gov** (`osti_gov`) — 4M+ DOE R&D records. OAI-PMH harvesting. Immediate
   open access per 2024 DOE public access plan. Score: 4/5.

4. **arXiv cs.CE** (`arxiv_cs_ce`) — Active computational engineering preprint feed.
   Atom/JSON API by category. Adjacent: physics.geo-ph, eess.SP. Score: 4/5.

5. **DOAJ Offshore / Marine Journals** (`doaj_offshore_journals`) — Fully open-access
   peer-reviewed journals: IJNAOE, IJCOE, JMSE, JOES, JNAME. DOAJ API for search.
   Score: 4/5.

### Category 5 — Professional Body and Conference Paper Sources

1. **IOGP Publications Library** (`iogp_publications`) — 200+ free publications.
   Annual safety KPI data, well control incidents, PSE statistics. Score: 5/5.

2. **SPE OnePetro** (`spe_onepetro`) — 80,000+ papers. Gold OA tier, Distinguished
   Lecturer slides free at dl.spe.org. Abstract search free. Score: 5/5.

3. **ASME JOMAE / OMAE** (`asme_jomae_omae`) — Premier offshore engineering journal
   and conference (OMAE 2025 Vancouver). ASME explicit OA program; gold OA flagged
   per article. Score: 5/5.

4. **ISOPE** (`isope`) — 35th ISOPE 2025, Seoul. Abstract pages free at isope.org.
   Historically one of the most accessible offshore conferences. Score: 4/5.

5. **OTC / OTC Brasil / OTC Asia** (`otc_onepetro`) — Largest offshore industry
   conference globally. Abstracts free; 2025 papers indexed from May 2025. Score: 4/5.

### Category 6 — Real-Time Operational Data Feeds

1. **Open-Meteo Marine Weather API** (`open_meteo_realtime`) — No API key or
   registration. Wave height, period, swell separation. 16-day global forecast.
   Ideal for agent weather-window queries. Score: 5/5.

2. **NOAA CO-OPS Real-Time Water Levels** (`noaa_coops_realtime`) — REST API for
   tides, currents, storm surge. Derived Product API for SLR projections and extreme
   water level probabilities. Score: 4/5.

3. **Climate TRACE Facility-Level Emissions API** (`climate_trace_api`) — 352M+
   asset-level emissions. Beta REST API. O&G sector monthly 2021-2025. Score: 4/5.

4. **USGS Earthquake Real-Time GeoJSON Feed** (`usgs_eq_geojson`) — Real-time seismic
   events globally. FDSN REST API for historical queries. Offshore geohazard
   monitoring. Score: 3/5.

5. **aisstream.io WebSocket AIS Feed** (`aisstream_websocket`) — Free WebSocket API
   for global vessel tracking. No data contribution requirement. Agent-friendly
   streaming format. Score: 3/5.

### Category 7 — Sustainability, ESG, and Carbon Data

1. **Climate TRACE Open Emissions Registry** (`climate_trace_registry`) — 352M+
   assets, O&G facility-level emissions, beta REST API. CC BY 4.0. Score: 4/5.

2. **Global Registry of Fossil Fuels** (`fossil_fuel_registry`) — 50,000+ fields,
   89 countries. Full scope 1/2/3 lifecycle model (38 MB). Carbon intensity model
   for 3340 projects. CC BY-SA. Score: 4/5.

3. **EDGAR 2025 GHG Emissions Database** (`edgar_2025`) — EU JRC reference dataset
   1970-2024. CO2, CH4, N2O, F-gases by sector/country. Published 2025. Score: 4/5.

4. **IEA Global Methane Tracker 2025** (`iea_methane_tracker`) — Country-level energy
   sector methane estimates. Open-access abatement model. CC BY 4.0. Score: 4/5.

5. **IPCC WG1 Interactive Atlas** (`ipcc_interactive_atlas`) — CMIP6 projections,
   DataLab Python/R access. Copernicus Interactive Climate Atlas updated May 2025.
   Score: 3/5.

### Category 8 — AI / Agent Skill Resources and MCP Ecosystem

1. **MCP Official Registry** (`mcp_official_registry`) — Official Anthropic-backed
   registry at registry.modelcontextprotocol.io. ~2000 servers, programmatic API.
   Donated to Linux Foundation AAIF December 2025. Score: 5/5.

2. **Awesome MCP Servers** (`awesome_mcp_servers`) — Curated GitHub community list.
   Companion to official registry. 270+ remote servers at mcpservers.org. Score: 5/5.

3. **wavespectra** (`wavespectra_agent`) — See Category 3. Highest direct module
   integration value. Fills wave_spectra gap immediately. Score: 5/5.

4. **Semantic Scholar MCP Server** (`semantic_scholar_mcp`) — MCP server for 200M+
   paper search from within Claude Code. Direct LLM integration for engineering
   literature retrieval. Score: 4/5.

5. **MoorPy** (`moorpy_agent`) — See Category 3. Addresses mooring_analysis module
   gap with NREL-backed quasi-static mooring design tool. Score: 4/5.

---

## Module Gap Coverage (per WRK-383)

| WRK-383 Gap | Resources Identified |
|---|---|
| CP module (no cathodic protection module) | AMPP/NACE Knowledge Hub, TWI Job Knowledge Series |
| Mooring analysis (subsea/mooring_analysis) | MoorDyn, MoorPy, OpenMoor, MoorPy NREL |
| Wave spectra (hydrodynamics/wave_spectra) | wavespectra v4.4.2, CMEMS wave multi-year |
| Safety analysis (marine_safety) | IMO GISIS, NTSB CAROL, IOGP publications |
| Well bore design | lasio, ANP BDEP, SODIR/NPD well data |
| ESG/Carbon (no current module) | Climate TRACE, EDGAR, IEA Methane Tracker, GRFF |
| Geomechanics (no current module) | OpenGeoSys, MOOSE INL |

---

## New Discoveries — Things We Did Not Know Existed

These are resources not previously in scope for the ecosystem and represent the
highest-leverage findings from this research:

### 1. wavespectra (Python wave spectra library)
URL: https://github.com/wavespectra/wavespectra
Directly fills the `wave_spectra` module gap in `digitalmodel/hydrodynamics` and
`worldenergydata/metocean`. 15+ format readers (ERA5, WW3, SWAN, NDBC), 60+ spectral
parameter methods, xarray-based. v4.4.2 released March 2025. This is an immediate
integration candidate requiring no new code — just `pip install wavespectra`.

### 2. MoorDyn + MoorPy (open mooring dynamics and quasi-statics)
URLs: github.com/FloatingArrayDesign/MoorDyn, github.com/NREL/MoorPy
Both address the WRK-383-identified mooring gap. MoorPy
(NREL) is published on OSTI and is part of the Wind Energy Technology Office software
stack — meaning it is actively maintained with US DOE backing. MoorDyn covers dynamics;
MoorPy covers quasi-statics. Together they provide a complete open-source mooring
capability.

### 3. Open-Meteo Marine API (zero-auth weather queries)
URL: https://open-meteo.com/en/docs/marine-weather-api
No API key, no registration, no cost, AGPLv3 open source. Provides ocean wave
forecasts (Hs, Tp, direction, swell separation) globally at 1-11 km resolution,
16-day horizon, as a simple JSON REST API. This is the ideal weather-window query
tool for agent use — zero integration overhead.

### 4. Climate TRACE Facility-Level O&G Emissions API
URL: https://climatetrace.org/data
352M+ assets with monthly O&G sector emissions 2021-2025. The only resource
identified that provides facility-level emissions data accessible via a (beta)
REST API. This is the foundation of a future ESG/carbon module and is entirely
unknown to the current ecosystem. CC BY 4.0.

### 5. Global Registry of Fossil Fuels (Carbon Tracker)
URL: https://fossilfuelregistry.org/
First open-source global database of O&G and coal assets in CO2-equivalent.
50,000+ fields, 89 countries. The O&G Supply Chain Carbon Intensity Model
ranks 3,340 oil and gas projects by carbon intensity. This directly enables
stranded-asset analysis and ESG benchmarking — a natural future module.

### 6. IACS Unified Requirements (Blue Book — fully free)
URL: https://iacs.org.uk/publications/unified-requirements/
It was not previously known that the complete IACS Blue Book (all Unified
Requirements and Unified Interpretations from all classification societies) is
freely downloadable. This is the common denominator for LR, BV, DNV, ABS,
ClassNK, GL, Bureau Veritas rules. UR E26/27 (2024) on cybersecurity for ships
is a notable recent addition.

### 7. DOAJ Fully Open-Access Offshore Engineering Journals
URL: https://doaj.org/
Multiple fully open-access peer-reviewed offshore/marine journals discovered:
International Journal of Naval Architecture and Ocean Engineering; International
Journal of Coastal and Offshore Engineering; Journal of Marine Science and
Engineering; Journal of Ocean Engineering and Science. All are free to read with
no subscription. The DOAJ API at doaj.org/api/ enables programmatic article search.

### 8. Semantic Scholar MCP Server
URL: https://lobehub.com/mcp/fujishigetemma-semantic-scholar-mcp
An MCP server wrapping the Semantic Scholar Academic Graph API for 200M+ papers.
This means Claude Code agents can search engineering literature directly from within
the workspace-hub agent workflow. **Supply-chain note:** third-party MCP servers
should be reviewed for trust, version-pinned, and run with least-privilege
permissions before installation into production workflows.

### 9. MCP Official Registry (registry.modelcontextprotocol.io)
URL: https://registry.modelcontextprotocol.io
Launched September 2025. ~2000 MCP servers with programmatic discovery API.
The registry was donated to the Agentic AI Foundation (Linux Foundation) in
December 2025. This is the canonical source for discovering new agent capabilities
and should be consulted before building any new skill from scratch.

### 10. FEniCS DOLFINx v0.10 + OpenGeoSys
FEniCSx v0.10 (October 2025) and OpenGeoSys both provide Python-first FEM
capabilities not previously tracked. FEniCSx enables custom constitutive models
(e.g., cathodic protection field modelling). OpenGeoSys covers THMC processes
critical to wellbore integrity and CO2 storage simulation.

---

## Access Model Summary

| Access Tier | Count | Examples |
|---|---|---|
| Completely free, no auth | 62 | Open-Meteo, GEBCO, USGS, EDGAR, wavespectra, Gmsh, MoorDyn |
| Free with registration/key | 9 | EIA, CDS, CMEMS, NDBC, Earthdata, aisstream |
| Member/subscription (abstract free) | 10 | SPE, ASME, RINA, SNAME, DNV Explorer+, AMPP |
| Contribution-based free | 1 | AISHub |
| Consortium membership | 1 | OSDU |

---

## Agentic Integration Priority

Resources most immediately actionable for agent integration (no code required,
no subscription, relevant API or pip package exists):

1. `open_meteo_realtime` — zero-auth real-time marine weather JSON API
2. `wavespectra` — `pip install wavespectra`, fills wave_spectra module gap
3. `usgs_eq_geojson` — real-time geohazard GeoJSON feed, no auth
4. `noaa_coops_realtime` — real-time tides and currents REST API, no auth
5. `semantic_scholar_mcp` — MCP server for 200M+ paper search
6. `mcp_official_registry` — discover new MCP servers programmatically
7. `climate_trace_api` — beta REST API for O&G facility emissions
8. `moorpy_nrel` — `pip install moorpy` (NREL), fills mooring gap

---

*Catalog: `specs/online-resources/catalog.yaml` | Follow-on: `specs/online-resources/follow-on-candidates.md`*
*Source WRK: WRK-391 | Related: WRK-383, WRK-309, WRK-393*
