---
title: "WRK-165: Subsea Intervention Analysis — Market & Technical Research"
wrk_id: WRK-165
status: research_complete
created: 2026-02-24
target_repos:
  - digitalmodel
  - worldenergydata
target_module: subsea_intervention
related: [WRK-016, WRK-019, WRK-046, WRK-105, WRK-148, WRK-164]
group: ACE-GTM
---

# WRK-165: Subsea Intervention Analysis — Market & Technical Research

> Research date: 2026-02-24 | Disposition (from WRK-165): Park 2-3 months (April 2026
> review recommended). This document front-loads the landscape so that April execution
> can begin immediately.

---

## 1. Market Landscape

### 1.1 What Is Subsea Intervention Analysis?

Subsea intervention covers all operations that gain access to a completed subsea well
or infrastructure after initial installation. The engineering analysis required varies
by intervention type:

| Intervention Type | Description | Depth Range | Key Analysis |
|---|---|---|---|
| Light Well Intervention (LWI) | Wireline, slickline, coiled tubing from a vessel — no kill fluid | All subsea depths | Vessel motion limits, intervention riser stroke, tool deployment loads |
| Heavy Well Intervention (HWI) | Full BOP stack deployment, well-control capable | >200 m typically | Riser analysis, vessel RAO limits, metocean windows |
| Coiled Tubing Intervention | CT string deployed through riser or lubricator | Shelf + deepwater | CT fatigue, string weight, heave compensation requirements |
| Wireline Intervention | Electric line or slickline toolstring deployment | All depths | Toolstring dynamics, lubricator pressure, vessel heave |
| ROV-Based Intervention | Valve manipulation, connector make/break, debris removal | Any depth | None from riser perspective — ROV spread operability |
| Well Stimulation | Acid stimulation, matrix treatment through coiled tubing | Shallow–mid | CT hydraulics, injection pressure limits |
| P&A / Plug & Abandon | Well barrier placement, riser or lubricator access | All | Varies; often wireline + cement |

### 1.2 Who Buys Intervention Analysis?

**Tier A — Operators (primary buyers)**
Oil and gas operators are the end clients for intervention analysis. They commission
it before contracting intervention vessels to:
- Establish vessel motion limits (operability criteria)
- Confirm riser design for the specific water depth and well configuration
- Verify weather window statistics for scheduling and contracting
- Produce regulatory documentation (BSEE/NOPSEMA/HSE)

Key operators in the Gulf of Mexico with active subsea portfolios: Shell, Chevron,
BP, Equinor, Murphy Oil, CNOOC, Kosmos, Beacon Offshore.

**Tier B — Intervention Vessel Contractors (secondary buyers)**
Vessel contractors need riser analyses when they market their vessels for a new
water depth regime or when configuring a riser system for a specific project.

Key intervention vessel contractors globally:
- **Helix Energy Solutions** (Well Enhancer, Q4000, Q5000, Q7000, Seawell) — dominant
  GOM light intervention player; runs the only Jones Act-compliant LWI vessel
- **Aker Solutions** — provides LWI services (now Aker Subsea Intervention)
- **Expro Group** — intervention tooling, tree services, well testing
- **Oceaneering International** — robotics, tooling, some LWI capability
- **TechnipFMC** — complete intervention scope via riser systems
- **Trendsetter Engineering** (Houston) — lubricator and intervention tooling OEM
- **Proserv** — well access / intervention controls
- **Coretrax** — well intervention tools (tubular running, clean-up)

**Tier C — SURF / EPCI Contractors**
Subsea7, McDermott, TechnipFMC, Saipem — when they hold the SURF frame agreement
and are asked to include intervention scope or when completing a trunkline tie-back
that requires access engineering.

### 1.3 What Analysis Deliverables Do Buyers Need?

| Deliverable | Buyer | Frequency |
|---|---|---|
| Operability study — metocean window analysis | Operator | Every well campaign |
| Intervention riser analysis — static + dynamic | Operator / vessel contractor | Per vessel–well combination |
| Vessel motion limits — Hs vs. Tp with heading | Operator | Per campaign |
| Tool deployment analysis — toolstring weight, lubricator pressure | Operator / tool company | Per well |
| Heave compensation sizing | Vessel contractor | Per riser design |
| Riser stroke envelope — tensioner stroke, flex joint angles | Vessel contractor | Per riser design |
| Current profile assessment — worst-case riser loading | Operator | Per field/season |
| Weather window probability — % operable by month | Operator | Per campaign |
| Regulatory documentation | Operator | Per BSEE/NOPSEMA/HSE requirement |
| Risk assessment — HAZID/HAZOP for toolstring deployment | Operator / contractor | Per novel operation |

