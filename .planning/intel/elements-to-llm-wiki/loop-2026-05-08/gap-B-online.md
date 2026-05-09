# LLM-Wiki External-Source Gap Analysis (Track B: online-public)

**Date:** 2026-05-08
**Method:** Per-domain inventory of existing sources/standards/concepts pages cross-referenced against verified online authorities; URLs validated via WebSearch 2026-05-08.
**Exclusions (already covered or in-flight):** API design, asset-management foundations, DNV-OS-E301/F101, ASME B31.4/B31.8, ABS rules, ISO 19900, naval-arch foundations, riser sub-domain, NACE/AMPP corrosion (W4), BSI subset (W4), maritime-law foundations, engineering audit (W1-W3, issues #2586-#2597). Also excluded: LinkedIn / vendor blogs / marketing posts (separate ingest path per memory `feedback_llm_wiki_concept_pages_need_public_references`).

---

## Executive Summary (≈200 words)

Across the eight wiki domains, the largest external-resource gaps sit in **acma-projects (8 pages, 2 sources)**, **lng-projects (15 pages, 0 standards directory)**, and **maritime-law (33 pages, 2 sources)**. These are sparse scaffolds with foundational concept pages but almost no provenance-grounded standards or authoritative datasets. The next-tier gap is **engineering-standards (82 pages)** which is rich on ABS/API/ASME but missing whole regulator surfaces (BSEE, PHMSA, USCG, NTSB) and **naval-architecture (74 pages)** missing live data feeds (NCEI/GEBCO bathymetry, USACE CEM, ITTC procedures, NTSB CAROL). Marine-engineering's 19,221 pages are mostly raw-source page-imports — selective targeted additions, not a build-out, are the right move. asset-management (27 pages) already has the ISO 55000 spine; gaps are practitioner-frameworks (IAM endorsement scheme, Reliabilityweb Uptime Elements registry) and government RBI/RBM sources.

**Highest-impact single ingest target:** the **BSEE Data Center (data.bsee.gov)** — a federal open-data portal that simultaneously feeds engineering-standards (incidents, regulatory enforcement), lng-projects (offshore terminal production), naval-architecture (drilling rig casualties), and acma-projects (mooring failures, the ACMA seed already cites Sirocco). Authoritative, free, machine-queryable, multi-domain.

---

## Per-domain sections

### 1. acma-projects (8 pages, sources/=2)

Sparsest scaffold. Existing seeds are NTSB/MAIB Sirocco-style breakaway incident reports. Anchor and mooring code/standards work belongs here.

| # | Source | Publisher | Authority | Scope cover | Access | Ingest difficulty |
|---|---|---|---|---|---|---|
| 1 | **NAVFAC DM-26.5 Fleet Moorings + DM-26.6 Mooring Design Physical/Empirical Data + UFC 4-159-03** | US Navy NAVFAC / DoD | Government / military standard | ≈40% (fleet moorings, anchor selection, design loads) | Free, public-release, hosted on wbdg.org and maritime.org | Trivial — PDFs |
| 2 | **NAVFAC MO-124 Mooring Maintenance Manual (1987)** | US Navy NAVFAC | Government | ≈15% (operational + inspection cycle for moorings) | Free, wbdg.org PDF | Trivial — PDF |
| 3 | **NTSB CAROL marine accident docket** (carol.ntsb.gov, data.ntsb.gov) | NTSB (US gov) | Government investigative | ≈20% (mooring breakaway, ATB, vessel-on-mooring incidents) | Free, public docket search; structured fields | Medium — HTML+ZIP, queryable but per-incident |
| 4 | **PIANC Working Group reports (mooring/berthing-relevant: WG145, WG153, WG211)** | PIANC (intergovernmental waterborne-transport association) | Standards body (industry consensus) | ≈15% (terminal/berth mooring guidance) | Free for PIANC members; ≈$80–250 per non-member report from pianc.org/publications | Hard — paywalled for non-members |
| 5 | **OCIMF MEG4 industry guideline (Mooring Equipment Guidelines, 4th ed.)** | OCIMF | Industry standards body | ≈25% (tanker terminal mooring, breaking-load criteria) | Paid (~£280 print/PDF via Witherbys); abstract free | Hard — paywalled |

### 2. asset-management (27 pages, ISO 55000 spine present)

Existing standards/ folder has ISO 55000–55002, API 579/580/581, NORSOK Z-008, DNV-RP-G101, HSE SCR. Gaps: practitioner frameworks and US/EU government RBI guidance.

| # | Source | Publisher | Authority | Scope cover | Access | Ingest difficulty |
|---|---|---|---|---|---|---|
| 1 | **IAM (Institute of Asset Management) Subject-Specific Guidelines + Anatomy of Asset Management** | Institute of Asset Management (UK professional body) | Industry standards body | ≈30% (the ISO 55001 implementation companion the standard itself defers to) | Free PDFs at theIAM.org, registration-gated | Medium — registration, then PDF |
| 2 | **Uptime Elements body of knowledge (Reliabilityweb / O'Hanlon)** | Reliabilityweb / Association of Asset Management Professionals | Industry framework | ≈15% (RCM/PMO/FMEA framework, complementary to ISO 55000) | Free framework summary; books paid | Medium — HTML scrape of element pages |
| 3 | **GFMAM Competency Specification for ISO 55001 Auditor** | Global Forum on Maintenance and Asset Management | Standards body (federation) | ≈10% (auditor competency, certification basis for CAMA) | Free PDF on gfmam.org | Trivial — PDF |
| 4 | **HSE COMAH Safety Report Assessment Manuals (UK)** | UK Health & Safety Executive | Government regulator | ≈15% (major-hazard asset integrity, RBI/SCE practice) | Free at hse.gov.uk/comah | Trivial — HTML+PDF |
| 5 | **NIST SP 800-82r3 (Guide to OT/ICS Security) — asset-mgmt-relevant chapters** | NIST | Government standards body | ≈10% (OT asset register, criticality classification — bridges to engineering) | Free, doi.org/10.6028/NIST.SP.800-82r3 | Trivial — PDF |

### 3. engineering (638 pages — already mature)

**Skip / minimal additions only.** Per task brief, engineering is the most-developed domain and W1-W3 audit already covered it. No new recommendations; defer net-new ingest until cross-link Work Stream A consumes existing 638 pages.

### 4. engineering-standards (82 pages, sources/= ABS/API/ASME core)

Strong on classification + API + ASME. Missing whole government-regulator surfaces.

| # | Source | Publisher | Authority | Scope cover | Access | Ingest difficulty |
|---|---|---|---|---|---|---|
| 1 | **BSEE Data Center (data.bsee.gov) + Regulations & Standards register (bsee.gov/what-we-do/offshore-regulatory-programs/regulations-standards)** | Bureau of Safety & Environmental Enforcement (US gov) | Government regulator | ≈25% (offshore incident, production, regulatory enforcement on US OCS) | Free, queryable + bulk download | Trivial — HTML, CSV, structured queries |
| 2 | **PHMSA Pipeline Incident & 20-year Trends datasets** | PHMSA / US DOT | Government regulator | ≈15% (onshore pipeline incidents 1970-present, hazliquid + gas) | Free, ZIP downloads at phmsa.dot.gov/data-and-statistics/pipeline | Trivial — CSV |
| 3 | **USACE EM 1110-2-1100 Coastal Engineering Manual (6 vols, Parts I-VI)** | US Army Corps of Engineers | Government engineering manual | ≈10% (coastal hydrodynamics, sediment, project design — bridges to naval-architecture) | Free PDFs at publications.usace.army.mil | Trivial — PDFs (~350 MB total) |
| 4 | **NIST Handbook 130 (2025 ed.) + Handbook 44 (legal metrology)** | NIST | Government standards body | ≈5% (measurement law, fuel/lubricant standards relevant to refining/terminal QA) | Free at doi.org/10.6028/NIST.HB.130-2025 | Trivial — PDF + DOCX |
| 5 | **FERC eLibrary LNG/pipeline dockets (CP25-xxx, CP26-xxx)** | Federal Energy Regulatory Commission | Government regulator | ≈10% (cross-cuts engineering-standards + lng-projects: terminal certificate evidence, third-party engineering reviews) | Free, public eLibrary; per-docket browsing | Hard — large dockets, dynamic site |

### 5. lng-projects (15 pages, no standards/ directory yet)

Concepts sketched (boil-off, liquefaction, regulatory framework) but zero standards anchoring. CSA Z276 deliberately excluded per task brief (issue #2227 in flight).

| # | Source | Publisher | Authority | Scope cover | Access | Ingest difficulty |
|---|---|---|---|---|---|---|
| 1 | **IGU World LNG Report 2025 (16th ed., 168 pp)** | International Gas Union | Industry body | ≈30% (global LNG trade, liquefaction capacity, bunkering, FSRU, regas — foundational figures) | Free PDF at datocms-assets.com/146580/...igu-world-lng-report-2025 | Trivial — PDF |
| 2 | **DOE Office of Fossil Energy and Carbon Management — 2024 LNG Export Study + monthly LNG semi-annual reports** | US DOE FECM | Government | ≈20% (US LNG export approvals, project-level production volumes) | Free at energy.gov/fecm | Trivial — PDF |
| 3 | **FERC LNG terminal page + per-project dockets (Plaquemines, Commonwealth, Gulfstream, etc.)** | FERC | Government regulator | ≈25% (US LNG export terminals: existing/approved/proposed list, per-project FERC certificate proceedings) | Free, ferc.gov/natural-gas/lng | Medium — list page trivial; per-docket hard |
| 4 | **EIA Natural Gas + LNG export data (Open Data API)** | US Energy Information Administration | Government | ≈15% (LNG export volumes, prices, contract status) | Free API at api.eia.gov | Trivial — JSON |
| 5 | **SIGTTO publications (LNG Marine Loading Arms, Mooring of Gas Carriers, LNG Bunkering Guidance)** | SIGTTO | Industry standards body | ≈25% (LNG terminal mooring, transfer, bunkering operations) | Mixed: a few free PDFs at sigtto.org/media; most paid via Witherbys | Hard — paywalled for most titles |

### 6. marine-engineering (19,221 pages — selective adds only)

**Largely raw-imports already.** Recommend only narrow strategic additions that fill a *concept* gap rather than another document dump.

| # | Source | Publisher | Authority | Scope cover | Access | Ingest difficulty |
|---|---|---|---|---|---|---|
| 1 | **ITTC Recommended Procedures and Guidelines (Procedures Register)** | International Towing Tank Conference | Standards body (academic+industry consensus) | ≈10% (canonical test procedures: resistance, propulsion, seakeeping, cavitation — referenced from naval-arch too) | Free at ittc.info/downloads, per-procedure PDFs | Trivial — PDFs |
| 2 | **NOAA NCEI / IHO DCDB / GEBCO_2026 Grid (15-arcsec global bathymetry)** | NOAA + IHO | Government / standards body | ≈5% (foundational dataset for hydrodynamic modelling, referenced by every metocean study) | Free at download.gebco.net + ncei.noaa.gov/iho-data-centre-digital-bathymetry | Medium — netCDF, large files |
| 3 | **EMSA Annual Overview of Marine Casualties and Incidents (2025 ed., EMCIP-derived)** | European Maritime Safety Agency | Government (EU) | ≈10% (EU-flag vessel casualty statistics 2014–present) | Free PDF at emsa.europa.eu/publications | Trivial — PDF |

### 7. maritime-law (33 pages, sources/=2)

Concepts solid (UNCLOS, SOLAS, MARPOL, OPA-90, MLC, CLC, salvage, GA). Missing primary-source anchors.

| # | Source | Publisher | Authority | Scope cover | Access | Ingest difficulty |
|---|---|---|---|---|---|---|
| 1 | **UN DOALOS — UNCLOS official text + Conference Final Act + ratification list** | UN Office of Legal Affairs / DOALOS | Government (intergovernmental) | ≈25% (foundational treaty text every concept page references) | Free at un.org/depts/los | Trivial — PDF + HTML |
| 2 | **IMO GISIS public modules (Treaties, MSI casualties, Port Reception Facilities, Ship Particulars)** | IMO | Government (intergovernmental) | ≈25% (treaty status, ship registry, casualty case index) | Free with public account at gisis.imo.org | Medium — registration, then queryable |
| 3 | **CMI (Comité Maritime International) — Rotterdam Rules text, York-Antwerp Rules, Sea Waybills, e-Bills of Lading, CMI Yearbook 2003+, CML/CMI Database of Judicial Decisions** | Comité Maritime International | Industry standards body (treaty drafting NGO) | ≈20% (private maritime law conventions; case-law database — fills the cases/ gap) | Free at comitemaritime.org | Medium — multiple PDFs + DB |
| 4 | **EU EMSA + EUR-Lex maritime legislation portal** | European Commission / EMSA | Government (EU) | ≈10% (port state control directive, EMCIP, ship recycling regulation) | Free at eur-lex.europa.eu + emsa.europa.eu | Medium — large legal corpus |
| 5 | **US Coast Guard Marine Safety Manual (CIM 16000 series)** | USCG | Government | ≈10% (US flag state operational regs, MARPOL implementation) | Free at uscg.mil/dco | Trivial — PDFs |

### 8. naval-architecture (74 pages, sources/= SNAME textbooks dominant)

Strong textbook coverage (PNA series, Newman, Bertram, Tupper). Missing **live data feeds** and **regulatory test procedures**.

| # | Source | Publisher | Authority | Scope cover | Access | Ingest difficulty |
|---|---|---|---|---|---|---|
| 1 | **ITTC Procedures (full register, ≈80 procedures)** | ITTC | Standards body | ≈20% (canonical experimental + numerical procedures: resistance, seakeeping, propulsion, manoeuvring) | Free at ittc.info | Trivial — PDFs |
| 2 | **USNA EN400 Principles of Ship Performance + MIT OCW 2.20 / 2.019 lecture notes** | US Naval Academy + MIT OpenCourseWare | Academic (CC-BY) | ≈15% (undergraduate course-grade synthesis; complements PNA without licensing risk) | Free at usna.edu/NAOE + ocw.mit.edu | Trivial — PDFs |
| 3 | **NTSB marine reports (CAROL) + USCG Marine Casualty data** | NTSB + USCG | Government investigative | ≈10% (vessel-loss case studies that ground stability/strength theory) | Free at carol.ntsb.gov + uscg.mil | Medium — per-incident |
| 4 | **NOAA NCEI bathymetry (GEBCO_2026) + Marine Cadastre / BOEM Offshore Marine Cadastre Data Collection (April 2026 release)** | NOAA / BOEM | Government | ≈10% (environmental input data for seakeeping/manoeuvring; lease block geometry for offshore unit siting) | Free at gebco.net + hub.marinecadastre.gov | Medium — geospatial formats |
| 5 | **FEMA Hazus Inventory National Database (ports + critical infrastructure)** | FEMA | Government | ≈5% (port/harbor classification taxonomy, critical-infrastructure inventory for vulnerability work) | Free File Geodatabase at msc.fema.gov/portal/resources/hazus | Medium — GIS format |

---

## Cross-domain top-10 (impact = breadth × authority × access ease)

| Rank | Source | Domains served | Authority | Access | Score note |
|---:|---|---|---|---|---|
| 1 | **BSEE Data Center (data.bsee.gov)** | engineering-standards, lng-projects, naval-architecture, acma-projects | gov | free / structured | Multi-domain, free, queryable, regulator-authoritative |
| 2 | **UN DOALOS UNCLOS portal** | maritime-law, lng-projects (treaty status), engineering-standards (jurisdiction) | gov (intergov) | free | Foundational treaty text used by every maritime-law concept page |
| 3 | **NAVFAC DM-26.5/DM-26.6 + UFC 4-159-03** | acma-projects, naval-architecture, engineering-standards | gov / military | free | Public-release, fills entire acma-projects standards/ surface |
| 4 | **ITTC Recommended Procedures register** | naval-architecture, marine-engineering | standards body | free | Canonical test procedures; procedures already structured |
| 5 | **PHMSA Pipeline Incident dataset** | engineering-standards, lng-projects | gov | free / CSV | Time-series 1970-present, machine-queryable |
| 6 | **IGU World LNG Report 2025** | lng-projects, marine-engineering | industry body | free PDF | 168 pp, single-PDF foundation page for lng-projects |
| 7 | **IMO GISIS public modules** | maritime-law, engineering-standards, naval-architecture | gov (intergov) | free w/ registration | Treaty status + casualty case index + ship registry |
| 8 | **NTSB CAROL marine accident docket** | acma-projects, naval-architecture, maritime-law | gov | free | Per-incident structured records; already feeding seeds |
| 9 | **FERC LNG terminal page + eLibrary** | lng-projects, engineering-standards | gov | free; some hard | List page trivial; deep dockets hard but high-evidence |
| 10 | **USACE EM 1110-2-1100 Coastal Engineering Manual** | engineering-standards, naval-architecture, acma-projects | gov / engineering manual | free PDF | Bridges coastal hydrodynamics → naval-arch + mooring siting |

**Honorable mentions (close cuts at 11–13):** NOAA NCEI/GEBCO_2026 bathymetry; CMI Rotterdam-Rules + CML database; IAM Subject-Specific Guidelines.

---

## Notes on exclusions and confidence

- **CSA Z276**: covered separately by issues #2227/#2283 (in-flight per W1-W3 references) — not re-listed.
- **OCIMF MEG4**: listed once for acma-projects only because #2284 already targets it for marine-engineering mooring wiki.
- **API RP 2SK**: excluded — already listed as standards/api-rp-2sk.md in engineering-standards.
- **All recommendations verified 2026-05-08** via WebSearch; URLs were live at search time. Re-verify before ingest.
- **"Hard" ingest difficulty** items (PIANC, OCIMF MEG4, most SIGTTO titles) should be tagged `paywalled` and held in registry-only state per the established do-not-process-yet pattern, except for the small set of free SIGTTO PDFs already on sigtto.org/media.
