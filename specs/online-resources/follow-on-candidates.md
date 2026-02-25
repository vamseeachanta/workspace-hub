# Follow-On WRK Candidates — WRK-391 Research Outputs

**Generated:** 2026-02-24
**Source:** WRK-391 Online Resources Research

Prioritised list of actionable follow-on WRK items identified during the
horizon-scanning research mission. Each item represents a concrete capability
unlock or module gap closure.

---

## Priority 1 — Immediate Module Gap Closures (high value, low effort)

### WRK-WAVE-1: Integrate wavespectra into digitalmodel/hydrodynamics
**Resource:** `wavespectra` v4.4.2 (MIT, pip-installable)
**Rationale:** WRK-383 identified `hydrodynamics/wave_spectra` as a gap module.
wavespectra provides the complete solution: 15+ format readers (ERA5, WW3, SWAN,
NDBC), 60+ spectral parameter methods, xarray-native, active community. No new
algorithm code needed — the library already implements JONSWAP/PM fitting and
spectral partitioning. Effort: low (dependency addition + thin module wrapper).
**Related resources:** `wavespectra`, `wavespectra_agent`

### WRK-MOOR-1: Integrate MoorDyn + MoorPy into digitalmodel/subsea/mooring_analysis
**Resource:** MoorDyn (BSD-3, PyPI), MoorPy (BSD, NREL/OSTI)
**Rationale:** WRK-383 identified no mooring dynamics module. MoorDyn provides
lumped-mass mooring line dynamics; MoorPy provides quasi-static design. Together
they cover the full mooring analysis workflow: pre-design (MoorPy) → dynamic
verification (MoorDyn). NREL DOE backing gives long-term maintenance confidence.
Effort: medium (module wrapper + test cases against API RP 2SK scenarios).
**Related resources:** `moordyn`, `moorpy_nrel`, `moorpy_agent`

### WRK-METEO-1: Wire Open-Meteo Marine API into marine_ops weather-window module
**Resource:** Open-Meteo Marine Weather API (free, no key, JSON REST)
**Rationale:** No authentication, no registration, no cost. Returns Hs, Tp, wave
direction, swell separation for any global coordinate as JSON. Ideal drop-in for
weather-window calculations in `marine_ops/marine_analysis`. Agents can call it
directly at task time without credential management. Effort: very low (single API
call, JSON parsing, unit conversion).
**Related resources:** `open_meteo_marine`, `open_meteo_realtime`

---

## Priority 2 — New Module Creation (medium effort, high strategic value)

### WRK-ESG-1: Create ESG/Carbon Emissions Module using Climate TRACE + EDGAR + GRFF
**Resources:** Climate TRACE (beta API), EDGAR 2025 (structured download), Global
Registry of Fossil Fuels (CC BY-SA model), IEA Methane Tracker (CC BY 4.0)
**Rationale:** No ESG/carbon module currently exists in the workspace-hub ecosystem.
Climate TRACE provides facility-level O&G emissions via a REST API. EDGAR provides
national reference inventories. The Global Registry of Fossil Fuels provides
stranded-asset and carbon intensity analysis for 50,000+ fields. This is a natural
extension given the existing upstream O&G modules. Together these three sources
form a complete ESG data stack.
**Scope:** module in `worldenergydata/esg_carbon/` covering: (a) facility-level
emission lookup via Climate TRACE API, (b) national inventory comparison via EDGAR,
(c) asset-level carbon intensity via GRFF model.
**Related resources:** `climate_trace_api`, `climate_trace_registry`, `edgar_2025`,
`iea_methane_tracker`, `fossil_fuel_registry`

### WRK-GEOHAZ-1: Create Offshore Geohazard Feed Module using USGS Earthquake API
**Resource:** USGS Earthquake Hazards FDSN API (free, no auth, real-time + historical)
**Rationale:** No geohazard module exists. Offshore seismic risk is relevant to
subsea infrastructure design, site assessment, and insurance. The USGS FDSN API
provides real-time GeoJSON feeds and historical parametric queries (magnitude, depth,
region, time). A thin module in `worldenergydata/safety_analysis/geohazard` could
provide seismic hazard lookups by geographic bounding box for any offshore location.
Effort: low (thin API wrapper + radius queries around offshore asset coordinates).
**Related resources:** `usgs_earthquake_feed`, `usgs_eq_geojson`, `usgs_sciencebase`

### WRK-CP-1: Create Cathodic Protection Module — gap identified in WRK-383
**Resources:** AMPP/NACE Knowledge Hub (SP0169, SP0176), TWI Job Knowledge Series,
DNV-RP-B401 (free viewer), FEniCSx (custom CP field modelling)
**Rationale:** WRK-383 explicitly flagged `subsea/` cathodic protection as a gap
(no CP module; reference DNV-RP-B401). AMPP Knowledge Hub provides standards
context. FEniCSx enables custom CP field simulation (electrochemical potential
distribution in seawater). This is a significant gap: every subsea structure
requires CP design verification.
**Scope:** module in `digitalmodel/subsea/cp_analysis` covering: (a) CP current
demand calculations per DNV-RP-B401, (b) anode design (bracelet/flush/stand-off),
(c) optional FEniCSx boundary element model for complex geometries.
**Related resources:** `ampp_knowledge_hub`, `twi_job_knowledge`, `fenics_dolfinx`

---

## Priority 3 — Data Source Wiring (straightforward, significant data value)