### 1.4 Software and Tools Used

| Tool | Vendor | Role |
|---|---|---|
| **OrcaFlex** | Orcina | Industry standard for intervention riser dynamics, catenary profiles, flex joint angles, vessel coupling |
| **Flexcom** | Wood Group (now Flexcom by Wood) | Riser analysis, alternative to OrcaFlex; less common for LWI |
| **DeepRiser** | SINTEF / commercial | Academic origin; used in Norway-based work |
| **SESAM / SIMA** | DNV | Coupled analysis; more common for platforms; sometimes used for intervention spread |
| **ProteusDS** | DSA Ocean | Canadian market, hydrodynamics + mooring |
| **Python/MATLAB** | Internal | Post-processing, weather windows, operability envelopes |

**OrcaFlex dominates** the GOM intervention analysis market. Nearly all US-based vessel
contractors and operators use it or require deliverables from it.

### 1.5 Project Values and Timelines

Based on public contract announcements and industry salary/billing benchmarks:

| Service | Estimated Value | Timeline |
|---|---|---|
| Simple LWI operability study (shelf, single vessel) | $25K–$60K | 2–4 weeks |
| Full intervention riser analysis (deepwater, single campaign) | $80K–$200K | 4–10 weeks |
| Parametric riser analysis (multiple water depths / vessel configs) | $150K–$400K | 8–16 weeks |
| Full well access engineering package (riser + operability + reg docs) | $200K–$500K | 10–20 weeks |
| Retainer — ongoing campaign support (per year) | $120K–$300K/yr | Ongoing |

Day rates for intervention specialists: $1,500–$2,500/day (US market, 2025).
Intervention vessel day rates: $80K–$200K/day depending on vessel class and depth rating.

The high vessel day rate is the primary driver of operator demand for analysis —
a single weather downtime event at $150K/day makes a $100K operability study
immediately cost-justified.

---

## 2. Competitor Scan

The following firms provide subsea intervention analysis services:

| Firm | Headquarters | OrcaFlex? | Key Differentiator |
|---|---|---|---|
| **2H Offshore** (now Cactus 2H) | London / Houston | Yes | Deep riser expertise, decades of riser analysis track record; OTC presenter, highly credentialed |
| **Wood plc (formerly Amec)** | Aberdeen / Houston | Yes — Flexcom too | Large bench, regulatory relationships, framework contracts |
| **Subsea7 (engineering arm)** | Luxembourg / Houston | Yes | EPCI integration; intervention as part of SURF campaign |
| **TechnipFMC** | Paris / Houston | Yes | Full system OEM + analysis; proprietary riser systems |
| **Intecsea** (Worley) | Houston | Yes | Riser engineering specialists; deepwater GOM track record |
| **Exponent** | Menlo Park | Unknown | Forensics + failure analysis; some marine ops overlap |
| **Oceaneering International** | Houston | Yes — internal | Primarily tooling + ROV; engineering analysis for own operations |
| **Helix Energy Solutions** | Houston | Yes — internal | Self-analyzing; occasional external design work |
| **Expro Group** | Aberdeen / Houston | Varies | Primarily tooling/services; may subcontract analysis |
| **Trident Energy Services** | Aberdeen | Yes | Niche UK/Norway light intervention specialists |

**Key observation**: The major competitors (2H, Wood, Intecsea) have large, credentialed
teams and long histories. They compete on reputation and framework contracts.
A&CE's angle is not to displace them on large frame agreements — it is to:
1. Win smaller operator studies ($25K–$100K) where procurement cycles are shorter
2. Provide faster turnaround with automation (batch OrcaFlex parametrics)
3. Price below large-firm rates while delivering comparable technical quality
4. Target operators who don't want to commit to full EPCI contractors for analysis only

---

## 3. Technical Gap Analysis

### 3.1 What A&CE Can Do Now

