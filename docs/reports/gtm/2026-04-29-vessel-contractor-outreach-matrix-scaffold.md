# Vessel Contractor Outreach Matrix — Scaffold (2026-04-29)

> **Issue:** [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) — feat(gtm): weekly vessel contractor outreach matrix for April target
> **Parent campaign:** [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) — vessel installation contractor outreach
> **GTM umbrella:** [#2016](https://github.com/vamseeachanta/workspace-hub/issues/2016) — client conversion pipeline
> **Demo proof anchors:** Demo 3 (deepwater mudmat installation), Demo 4 (shallow-water S-lay), Demo 5 (deepwater rigid-jumper installation) — all shipped Apr 14
> **Authoring lane:** Claude planning/research worker, ace-linux-1, 2026-04-29
> **Status:** **scaffold v1 — not yet a send-ready list.** Per-target evidence is now split into `corporate_root_evidence` vs. `deep_link_evidence`, and `pain_point_evidence` is carried explicitly. High-priority rows currently satisfy only the corporate-root scaffold gate; deep-link confirmation, contact routing, and pain-point hardening remain matrix-fill execution work after plan approval.

---

## Public/Private Boundary Decision (mandatory header)

This artifact is **public repo-tracked content**.

- **In this file:** company names (already public), public segment / fleet category, official corporate-root evidence URLs, planned deep-link evidence slots, pain-point evidence slots, demo-anchor mappings, `can-say-now` / `cannot-claim-yet` envelopes, and outreach priority.
- **Not in this file:** named individual contacts, direct emails, phone numbers, LinkedIn URLs of named persons, BD-ops session notes, or any private-route data. Per-target private-routing pointers (e.g., "search LinkedIn for offshore-engineering-lead at [company]") are recorded *outside this repo* and referenced here only as `private_route: external` with no detail.
- **Legal sanity gate:** any future promotion of this file to a public-facing surface (aceengineer.com, brochure attachment, expert-network deck) must pass `scripts/legal/legal-sanity-scan.sh --diff-only` and a manual public/private boundary review, per `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates for Public Artifacts".

---

## How to read this matrix

Each target carries the eight-field contract used by `docs/gtm/outreach-candidate-briefs-2026-04-28.md`, adapted to a *contractor row* shape:

| Field | Purpose |
|---|---|
| `company` | Public corporate name |
| `tier_seed` | Tier from [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) (T1 / T2 / T3) |
| `tier_revised` | Tier after this scaffold's reconciliation |
| `segment` | Subsea install / pipelay / heavy-lift / wind install / IRM / Gulf-niche |
| `relevant_fleet` | Public vessel anchor (named in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) or [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed) |
| `demo_anchor` | Which ACE shipped demo speaks to this contractor's work |
| `pain_point_hypothesis` | Public-evidence-bounded — never invented |
| `pain_point_evidence` | Public source path/URL or explicit `inferred-from-demo-coverage` placeholder |
| `corporate_root_evidence` | Official corporate-domain anchor, required at scaffold-review depth |
| `deep_link_evidence` | Official fleet / project / vessel subpage to verify before send |
| `can_say_now` | Defensible ACE claim envelope for this contractor |
| `cannot_claim_yet` | Adjacent claims to flag in the proposal/disclaimer |
| `outreach_priority` | High / Medium / Low / Defer |
| `private_route` | `external` if a routing pointer exists privately; `none` otherwise |

**Evidence-handling note (anti-fabrication):** every `corporate_root_evidence` value below is an official corporate-domain anchor that any reader can verify resolves to the named company's site. `deep_link_evidence` is intentionally left as a planned verification slot unless an official fleet/project/vessel page has been confirmed. This avoids manufacturing URLs that may not match the live site while still making the missing proof surface explicit. `pain_point_evidence` is likewise separated so readers can distinguish public proof from current demo-coverage inference.

---

## Tier-1 — Major EPIC / Heavy-Lift / Subsea Installation Contractors

### Target 1 — Subsea7

- **company.** Subsea7 (UK / Norway / global)
- **tier_seed.** T1
- **tier_revised.** T1 (no change)
- **segment.** Subsea installation, deepwater EPIC, mooring / riser, rigid-jumper installation; renewables arm = Seaway7
- **relevant_fleet.** Seven Borealis (HLV — explicitly named in `outreach-candidate-briefs-2026-04-28.md` Candidate 3 demo input as a *class-typical* envelope), Seven Navica (PLV — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed)
- **demo_anchor.** Demo 3 (deepwater mudmat installation, CSV class-typical envelope), Demo 5 (rigid jumper installation), Demo 4 (S-lay screening — Seven Navica analogue)
- **pain_point_hypothesis.** Deepwater installation contractors face decision-cost pressure on go/no-go for marginal sea-states across the lift envelope; screening artifacts (180-case mudmat / 300-case jumper) reduce committee-review cycle time before a project-specific OrcaFlex run.
- **corporate_root_evidence.** https://www.subsea7.com/ (corporate root; fleet/project deep-links are matrix-fill work)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "We screened 180 deepwater mudmat installation cases against a Seven Borealis-class envelope overnight, and 300 rigid-jumper cases including a 50 mm tie-in alignment phase — both as auditable HTML." Source: `digitalmodel/examples/demos/gtm/output/demo_03_*.html`, `demo_05_*.html`.
- **cannot_claim_yet.** Vessel-specific RAOs; full DP envelope at landing; named-Subsea7-project case studies (we hold no such public license).
- **outreach_priority.** **High** — Tier-1 fit + named-vessel anchor in our shipped demo input.
- **private_route.** omitted-public-artifact (details intentionally absent from this public repo).

### Target 2 — TechnipFMC (Subsea)

- **company.** TechnipFMC (US/UK/global; subsea installation segment)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Subsea EPIC, integrated subsea solutions (iEPCI), umbilical/flowline install
- **relevant_fleet.** Deep Energy (PLV), Coral do Atlantico (PLV) — named-vessel detail is matrix-fill work
- **demo_anchor.** Demo 4 (shallow-water S-lay — only the *concept* maps; deepwater PLV envelope sits outside Demo 4's water-depth set), Demo 1 (freespan VIV screening once the line is laid)
- **pain_point_hypothesis.** iEPCI workflows are sensitive to early concept-stage screening accuracy because rework downstream propagates across multiple disciplines; multi-code WT comparison + freespan screening at concept gate is high-leverage.
- **corporate_root_evidence.** https://www.technipfmc.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "DNV-ST-F101 / API RP 1111 / PD 8010-2 wall-thickness comparison across 72 cases for an 8″–20″ portfolio at concept stage."
- **cannot_claim_yet.** iEPCI integration depth; named-TechnipFMC project work; vessel-specific motion analysis without their RAOs.
- **outreach_priority.** **High** — Tier-1 fit; even without a vessel-anchored demo match, Demo 1 + Demo 2 are credible anchors.
- **private_route.** omitted-public-artifact.

### Target 3 — Saipem

- **company.** Saipem (Italy)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Subsea EPIC, pipelay (deep + shallow), heavy lift, drilling
- **relevant_fleet.** Castorone (PLV — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed; deep + shallow capable), FDS-2 HLV
- **demo_anchor.** Demo 4 (shallow-water S-lay — Castorone shallow envelope), Demo 3 (deepwater installation — FDS-2 analogue), Demo 5 (rigid-jumper)
- **pain_point_hypothesis.** Cross-water-depth fleet flexibility is a competitive lever; concept-stage screening that compares small-barge vs. larger-vessel feasibility frees engineering bandwidth on portfolio bidding.
- **corporate_root_evidence.** https://www.saipem.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "60-case shallow-water S-lay screening across 2 barge classes × 5 pipe sizes × 6 depths" (Demo 4); "180-case deepwater mudmat installation against Large-CSV / Medium-CSV envelopes" (Demo 3).
- **cannot_claim_yet.** Castorone-specific RAOs; named-Saipem project case studies.
- **outreach_priority.** **High**.
- **private_route.** omitted-public-artifact.

### Target 4 — McDermott International

- **company.** McDermott International (Houston)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Subsea EPIC, lay barge, GoM deepwater
- **relevant_fleet.** DB101 (lay barge — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed), Amazon (HLV), Lay Vessel 108
- **demo_anchor.** Demo 4 (S-lay shallow + transitional), Demo 5 (rigid jumper), Demo 1 (freespan/VIV)
- **pain_point_hypothesis.** GoM project economics + post-restructuring schedule pressure → screening artifacts that compress weeks of OrcaFlex pre-checks into hours align with internal cost discipline.
- **corporate_root_evidence.** https://www.mcdermott.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "60-case S-lay screening, including 8″–24″ pipe range, in self-contained HTML — no proprietary toolchain to install for inspection."
- **cannot_claim_yet.** Vessel-specific dynamics under DB101 RAOs; named-McDermott project work.
- **outreach_priority.** **High** — GoM proximity, named-vessel anchor in [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799).
- **private_route.** omitted-public-artifact.

### Target 5 — Allseas

- **company.** Allseas Group (Switzerland / Netherlands)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Pipelay (S-lay + J-lay), heavy lift (Pioneering Spirit single-lift), decommissioning
- **relevant_fleet.** Pioneering Spirit, Lorelay (PLV — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed), Solitaire, Audacia
- **demo_anchor.** Demo 4 (S-lay screening), Demo 1 (freespan VIV after lay)
- **pain_point_hypothesis.** Allseas operates on the largest single-lift / longest pipelay envelopes in the industry; the differentiator at concept stage is *defensible engineering audit trail* per the citation contract — methodology messaging may resonate more than capacity messaging.
- **corporate_root_evidence.** https://allseas.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Every numeric in the screening report cites the code clause it came from." Methodology proof: `.claude/rules/calc-citation-contract.md` + `digitalmodel/src/digitalmodel/citations/schema.py`.
- **cannot_claim_yet.** Pioneering-Spirit-class single-lift dynamics; vessel-specific motion analysis.
- **outreach_priority.** **High**.
- **private_route.** omitted-public-artifact.

### Target 6 — Heerema Marine Contractors

- **company.** Heerema Marine Contractors (Netherlands)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Heavy lift (Sleipnir, Thialf), subsea installation, decommissioning
- **relevant_fleet.** Sleipnir, Thialf, Aegir
- **demo_anchor.** Demo 3 (deepwater mudmat installation, HLV envelope analogue), Demo 5 (rigid jumper)
- **pain_point_hypothesis.** Heavy-lift schedule cost is dominated by weather-window risk; screening that resolves go/amber/red across mudmat sizes × Hs envelopes maps directly to operability decisions.
- **corporate_root_evidence.** https://www.heerema.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "180-case mudmat install screening across 5 Hs values per case — overnight HTML report."
- **cannot_claim_yet.** Sleipnir-/Thialf-specific RAOs; HLV-specific DP envelope.
- **outreach_priority.** **High**.
- **private_route.** omitted-public-artifact.

### Target 7 — Boskalis (Subsea Services)

- **company.** Royal Boskalis Westminster (Netherlands) — Subsea Services / Offshore Energy
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Subsea installation, lay support, dredging-adjacent install
- **relevant_fleet.** Boskalis lay barges (named in [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed), heavy-transport vessels
- **demo_anchor.** Demo 4 (shallow / transitional S-lay), Demo 3 (mudmat install)
- **pain_point_hypothesis.** Cross-segment fleet (subsea + dredging + heavy-transport) → buyer often evaluates marginal-economics fields where small-barge feasibility is the decision driver.
- **corporate_root_evidence.** https://boskalis.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Shallow-water S-lay screening with overbend / sagbend / tension / stinger-departure outputs in a single HTML."
- **cannot_claim_yet.** Boskalis-specific vessel motion data.
- **outreach_priority.** **High**.
- **private_route.** omitted-public-artifact.

### Target 8 — Van Oord

- **company.** Van Oord (Netherlands)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Offshore wind installation (cable + foundation + turbine), dredging-adjacent
- **relevant_fleet.** Aeolus (wind installation), Bokalift class, Stork (shallow-water lay — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed)
- **demo_anchor.** Demo 4 (S-lay shallow envelope, Stork analogue); FOWT segment is currently scope-note-only (`docs/gtm/fowt-engineering-scope.md`) — no shipped FOWT demo.
- **pain_point_hypothesis.** Wind installation differs from oil-and-gas; ACE messaging needs explicit "what transfers and what doesn't" to be credible (covered by the FOWT scope note).
- **corporate_root_evidence.** https://www.vanoord.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Shallow-water lay screening for the Stork-class envelope" (Demo 4); "explicit boundary on what oil-and-gas mooring expertise transfers to floating wind" (FOWT scope note).
- **cannot_claim_yet.** Full IEC 61400-3 DLC execution; coupled aero-hydro-servo-elastic time-domain; certification-grade output.
- **outreach_priority.** **Medium** — wind segment best contacted *after* the FOWT worked example (OC4-DeepCwind 1-pager, `outreach-candidate-briefs-2026-04-28.md` §4.3) ships. Pipelay segment can lead today.
- **private_route.** omitted-public-artifact.

### Target 9 — DEME Offshore

- **company.** DEME Group, Offshore arm (Belgium)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Offshore wind installation, heavy lift, cable lay
- **relevant_fleet.** Orion (HLV, wind-tuned), Living Stone (cable lay)
- **demo_anchor.** scope-note-only — FOWT lane not shipped; Demo 3 deepwater mudmat envelope partially analogous for foundation install
- **pain_point_hypothesis.** Wind-foundation install is operability-window-bound; Hs / period sensitivity screening at concept stage is the core decision aid.
- **corporate_root_evidence.** https://www.deme-group.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Hs sensitivity sweep across mudmat sizes and water depths" (Demo 3 transferable framing).
- **cannot_claim_yet.** Wind-foundation-specific dynamics; named-DEME project work.
- **outreach_priority.** **Medium** (defer until FOWT worked example ships).
- **private_route.** omitted-public-artifact.

---

## Tier-2 — Specialist / Mid-Tier Installation & Subsea Operators

### Target 10 — DOF Group (DOF Subsea + Solstad merger)

- **company.** DOF Group (Norway / global) — combined post-merger entity (DOF + Solstad)
- **tier_seed.** T2 (DOF Subsea, Solstad listed separately in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669))
- **tier_revised.** T2 (consolidated row; Solstad collapsed into this entry)
- **segment.** Subsea CSV / IMR / IRM
- **relevant_fleet.** Skandi-class subsea CSVs (multiple)
- **demo_anchor.** Demo 5 (rigid-jumper installation), Demo 3 (mudmat install)
- **pain_point_hypothesis.** IMR-cycle vessel utilization is the operating lever; screening that compresses concept analysis time on a tie-in candidate increases the count of bid-able opportunities per quarter.
- **corporate_root_evidence.** https://dofgroup.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "300-case rigid-jumper install screening — including the 50 mm tie-in alignment phase."
- **cannot_claim_yet.** Skandi-class-specific RAOs; named-DOF project work.
- **outreach_priority.** **High** — Tier-2 fit, named-segment match.
- **private_route.** omitted-public-artifact.

### Target 11 — Bourbon Offshore

- **company.** Bourbon Maritime (France)
- **tier_seed.** T2
- **tier_revised.** T2
- **segment.** Subsea support, IMR, OSV
- **relevant_fleet.** Bourbon Evolution series (CSV / IMR)
- **demo_anchor.** Demo 5 (rigid jumper), Demo 3 (mudmat install)
- **pain_point_hypothesis.** Mid-tier fleet operators bid against majors on cost; anything that strengthens engineering rigor without buying tooling is a margin lever.
- **corporate_root_evidence.** https://www.bourbon-online.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Self-contained HTML reports — your engineers spot-check the calc surface without installing proprietary toolchains" (Demo 4 framing applies broadly).
- **cannot_claim_yet.** Vessel-specific RAOs; named-Bourbon project work.
- **outreach_priority.** **Medium**.
- **private_route.** omitted-public-artifact.

### Target 12 — Sapura Energy

- **company.** Sapura Energy Berhad (Malaysia)
- **tier_seed.** T2
- **tier_revised.** T2
- **segment.** SE Asia subsea EPIC, pipelay, drilling
- **relevant_fleet.** Sapura Constructor ([#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed), Sapura Onix
- **demo_anchor.** Demo 4 (shallow-water S-lay), Demo 1 (freespan VIV)
- **pain_point_hypothesis.** SE Asia marginal-economics fields favor barge classes where Demo 4's "Can a smaller barge do this without departure-angle pain?" question is the decision driver.
- **corporate_root_evidence.** https://www.sapuraenergy.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Shallow-water S-lay screening — barge selection across pipe size and water depth."
- **cannot_claim_yet.** Sapura-Constructor-specific dynamics; named-Sapura project work.
- **outreach_priority.** **High** (named-vessel anchor in [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799)).
- **private_route.** omitted-public-artifact.

### Target 13 — Seaway7 (Subsea7 Renewables)

- **company.** Seaway7 (subsidiary of Subsea7)
- **tier_seed.** T2
- **tier_revised.** T2 (deduplicated against Subsea7 row; renewables-segment-specific)
- **segment.** Offshore wind installation (foundation + cable)
- **relevant_fleet.** Seaway Strashnov, Seaway Yudin
- **demo_anchor.** scope-note-only (FOWT lane not shipped)
- **pain_point_hypothesis.** Same FOWT-credibility problem as Target 8 — explicit transfer-and-gap framing is the lead, not capacity claims.
- **corporate_root_evidence.** https://www.seaway7.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Mooring concept screening at pre-FEED level using the same OrcaFlex workflow as deepwater oil-and-gas mooring — with explicit gaps vs. IEC DLCs flagged" (FOWT scope note).
- **cannot_claim_yet.** Coupled aero-hydro-servo-elastic verification; certification-grade output.
- **outreach_priority.** **Medium** (defer until FOWT worked example ships).
- **private_route.** omitted-public-artifact.

### Target 14 — Cadeler

- **company.** Cadeler A/S (Denmark)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added here as 2026-current wind-segment leader)
- **tier_revised.** T2 (new entry)
- **segment.** Offshore wind installation (turbine install)
- **relevant_fleet.** Wind Orca, Wind Osprey, NextGenerator class (under build)
- **demo_anchor.** scope-note-only
- **pain_point_hypothesis.** Pure-play wind installation operator; messaging must be 100% wind-credibility-anchored.
- **corporate_root_evidence.** https://www.cadeler.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** Defer outreach until FOWT worked example ships; today's claim is "we have a published scope note explicit about what does/doesn't transfer".
- **cannot_claim_yet.** Any oil-and-gas demo as the lead; turbine-specific dynamics.
- **outreach_priority.** **Defer** (logged here so subsequent runs do not re-add).
- **private_route.** none yet.

### Target 15 — Helix Energy Solutions

- **company.** Helix Energy Solutions (Houston)
- **tier_seed.** T3 ("Cal Dive (now Helix)")
- **tier_revised.** T2 (well-intervention-major; retiered up given GoM relevance)
- **segment.** Well intervention, IRM, decommissioning
- **relevant_fleet.** Q4000, Q5000, Q7000, Siem Helix 1
- **demo_anchor.** Demo 5 (rigid jumper — tie-in to existing infrastructure is intervention-adjacent), Demo 3 (mudmat install for new infrastructure)
- **pain_point_hypothesis.** Intervention scopes hinge on tie-in alignment and re-entry tolerances; Demo 5's 50 mm tie-in alignment phase is a direct conversation hook.
- **corporate_root_evidence.** https://www.helixesg.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "300-case rigid-jumper install screening including the 50 mm tie-in alignment phase, which is where day-rate bleed actually happens."
- **cannot_claim_yet.** Q-class-specific RAOs; named-Helix project work; well-intervention dynamics specifically.
- **outreach_priority.** **High** (GoM proximity + tie-in alignment hook).
- **private_route.** omitted-public-artifact.

---

## Tier-3 — Niche / Regional / IRM Operators

### Target 16 — DeepOcean Group

- **company.** DeepOcean Group (Norway)
- **tier_seed.** T3
- **tier_revised.** T3
- **segment.** IRM, subsea services, decommissioning
- **relevant_fleet.** Multiple subsea CSVs (Edda Fauna, Edda Flora class — public)
- **demo_anchor.** Demo 5 (rigid jumper), Demo 3 (mudmat install)
- **pain_point_hypothesis.** IRM operators run high-cycle workflows where engineering-screening rigor compounds across many small jobs.
- **corporate_root_evidence.** https://www.deepoceangroup.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Self-contained HTML screening reports — overnight turnaround, code-clause-cited."
- **cannot_claim_yet.** DeepOcean-vessel-specific dynamics; named-DeepOcean project work.
- **outreach_priority.** **Medium**.
- **private_route.** omitted-public-artifact.

### Target 17 — Jan De Nul

- **company.** Jan De Nul Group (Belgium / Luxembourg)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added for crossover dredging + offshore install)
- **tier_revised.** T3 (new entry)
- **segment.** Heavy installation, dredging crossover, offshore wind
- **relevant_fleet.** Voltaire (jack-up wind installation, public)
- **demo_anchor.** scope-note-only (wind segment) + Demo 4 (shallow-water lay framing)
- **pain_point_hypothesis.** Cross-segment buyer; wind-credibility framing required.
- **corporate_root_evidence.** https://www.jandenul.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Concept-stage screening + explicit transfer-and-gap framing for offshore wind work."
- **cannot_claim_yet.** Voltaire-specific dynamics; named-JDN project work; full IEC DLC.
- **outreach_priority.** **Medium**.
- **private_route.** omitted-public-artifact.

### Target 18 — Eidesvik Offshore

- **company.** Eidesvik Offshore (Norway)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added as Norwegian subsea / OSV niche)
- **tier_revised.** T3
- **segment.** Subsea support, OSV, IRM
- **relevant_fleet.** Subsea / IMR fleet (public)
- **demo_anchor.** Demo 5 (rigid jumper)
- **pain_point_hypothesis.** Mid-tier Norwegian operator competing on engineering rigor + utilization.
- **corporate_root_evidence.** https://www.eidesvik.no/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** Same as Target 16.
- **cannot_claim_yet.** Eidesvik-vessel-specific dynamics.
- **outreach_priority.** **Low** (audience saturation may be high for this segment).
- **private_route.** none yet.

### Target 19 — Acteon Group

- **company.** Acteon Group (UK; mooring, geosciences, IRM brands)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added for mooring/anchor expertise crossover)
- **tier_revised.** T3
- **segment.** Mooring services, anchor design, IRM
- **relevant_fleet.** N/A — services brand, not a fleet operator (consumed by us as adjacent expertise / partner candidate)
- **demo_anchor.** Mooring messaging via `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` + DNV-OS-E301 citation pilot; FOWT scope note.
- **pain_point_hypothesis.** Mooring-services brand → ACE methodology message (citation contract + multi-AI cross-review) may resonate as differentiation against incumbent toolchains.
- **corporate_root_evidence.** https://acteon.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Every standards-derived numeric carries a citation back to the code clause; multi-AI cross-review is standard pre-merge step."
- **cannot_claim_yet.** Anchor-specific design depth (out-of-scope today).
- **outreach_priority.** **Medium** (methodology-led, partner-shape, not a vessel-fleet target).
- **private_route.** none yet.

### Target 20 — Otto Candies LLC

- **company.** Otto Candies LLC (US Gulf, Louisiana)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added as GoM-niche per [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) "Gulf of Mexico/offshore adjacent work")
- **tier_revised.** T3
- **segment.** OSV / GoM marine, MPSV, ROV-support
- **relevant_fleet.** Public fleet pages (matrix-fill work to confirm vessel detail)
- **demo_anchor.** Demo 3 (mudmat install, GoM proximity)
- **pain_point_hypothesis.** Gulf-niche operator economics are utilization-driven; methodology messaging may be over-tooled relative to ICP.
- **corporate_root_evidence.** https://www.ottocandies.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Concept-stage screening on a Gulf-relevant water-depth envelope."
- **cannot_claim_yet.** GoM-specific weather-window data; named-Candies project work.
- **outreach_priority.** **Low** (ICP fit uncertain; flag for user confirmation).
- **private_route.** none yet.

### Target 21 — Solstad Offshore (legacy, now DOF)

- **company.** Solstad Offshore (now consolidated into DOF Group post-merger; retained here as named-vessel anchor)
- **tier_seed.** T2
- **tier_revised.** **Deprecated — collapse into Target 10 (DOF Group).** Listed here so the next reader does not re-add as a separate row.
- **outreach_priority.** **Defer** (treated under Target 10).

### Target 22 — EMAS / Ezra Holdings (legacy)

- **company.** EMAS Energy / Ezra Holdings (Singapore; restructured 2017+; assets dispersed across PaxOcean and other operators)
- **tier_seed.** T2
- **tier_revised.** **Deprecated — restructured entity.** Listed here per [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed; no longer a coherent outreach target. The named lay-vessel asset family flagged in [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) ("EMAS/Ezra type barges") routes to whichever current operator now holds the hull.
- **outreach_priority.** **Defer**. Follow-up: open a research issue to map ex-EMAS hulls to current operators if the GoM/SE Asia barge segment becomes a focus lane.

---

## Summary Counts

- **Total scaffold rows:** 22.
- **Live usable targets:** 19. Deprecated/deferred rows are excluded from the ≥20 acceptance count, so this does **not** yet satisfy the ≥20 live-target requirement unless the user explicitly accepts 19 live targets plus 3 deferred/deprecated rows for this wave.
- **Live targets (priority High / Medium / Low):** 19. Deprecated/deferred: 3 (Solstad, EMAS, Cadeler-deferred).
- **Targets with at least one shipped-demo anchor:** 17 of 19 live (Demo 3 / 4 / 5 mapping).
- **Targets in `outreach_priority: High`:** 10 (Subsea7, TechnipFMC, Saipem, McDermott, Allseas, Heerema, Boskalis, DOF Group, Sapura Energy, Helix). Each carries a named-vessel anchor and a demo-mapping.
- **High-priority evidence state:** 10 of 10 currently have `corporate_root_evidence`, `deep_link_evidence`, and `pain_point_evidence` fields present; all 10 still require replacement of scaffold placeholders with verified public deep links / pain-point proof before send.
- **Targets in `outreach_priority: Medium`:** 7 (Van Oord, DEME, Bourbon, Seaway7, DeepOcean, Jan De Nul, Acteon).
- **Targets in `outreach_priority: Low`:** 2 (Eidesvik, Otto Candies).
- **Targets in `outreach_priority: Defer`:** 3.

---

## Matrix-Fill Execution Backlog (follow-up issues to open)

Per [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) acceptance criterion #4, follow-up issues should be opened for high-value targets with insufficient evidence depth before the brochure-send lane ([#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556)) consumes this matrix. **BLOCKER for `status:plan-review`: required follow-up issues for High-priority rows with insufficient deep-link/pain-point evidence are not yet opened.** The lane that produced this scaffold intentionally stopped before issue creation to avoid mutating backlog against a draft that may pivot during review.

Recommended issues to file after user review:

1. **Per-target deep-link verification.** For each High-priority target: confirm fleet/project deep-link URLs, vessel datasheet pages, and any current public project announcements. Output: keep `corporate_root_evidence` as the official-domain anchor, fill `deep_link_evidence` with verified public subpages, and add fetch-date footnotes.
2. **FOWT worked example unblock.** Targets 8 (Van Oord), 9 (DEME), 13 (Seaway7), 14 (Cadeler), 17 (JDN-wind) are blocked on the OC4-DeepCwind FOWT mooring screening 1-pager (`outreach-candidate-briefs-2026-04-28.md` §4.3). Open issue: "feat(gtm): FOWT mooring screening worked example — OC4-DeepCwind reference geometry, 1-pager output".
3. **Ex-EMAS hull mapping.** If the SE Asia / Gulf small-barge segment becomes a focus lane, file a research issue: "DATA: map ex-EMAS / Ezra hulls to current operators (2017+ restructuring)".
4. **GoM-niche ICP confirmation.** Targets 15 (Helix), 20 (Otto Candies) sit in the GoM niche segment. If the user confirms GoM is in scope at High priority, file a research issue to expand GoM-niche coverage (Hornbeck, Edison Chouest, Tidewater) before the next iteration of this matrix.

---

## Cross-References

- **Email templates:** `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` — three-step Day 0/3/7 sequence with placeholder slots that this matrix's `pain_point_hypothesis` field is designed to fill.
- **Capability framing:** `docs/gtm/capability-summary.md`, `docs/gtm/capability-map.md`.
- **Buyer-segment briefs (deeper proof paths):** `docs/gtm/outreach-candidate-briefs-2026-04-28.md` Candidates 3 / 4 / 5 (vessel-installation segment) and Candidate 8 (methodology lane).
- **Adjacent segment scope notes (out-of-scope-for-this-matrix but referenced):** `docs/gtm/marine-terminal-engineering-scope.md` (LNG terminals), `docs/gtm/fowt-engineering-scope.md` (floating wind).
- **Demo proof anchors:** `digitalmodel/examples/demos/gtm/output/demo_03_mudmat_installation_report.html`, `demo_04_shallow_pipelay_report.html`, `demo_05_jumper_installation_report.html`.
- **Vessel-spec data dependency:** [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) (pipelay barge specs collection) — provides spec depth for Targets 1, 3, 4, 5, 7, 12.

---

## Authoring Honesty Footnote

Built from public-corpus sources only:

- [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) tier seed list (publicly known company names).
- [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) public vessel inventory.
- `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (already-public proof framing).
- Each `corporate_root_evidence` value is an official-domain root the reader can verify; `deep_link_evidence` and `pain_point_evidence` are separated so missing proof is visible instead of implied.

No private contact data, client-derived information, or unverified deep-links were inserted into this scaffold. Live deep-link confirmation, contact-route discovery, and pain-point hardening are matrix-fill execution work tracked in the backlog above.