### WRK-NORWAY-1: Wire SODIR FactPages OData API into worldenergydata/sodir
**Resource:** SODIR / NPD FactPages REST/OData API (free, 30,000+ datasets)
**Rationale:** The worldenergydata/sodir module exists but the scope of the SODIR
open data is substantially larger than what the module currently ingests. The Diskos
NDR (cloud, Landmark) now exposes an open API covering well data, production, seismic,
and relinquished-area datasets. Enumerating and ingesting the full FactPages dataset
catalog would significantly expand coverage. 6000 additional relinquished-area
datasets are now public.
**Scope:** Audit all SODIR FactPages/FactMaps OData endpoints; extend module schema
to cover new dataset types; add scheduled update pipeline.
**Related resources:** `sodir_factpages`

### WRK-CMEMS-1: Integrate CMEMS Wave Multi-Year Product into worldenergydata/metocean
**Resource:** CMEMS Wave Multi-Year (1967-2025, first backward extension released 2025)
**Rationale:** The CMEMS wave multi-year product now extends back to 1967 — a 58-year
hindcast covering the offshore industry's full operational history. The June 2025
release cycle extended the IBI area product with monthly batch updates. This provides
a longer wave climate baseline than ERA5 (1940) in the sense of having dedicated
ocean-wave physics. Integration into the metocean module would improve extreme wave
statistics and return period calculations.
**Related resources:** `cmems_marine_service`

### WRK-BATHYM-1: Integrate GEBCO_2025 Bathymetry into subsea pipeline routing
**Resource:** GEBCO_2025 Grid (15 arc-second, published August 2025, OPeNDAP access)
**Rationale:** GEBCO_2025 is the 7th Seabed 2030 grid and the most current global
bathymetric dataset. OPeNDAP subset access at download.gebco.net enables programmatic
extraction for any bounding box. Integration into subsea pipeline routing and
installation planning would enable agents to query water depths automatically.
**Related resources:** `gebco_2025_bathymetry`

---

## Priority 4 — MCP Ecosystem Expansion (agent capability, self-referential)

### WRK-MCP-1: Audit Official MCP Registry for Engineering-Domain Servers
**Resource:** registry.modelcontextprotocol.io (programmatic API, ~2000 servers)
**Rationale:** The official MCP registry launched September 2025 and now holds ~2000
servers, with the programmatic API enabling automated scanning. A systematic audit
of the registry for engineering-domain servers (geospatial, scientific data, unit
conversion, weather, structural analysis) would identify servers that can be installed
into workspace-hub with zero integration code. The Semantic Scholar MCP server is
already identified as an immediate candidate.
**Scope:** Write a skill that queries the MCP registry API, filters by engineering-
relevant keywords, and produces a priority-ranked install list.
**Related resources:** `mcp_official_registry`, `awesome_mcp_servers`,
`mcpmarket_catalog`, `semantic_scholar_mcp`

### WRK-LIT-1: Install Semantic Scholar MCP Server for Agent Literature Search
**Resource:** Semantic Scholar MCP Server (free, no auth, 200M+ papers, OA filter)
**Rationale:** Currently agents have no direct path to engineering literature from
within a task. The Semantic Scholar MCP server enables direct paper search (by
topic, year, field-of-study, open-access only) without leaving the agent context.
This is a zero-code capability unlock: install the MCP server, configure in settings.
Immediate benefit for WRK items requiring literature-backed design decisions.
**Related resources:** `semantic_scholar_mcp`, `semantic_scholar_api`

---

## Priority 5 — Academic and Reference Expansion

### WRK-OA-1: Map Open-Access Journal Portfolio for Engineering Domains
**Resource:** DOAJ API (doaj.org/api/), CORE.ac.uk API, OpenAIRE API
**Rationale:** Multiple fully open-access offshore/marine engineering journals
were discovered that are not currently in scope: IJNAOE, IJCOE, JMSE, JOES,
JNAME. Together they represent hundreds of freely accessible peer-reviewed papers.
A systematic mapping using DOAJ API would identify all OA journals relevant to
the workspace-hub module set, enabling agents to retrieve authoritative full-text
references without subscription barriers.
**Scope:** Use DOAJ API to enumerate OA journals by subject keywords; cross-reference
with module list from WRK-383; produce a per-module OA journal registry.
**Related resources:** `doaj_offshore_journals`, `core_ac_uk`, `openaire_explore`

### WRK-ESG-2: Evaluate IEA Methane Tracker for Upstream O&G ESG Module
**Resource:** IEA Global Methane Tracker 2025 (CC BY 4.0, country-level, downloadable)
**Rationale:** The 2025 update of the IEA Methane Tracker adds country-level historical
emissions data and an open-access abatement model. The data provides a critical
reference for upstream O&G operators implementing methane reduction initiatives.
This is a natural complement to the Climate TRACE facility-level data and EDGAR
national inventories. Evaluate integration into a future `worldenergydata/esg_carbon`
module.
**Related resources:** `iea_methane_tracker`

---

## Additional Candidates (to investigate further)

| Candidate | Resource | Action |
|---|---|---|
| Geomechanics module | OpenGeoSys, MOOSE INL | Feasibility assessment for wellbore integrity |
| ANP Brazil production | ANP BDEP, re3data r3d100010989 | Verify REST API availability |
| NSTA UK exploration data | NSTA NDR (400+ GB) | Index available datasets; add to worldenergydata |
| IRENA offshore wind data | IRENASTAT | Add offshore wind capacity to energy mix module |
| IACS Blue Book automation | iacs.org.uk/publications | Auto-fetch UR updates for standards currency |
| Code_Aster structural | code-aster.org | Evaluate for large-scale topside structural FEA |
| OpenTURNS reliability | openturns.github.io | Integrate with fatigue reliability module |

---

*Source WRK: WRK-391 | Catalog: `specs/online-resources/catalog.yaml`*
*Related: WRK-383 (standards-to-module map), WRK-309 (document index)*