| Capability | Existing Asset | Location |
|---|---|---|
| OrcaFlex model generation (parametric, batch) | `modular_generator/`, `batch_manager/` | `digitalmodel/solvers/orcaflex/` |
| OrcaFlex riser lines builder | `riser_lines_builder.py`, `riser_linetype_builder.py`, `riser_vessel_builder.py` | `digitalmodel/solvers/orcaflex/modular_generator/builders/` |
| OrcaFlex results post-processing | `post_process/`, `analysis/` | `digitalmodel/solvers/orcaflex/` |
| Vertical riser analysis | `vertical_riser_components.py`, `vertical_riser.py` | `digitalmodel/subsea/vertical_riser/` |
| Catenary riser analysis | `catenary_riser/`, `catenary/` | `digitalmodel/subsea/` |
| Vessel RAO integration | `rao_processor.py`, `unified_rao_reader.py` | `digitalmodel/marine_ops/marine_analysis/` |
| Marine operations analysis | `marine_analysis/`, `marine_engineering/` | `digitalmodel/marine_ops/` |
| OrcaFlex operability analysis | `operability_analysis.py` | `digitalmodel/` |
| BSEE intervention activity data | `intervention/` analysis modules | `worldenergydata/bsee/analysis/intervention/` |
| Intervention rig type classification | `RigType` enum (WIRELINE_UNIT, COIL_TUBING_UNIT, WORKOVER_RIG) | `worldenergydata/bsee/data/loaders/rig_fleet/constants.py` |
| Drilling riser component data | `drilling_riser_components.csv`, `drilling_riser_loader.py` | `worldenergydata/vessel_fleet/` |
| Metocean statistics | `metocean/statistics/`, `metocean/processors/` | `worldenergydata/metocean/` |
| Intervention cost day rates | `cost_engine.py` (WRK-019) | `worldenergydata/bsee/analysis/cost/` |
| HSE incident data | `hse/` importers and database | `worldenergydata/hse/` |

### 3.2 What Needs to Be Built

The following gaps exist between A&CE's current state and a deployable intervention
analysis service:

| Gap | Description | Build Effort | Related WRK |
|---|---|---|---|
| **Intervention riser model** | OrcaFlex model for LWI/HWI riser: lubricator, BOP-less string, heave compensator coupling | High (3–5 weeks) | Extends WRK-046 |
| **Intervention riser parametrics** | Parametric sweeps: water depth, vessel RAO, current, tool weight — intervention-specific | Medium (2–3 weeks) | Extends WRK-046 |
| **Heave compensation model** | Active/passive heave compensator OrcaFlex model (stroke, stiffness, efficiency) | Medium (2 weeks) | New |
| **Tool deployment analysis** | Toolstring dynamics: weight, drag, jarring loads, lubricator pressure | Medium (2–3 weeks) | New |
| **Intervention vessel data** | Vessel capabilities dataset: vessel name, owner, LWI/HWI rating, water depth rating, riser system, motion specs | Medium (2–3 weeks) | Extends WRK-104/135 |
| **Intervention history by field** | BSEE WAR data segmented by intervention type with vessel attribution | Low (1–2 weeks) | Extends WRK-016 |
| **Weather window calculator** | Monthly operability % from metocean stats × vessel Hs limits | Low (1–2 weeks) | Extends metocean module |
| **Operability envelope generator** | Hs vs. Tp operability envelope from OrcaFlex parametric results | Low (1 week) | Extends existing operability_analysis.py |
| **Regulatory documentation template** | Auto-populated BSEE/doc template from analysis results | Low (1 week) | New |

#### Can WRK-046 (Drilling Riser) Be Extended to Intervention?

**Yes, with significant additions.** The drilling riser model (WRK-046) covers:
- Marine riser joints, flex joints, telescopic joint, tensioner, BOP, LMRP
- Vessel motion input via RAOs
- Parametric analysis engine

An intervention riser differs in these critical ways:

