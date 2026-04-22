# ACE Engineer — Engineering Capability Map

Generated: 2026-04-10 | GH: #2098

## Discipline Matrix

| # | Discipline | Module/Repo | GTM Demo | Standards | Readiness | Client Value |
|---|-----------|------------|----------|-----------|-----------|-------------|
| 1 | Pipeline Wall Thickness | digitalmodel/structural/wall_thickness | Demo 2 (72 cases) | DNV-ST-F101, API RP 1111, PD 8010-2 | Production | Multi-code comparison overnight |
| 2 | Freespan / VIV Screening | digitalmodel/subsea/free_span | Demo 1 (680 cases) | DNV-RP-F105, DNV-RP-C205 | Production | Allowable span maps for pipeline routes |
| 3 | Deepwater Installation (Lift) | digitalmodel/marine_ops/installation | Demo 3 (180 cases) | DNV-RP-H103, DNV-ST-N001 | Production | Vessel-structure go/no-go matrix |
| 4 | S-Lay Pipelay | digitalmodel/marine_ops | Demo 4 (60 cases) | DNV-ST-F101 Sec 5, API RP 1111 | Production | Catenary screening for pipe catalog |
| 5 | Rigid Jumper Installation | digitalmodel/marine_ops | Demo 5 (300 cases) | DNV-RP-H103, DNV-OS-F101 | Production | Tie-in feasibility assessment |
| 6 | Fatigue / S-N Curves | digitalmodel/fatigue/sn_library | Notebook planned (#1692) | DNV-RP-C203, BS 7608, API RP 2A | Production | 221 curves, 17 standards |
| 7 | Cathodic Protection | digitalmodel/structural/cp | CP demo exists | DNV-RP-B401, NACE SP0169 | Production | Anode sizing and life prediction |
| 8 | Pressure Vessel / FFS | digitalmodel/structural/pressure_vessel | PV demo exists | API 579, ASME VIII | Production | Remaining life assessment |
| 9 | Mooring Design | digitalmodel/mooring | --- | DNV-OS-E301, API RP 2SK | Available | Line sizing, fatigue life |
| 10 | Riser Analysis | digitalmodel/risers | --- | API RP 2RD, DNV-OS-F201 | Available | Dynamic response, VIV |
| 11 | Floating Offshore Wind (FOWT) | digitalmodel/mooring + digitalmodel/naval_arch | --- | API RP 2SK, DNV-RP-J203 | Available | O&G-to-FOWT transfer for moorings, installation, and integrity |
| 12 | On-Bottom Stability | --- | --- | DNV-RP-F109 | Planned (#1835) | Hydrodynamic stability check |
| 13 | Shore Approach | --- | --- | --- | Planned (#1836) | HDD, trenching, pull-in |
| 14 | Pipeline CAPEX | --- | --- | --- | Planned (#1837) | Cost estimation |
| 15 | Field Development Economics | digitalmodel/field_development | --- | --- | Production | NPV, CAPEX/OPEX, concept screening |
| 16 | Drilling Rig Fleet | digitalmodel/naval_arch | --- | --- | Production (#2062) | Hull form validation |

---

## Readiness Legend

- **Production**: Module exists, tested, demo-ready
- **Available**: Module exists, needs demo packaging
- **Planned**: Issue created, dependencies known

---

## Demo Coverage Summary

| Metric | Count |
|--------|-------|
| Parametric demos (GTM suite) | 5 |
| Total parametric cases across demos | 1,292 |
| Additional demos (CP, PV, S-N) | 3 exist, not in GTM suite |
| Disciplines with demos | 8 of 16 |
| Disciplines at Production readiness | 10 of 16 |
| Disciplines at Available readiness | 3 of 16 |
| Disciplines at Planned readiness | 3 of 16 |

---

## Standards Coverage

| Standards Body | Disciplines Covered | Key Codes |
|---------------|--------------------|----|
| DNV | 10 | ST-F101, RP-F105, RP-C205, RP-H103, ST-N001, RP-C203, RP-B401, OS-E301, RP-F109, OS-F201 |
| API | 7 | RP 1111, RP 2A, 579, RP 2SK, RP 2RD, RP 2T, RP 2RD |
| ASME | 1 | Section VIII |
| BSI | 1 | BS 7608 |
| NACE | 1 | SP0169 |
| ISO | Referenced across multiple disciplines | ISO 19901 series |

---

## Gap Analysis

### High-Value Gaps (module exists, no GTM demo)

| Discipline | Gap | Effort to Close | Priority |
|-----------|-----|-----------------|----------|
| Mooring Design | Module exists, no demo packaging | 1 week | High --- mooring is a bread-and-butter discipline for FPSO/TLP clients |
| Riser Analysis | Module exists, no demo packaging | 1 week | High --- always paired with mooring in deepwater scope |
| Floating Offshore Wind (FOWT) | Capability exists across mooring/naval-arch/offshore-wind know-how, but no focused GTM package yet | 1 week | High --- opens renewables buyers using transferable O&G installation and integrity methods |
| Fatigue / S-N | 221 curves exist, notebook planned (#1692) | 3 days | Medium --- supporting capability, not standalone sale |

### Missing Capabilities (no module yet)

| Discipline | Market Demand | Effort to Build | Priority |
|-----------|--------------|-----------------|----------|
| On-Bottom Stability (#1835) | Common RFQ item for pipeline contractors | 2 weeks | Tier 4 --- frequently bundled with wall thickness |
| Shore Approach (#1836) | Niche but differentiating for shallow water | 3 weeks | Tier 5 --- differentiator for GoM shelf work |
| Pipeline CAPEX (#1837) | Pairs with every pipeline discipline above | 1 week for screening-level | Tier 4 --- turns engineering into business case |

---

## Demo-to-Discipline Mapping

### Demo 1 --- Freespan / VIV Screening (680 cases)
- **Sweep**: span length x pipe OD x current velocity x soil stiffness
- **Output**: allowable span envelope, onset velocity map, modal response
- **Hero chart**: span length vs. allowable current --- green/red pass/fail bands
- **Client insight**: identifies which spans need detailed FEA vs. pass screening

### Demo 2 --- Wall Thickness (72 cases)
- **Sweep**: 3 codes x pipe catalog x design pressures x corrosion allowances
- **Output**: min wall thickness per code, governing load case, utilisation ratio
- **Hero chart**: lifecycle utilisation comparison across DNV / API / PD 8010
- **Client insight**: which code governs and by how much --- avoids over-design

### Demo 3 --- Deepwater Installation / Lift (180 cases)
- **Sweep**: structure mass x sling config x vessel crane x Hs/Tp sea states
- **Output**: DAF, sling loads, crane utilisation, weather window
- **Hero chart**: go/no-go heatmap (Hs vs. structure weight)
- **Client insight**: splash zone slamming governs for 200te+ structures; DAF alone misleading
- **Add installation-analysis detail**: segmented hydrodynamic loading across the lifted geometry improves heave/pitch realism versus single-point loading, making splash-zone and water-entry weather limits more trustworthy
- **Advanced modeling note**: full geometry, flow interaction, and local perforation/open-area effects matter for large subsea structures --- not just total mass and centre-point hydrodynamics

### Demo 4 --- S-Lay Pipelay (60 cases)
- **Sweep**: pipe OD/WT x water depth x tension x stinger setting
- **Output**: sagbend strain, overbend curvature, tensioner capacity check
- **Hero chart**: tension-curvature envelope per pipe size
- **Client insight**: catenary screening identifies lay-feasible pipe grades before vessel mobilisation

### Demo 5 --- Rigid Jumper Installation (300 cases)
- **Sweep**: jumper geometry x spool length x rigging config x sea state
- **Output**: lift loads, VIV screening, orientation sensitivity
- **Hero chart**: parametric VIV pass rate by pipe size and current
- **Client insight**: 8" jumper VIV pass rate is 33% vs. 13% for standard pipe --- geometry matters more than mass

### FOWT Capability Overlay --- Floating Offshore Wind
- **Positioning**: transfer proven offshore oil-and-gas engineering into floating wind without pretending the loading, scale, and cost model are identical
- **What ACE can lead with**: mooring concept selection, anchor strategy, fatigue/integrity planning, weather-limited installation logic, tow-out/hook-up planning, and bankability-oriented technical assurance
- **Client insight**: floating wind buyers care less about generic renewables messaging and more about whether O&G mooring, installation, and integrity lessons have been adapted correctly for farm-scale repeatability
- **Near-term GTM angle**: package ACE as the bridge between deepwater mooring/installation experience and FOWT commercialization needs

---

## Competitive Positioning

| Capability | Traditional Consultancy | ACE Engineer |
|-----------|------------------------|-------------|
| Wall thickness check (1 pipe, 1 code) | 2-3 days, $3K-5K | Same-day, included in screening |
| Parametric sweep (full catalog) | 2-3 weeks, $15K-25K | Overnight, $5K-15K |
| Multi-code comparison | Rarely done (too expensive) | Default workflow --- every screening includes it |
| Audit trail | Spreadsheet, manual QC | Code-generated, traceable input-to-result |
| Repeat analysis (revised inputs) | 50-80% of original cost | Re-run in minutes, marginal cost ~$0 |

---

## Deployment Model

| Tier | Scope | Timeline | Price Range |
|------|-------|----------|-------------|
| Screening | Parametric analysis, go/no-go report | 48 hours | $5K-15K |
| Detailed | OrcaFlex/FEA model, sensitivity studies | 2-4 weeks | $25K-75K |
| Operations | Real-time decision support | Ongoing | $10K/month |
| Retainer | On-call engineering + parametric tools | Monthly | $8K-15K/month |