| Parameter | Drilling Riser (WRK-046) | Intervention Riser |
|---|---|---|
| BOP | Full subsea BOP stack | No BOP (LWI) or lighter intervention BOP |
| Riser type | Heavy steel riser joints | Lighter intervention riser or lubricator string |
| Top end | Tensioner + telescopic joint | Passive / active heave compensator |
| Internal fluid | Mud weight (variable) | Completion fluid / seawater |
| Tool weight | N/A | Toolstring weight (0–20 t) is design driver |
| Connection at seabed | BOP/LMRP stack | Wellhead connector (Christmas tree interface) |
| Operability metric | Flex joint angle, tensioner stroke | Lubricator stroke, toolstring deployment window |

Recommended approach: create `digitalmodel/solvers/orcaflex/risers/intervention/`
as a parallel module to the planned `risers/drilling/`, sharing the parametric engine
but with intervention-specific model setup.

### 3.3 Intervention-Specific Data for worldenergydata

The following data additions would enrich worldenergydata and directly support
intervention analysis services:

| Dataset | Description | Source |
|---|---|---|
| Intervention vessel capabilities | Vessel name, owner, water depth rating, riser system (LWI/HWI), heave compensator specs, DP class | Public: company websites, BSEE vessel certificates, Offshore Magazine |
| BSEE intervention frequency by field | WAR records tagged by RigType (WIRELINE_UNIT, COIL_TUBING_UNIT, WORKOVER_RIG) grouped by field/water depth/year | Existing BSEE WAR data (WRK-016) |
| Tool string weight catalog | Standard toolstring weights by application (perforation gun, logging, setting tool, CT BHA) | Public: vendor specs |
| Metocean operability windows by GOM region | Monthly Hs/Tp exceedance probabilities at key LWI basins | Existing metocean module (NDBC) |

---

## 4. Recommended Service Offerings

The following service offerings are ranked by effort-to-launch and fit with A&CE's
existing capabilities:

### Offering A: LWI Operability Study (Quick Launch)
**Description**: Weather window analysis for a light well intervention campaign at a
given GOM location. Produces monthly operability percentages and Hs limit curves.
**Inputs**: Field location (lat/lon), vessel motion limits, intervention duration
**Outputs**: Monthly operability table, Hs–Tp envelope PDF/HTML
**Uses**: Existing metocean module + operability_analysis.py
**Effort to launch**: 2–3 weeks (limited new build required)
**Target price**: $25K–$50K per campaign
**Target buyer**: Small/mid operators (Murphy, Beacon, Kosmos) who don't have in-house
metocean teams

### Offering B: Intervention Riser Parametric Analysis
**Description**: OrcaFlex-based intervention riser analysis parametric across water
depth, vessel type, current profile, and toolstring weight. Delivers operability
envelopes, flex joint angles, and heave compensation requirements.
**Inputs**: Water depth range, vessel RAO library, riser configuration, current profiles
**Outputs**: Utilisation tables, operability envelopes, heave compensation sizing
**Uses**: OrcaFlex modular generator + new intervention riser module
**Effort to launch**: 8–12 weeks (significant new build in WRK-046 extension)
**Target price**: $80K–$200K
**Target buyer**: Helix Energy Solutions (vessel pre-qualification studies), operators

### Offering C: Intervention Activity Benchmarking (Data Product)
**Description**: Field-level intervention frequency analysis using BSEE WAR data.
Operators can see how their intervention rates compare to peer fields.
**Inputs**: BSEE WAR data (already collected in WRK-016)
**Outputs**: Field intervention frequency dashboard, water depth × era heatmaps
**Uses**: Existing intervention/ analysis modules in worldenergydata
**Effort to launch**: 1–2 weeks (primarily data analysis and report packaging)
**Target price**: $15K–$40K as a standalone data product; free teaser for GTM
**Target buyer**: Operators evaluating intervention risk before field development;
investment analysts evaluating asset portfolios

### Offering D: Well Intervention Campaign Planning Package
**Description**: Full-scope campaign support — operability analysis, riser analysis,
toolstring selection guidance, regulatory documentation package.
**Uses**: Combination of A + B + regulatory template
**Effort to launch**: 12–20 weeks (requires B to be built first)
**Target price**: $200K–$500K
**Target buyer**: Mid-tier operators running first deepwater LWI campaign

---

## 5. Connection to GTM Strategy (WRK-148)

### Target Companies with Specific Intervention Analysis Demand

The WRK-148 GTM document identifies 20 target companies. The following are the best
fits for subsea intervention analysis specifically:

| Company | GTM Tier | Why Intervention Analysis Fits |
|---|---|---|
| **Oceaneering International** | Tier 5 (Specialist) | Already rated 4/5 fit. Runs global LWI operations; needs riser analysis support for new deployment regions; A&CE batch OrcaFlex capability directly relevant |
| **Helix Energy Solutions** | Not in WRK-148 list — recommend adding | Dominant GOM LWI contractor; Q7000 new-build vessel requires riser design support; Hs limit curves for new water depths are a recurring need |
| **Subsea7** | Tier 1 (5/5 fit) | EPCI contractor with intervention scope on subsea contracts; deepwater GOM and Brazil active |
| **TechnipFMC** | Tier 1 (4/5 fit) | Has proprietary intervention riser systems; A&CE could provide third-party riser analysis or operability studies they subcontract |
| **2H Offshore / Cactus 2H** | Not in WRK-148 — potential subcontract | Large riser firm; could subcontract parametric analysis work to A&CE given the batch automation advantage |
| **Murphy Oil** | Not in WRK-148 — recommend adding | Mid-tier GOM operator; active deepwater subsea portfolio; intervention campaigns on Gulf of Mexico assets |
| **Beacon Offshore Energy** | Not in WRK-148 — recommend adding | GOM shelf + deepwater operator; likely uses external engineers for LWI analysis |

### Recommended GTM Actions for WRK-148

1. Add Helix Energy Solutions to the target company list (Tier 2, fit 4/5) — strongest
   near-term fit given ongoing LWI vessel deployments
2. Add Murphy Oil and Beacon Offshore as Tier 3 operator targets for LWI operability
   studies
3. Position Offering C (BSEE intervention benchmarking) as a free teaser/content piece
   on aceengineer-website — operators searching for "GOM well intervention frequency"
   will find it, establishing credibility before a sales conversation
4. OTC Houston 2026 (May 4-7) — Helix, Oceaneering, and Expro all exhibit; in-person
   conversations on LWI riser analysis needs are highly likely

---

## 6. Horizon and Priority Recommendation

The WRK-165 item notes a disposition of "park 2-3 months" due to the expected
improvement in AI synthesis capability. This research document pre-loads the landscape.
The following phasing is recommended:

### Immediate (now, no new build required)
- **Offering C** as GTM content: package the existing BSEE intervention data (WRK-016)
  into a field-level benchmarking report and publish to aceengineer-website
- Add Helix Energy Solutions to WRK-148 target list
- Use the BSEE WAR intervention data to produce one public-facing insight
  (e.g., "Intervention frequency in deepwater GOM by era") as LinkedIn content

### April 2026 (after park period)
- Start Offering A (LWI Operability Study) — quick launch, limited new build
- Begin intervention riser module as WRK-046 extension (new WRK item required)
- Add intervention vessel capabilities dataset to worldenergydata (new WRK item)

### Q3 2026
- Complete Offering B (Intervention Riser Parametric Analysis)
- Launch Offering D (full campaign package) once A and B are proven

---

## 7. Acceptance Criteria Checklist

- [x] Market landscape document: who buys, what they need, what it pays
  (see Section 1: Market Landscape)
- [x] Technical gap analysis: what we can do now vs. what we need to build
  (see Section 3: Technical Gap Analysis)
- [x] Competitor scan: 10 firms providing subsea intervention analysis
  (see Section 2: Competitor Scan)
- [x] Recommended service offerings with effort-to-launch estimates
  (see Section 4: Recommended Service Offerings)
- [x] Connection to GTM strategy (WRK-148) with specific target companies
  (see Section 5: GTM Connection)

---

## 8. Proposed Follow-On WRK Items

The following new WRK items are recommended as a result of this research:

| New WRK | Title | Priority | Effort |
|---|---|---|---|
| TBD | LWI operability study service — operability engine + weather window calculator | High | 2–3 weeks |
| TBD | Intervention riser OrcaFlex module (extends WRK-046) | Medium | 8–12 weeks |
| TBD | Intervention vessel capabilities dataset for worldenergydata | Medium | 2–3 weeks |
| TBD | Add Helix Energy Solutions to WRK-148 GTM target list | High | <1 day |
| TBD | BSEE intervention frequency content piece for aceengineer-website | High | 1 week |
