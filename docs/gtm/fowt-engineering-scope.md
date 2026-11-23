# FOWT Engineering Scope Note

Purpose: define an engineering-first ACE floating offshore wind scope that is grounded in tools, standards, and domain capability already available in the workspace, and that can be reused as the source document for later screening-packet and website work.

## 1. Why FOWT is Relevant to ACE

Floating offshore wind is a credible adjacency for ACE because the early engineering questions overlap strongly with established offshore oil and gas disciplines already present in ACE's capability base:

- stationkeeping and mooring concept selection
- anchor strategy framing
- tow-out, hook-up, and marine operations planning
- fatigue and integrity planning for lines, connectors, and offshore hardware
- weather-limited installation and offshore execution logic
- technical assurance for buyers, investors, and developers who need an engineering reality check before detailed design

The relevant transfer is not "ACE already does full wind turbine design." The relevant transfer is that floating wind projects still depend on offshore mooring, installation, integrity, and operability decisions that look familiar to deepwater engineering teams, even though the load environment, farm-scale repetition, and wind-turbine coupling requirements are different.

That distinction matters. ACE can contribute now where offshore engineering transfer is real, and should avoid overstating capability where floating wind requires a deeper aero-hydro-servo-elastic toolchain.

## 2. Near-Term ACE FOWT Engineering Boundary

ACE's near-term FOWT position should be defined as a screening, concept-framing, and technical-assurance scope built around mooring and offshore execution work, not as a full certification-grade floating wind design offering.

ACE can credibly position near-term FOWT work as:

- mooring concept screening for semi-sub, spar, or other floater arrangements at pre-FEED / early FEED level
- anchor strategy framing based on seabed, line concept, installation logic, and integrity implications
- quasi-static mooring response and stiffness screening
- floating platform response screening at frequency-domain level where RAFT is appropriate
- weather-limited tow-out, hook-up, and installation logic
- fatigue / integrity planning inputs for mooring components and associated offshore systems
- technical review of whether a concept needs deeper coupled analysis before major project decisions
- bankability-oriented technical assurance on engineering maturity, scope gaps, and escalation triggers

ACE should not claim, at this stage:

- full certification-grade coupled aero-hydro-servo-elastic design
- complete IEC design load case execution
- full controller co-design capability
- detailed time-domain load verification across the full turbine-platform-mooring system
- final class / certification support without partner tools and workflows beyond the current near-term stack

This boundary aligns with Workstream 1 in `docs/gtm/core-engineering-work-conversion.md`, which defines the FOWT Screening Starter Packet around mooring concept screening, anchor strategy framing, tow-out / hook-up logic, integrity planning inputs, and explicit capture of the gaps that still require OpenFAST / WEIS or external partners.

## 3. What ACE Can Do Now

Grounded in the current capability map and expert positioning, ACE can lead with the following FOWT work now.

### 3.1 Mooring and stationkeeping screening

ACE can perform early-stage concept screening around:

- catenary vs taut or hybrid mooring concept logic
- line arrangement tradeoffs
- line stiffness implications at screening level
- high-level line load and restoring-behavior comparisons
- anchor concept framing and preliminary installation implications
- damaged-case or reserve-margin discussion at a screening level, with clear fidelity limits stated

### 3.2 Anchor and foundation strategy framing

ACE can frame:

- likely anchor families suited to mooring concept and seabed conditions
- installation sequence implications of drag, suction, or other anchor choices
- inspection, integrity, and replacement considerations
- where geotechnical and specialized anchor design work must be handed off to partner specialists

### 3.3 Floating response screening for concept comparison

Using the practical near-term path identified in existing research, ACE can use RAFT-based frequency-domain screening to compare concepts and identify first-order response issues such as:

- platform motion tendencies relevant to concept ranking
- sensitivity of response to mooring stiffness assumptions
- early identification of concepts that likely require deeper coupled analysis
- response trends useful for screening tow-out, hook-up, and operability questions

### 3.4 Installation and marine operations logic

ACE can contribute directly on:

- tow-out configuration logic
- hook-up / connection sequence framing
- weather-window considerations for installation steps
- offshore execution constraints that affect concept selection
- interface logic between fabrication, quayside integration, tow-out, field connection, and commissioning

### 3.5 Fatigue, integrity, and technical-assurance framing

ACE can support:

- mooring integrity planning inputs
- identification of likely fatigue drivers requiring detailed follow-on analysis
- inspection and life-management planning logic adapted from offshore practice
- independent technical review of whether a concept is mature enough for the next decision gate
- buyer-facing explanation of what has been screened, what remains uncertain, and what must be escalated

This matches the FOWT overlay in `docs/gtm/capability-map.md`, which says ACE can lead with mooring concept selection, anchor strategy, fatigue/integrity planning, weather-limited installation logic, tow-out/hook-up planning, and bankability-oriented technical assurance.

## 4. Tools and Resources That Support This Scope Now

## 4.1 Practical near-term analysis stack

The current research basis is explicit: the practical near-term path is RAFT standalone plus MoorPy; full WEIS / OpenFAST is deferred because of complexity and compute burden.

From `docs/research/weis-floating-wind-eval.md`:

- RAFT alone is lightweight and practical for Level 1 frequency-domain analysis
- MoorPy is practical and low-risk for near-term quasi-static mooring work
- RAFT + MoorPy are the most accessible entry point for floating offshore engineering without committing to the full WEIS stack
- full WEIS fills major gaps, but at significant complexity cost

The same note also documents that standalone RAFT and MoorPy are already installed in `/mnt/local-analysis/raft-env`, supporting the claim that the near-term screening path is not hypothetical.

### 4.2 Resources cataloged in the workspace

`docs/resources/marine-resources.md` tracks the core resources relevant to this scope:

- RAFT for floating turbine response screening
- MoorPy for quasi-static mooring analysis
- MoorDyn for dynamic mooring follow-on scope
- OpenFAST for higher-fidelity coupled time-domain simulation
- API RP 2SK for stationkeeping-system design and analysis reference
- DNV OS E301 for position mooring reference

These resources support a layered message:

- RAFT + MoorPy = usable now for screening
- MoorDyn / OpenFAST = relevant follow-on tools, but not the current ACE front-line claim

### 4.3 ACE capability base supporting FOWT transfer

The existing ACE resource base supports the engineering transfer case through:

- mooring design capability (`digitalmodel/mooring`)
- riser and offshore system integrity orientation
- marine installation and weather-limited operations logic
- offshore structures and naval-architecture context
- expert-network positioning around mooring, riser, installation, and offshore wind foundations

`docs/gtm/expert-network-profiles.md` also supports this positioning by explicitly listing mooring system design, offshore wind foundations, floating systems, marine operations engineering, and fatigue-related topics.

## 5. Recommended Near-Term Workflow: RAFT + MoorPy Screening Path

The recommended ACE workflow for near-term FOWT work should be a screening workflow, not a disguised detailed-design workflow.

### Step 1: Define the screening question and decision gate

Examples:

- Which mooring concept is better suited to the candidate floater and site constraints?
- Does the concept appear installation-practical at an early stage?
- Are there obvious stationkeeping or operability concerns that should stop a concept before deeper study?
- Is the concept mature enough to justify escalation into a partner-led detailed design phase?

### Step 2: Establish the reference concept and assumptions

Set a representative case with:

- floater type and basic geometry assumptions
- draft, displacement, and mass-property assumptions available at screening stage
- water depth and preliminary metocean basis
- mooring layout candidates
- preliminary anchor assumptions
- key installation assumptions for tow-out and hook-up

### Step 3: Run MoorPy-based mooring screening

Use MoorPy to screen:

- line arrangement and restoring behavior
- tension and stiffness trends
- sensitivity to line-type assumptions
- first-pass comparisons among catenary, taut, or hybrid arrangements

This is the right level for early elimination or ranking, but not for claiming full dynamic verification.

### Step 4: Run RAFT-based floating response screening

Use RAFT to evaluate concept-level response trends such as:

- frequency-domain motion tendencies
- interaction between floater response and mooring stiffness assumptions
- relative suitability of concepts for early operability and response screening
- triggers indicating a need for higher-fidelity follow-on work

### Step 5: Integrate offshore execution logic

Combine analysis outputs with practical offshore engineering review:

- tow-out constraints
- hook-up sequence complexity
- weather exposure of key operations
- installation vessel or spread implications
- implications for anchor installation and field execution

### Step 6: Convert results into a decision-grade screening note

The output should answer:

- what was screened
- what concepts were compared
- what assumptions controlled the result
- what the likely next engineering gate is
- which questions remain open because the fidelity level is intentionally limited

This near-term workflow is directly consistent with the phased path in `docs/research/weis-floating-wind-eval.md`: start with RAFT standalone and MoorPy, validate value at screening level, and only escalate into full WEIS / OpenFAST when a project genuinely requires that complexity.

## 6. Candidate Questions ACE Can Answer Now

ACE can credibly answer the following types of FOWT questions now, provided the answers are explicitly framed as screening-level or concept-development work.

### Mooring and anchor questions

- Which mooring concept is directionally best aligned with the floater concept and water depth?
- How do catenary and taut-leg options compare in restoring behavior and likely installation implications?
- What anchor strategies are plausible at concept stage, and what are the major consequences for installation and integrity planning?
- Which concept assumptions are most sensitivity-driving and therefore worth maturing first?

### Floating response and operability questions

- Which floater/mooring combinations appear directionally more favorable at screening level?
- Are there obvious response trends that make a concept poor candidate for near-term development?
- Is the concept likely to require immediate escalation into higher-fidelity coupled analysis before a buyer should rely on it?

### Installation and execution questions

- What tow-out and hook-up logic should be assumed for the concept?
- Which installation steps are most weather-sensitive?
- What practical offshore execution issues are likely to dominate concept selection?
- How might anchor choice or line configuration affect field installation complexity?

### Integrity and assurance questions

- What are the most likely integrity and fatigue planning concerns that should be put on the project risk register now?
- What can be screened now versus what requires dynamic or certification-grade follow-on work?
- What is the defensible engineering scope for an early buyer or developer decision package?

## 7. Deferred or Out-of-Scope Items Requiring WEIS, OpenFAST, or Partners

The existing research is clear that WEIS and OpenFAST fill important gaps, but at significant complexity cost. ACE should therefore state these items as deferred or partner-dependent unless and until the higher-fidelity workflow is proven and productized.

### 7.1 Deferred because they require higher-fidelity coupled simulation

- full coupled aero-hydro-servo-elastic time-domain simulation
- nonlinear design load case execution across the turbine-platform-mooring system
- controller co-design and controls-sensitive optimization
- certification-oriented load verification
- detailed extreme and fatigue load assessment intended for final design signoff
- full farm-scale certification support tied to IEC load-case campaigns

`docs/research/weis-floating-wind-eval.md` identifies these as the gaps filled by the broader WEIS/OpenFAST stack: aero-hydro-servo-elastic coupled simulation, floating platform optimization, design load case automation for certification, and controller co-design capability.

### 7.2 Typically partner-led or specialist scope

- detailed wind turbine structural design
- blade, tower, nacelle, and controller design work
- geotechnical anchor capacity design and site-specific foundation engineering
- final class / certifier submission packages
- detailed cable dynamics and full-array integration studies unless separately scoped
- final procurement-grade specifications based on high-fidelity verified loads

ACE can still add value on these scopes as an offshore systems, mooring, installation, or independent-review contributor, but should not represent them as current standalone ACE delivery capability.

## 8. Standards and Resource Basis

The note should be positioned as grounded in recognized offshore references already tracked in the workspace.

### Core standards/resources to cite in this scope

- API RP 2SK — stationkeeping-system design and analysis reference
- DNV OS E301 — position mooring reference
- RAFT — frequency-domain floating turbine analysis resource
- MoorPy — quasi-static mooring analysis resource
- MoorDyn — dynamic mooring follow-on resource
- OpenFAST — higher-fidelity time-domain follow-on resource

### How these standards/resources should be used in ACE messaging

- Use API RP 2SK and DNV OS E301 as the immediate offshore engineering standards basis for mooring-related framing and screening logic.
- Use RAFT and MoorPy as the practical analysis basis for what ACE can do now.
- Use MoorDyn and OpenFAST as the explicit higher-fidelity path for deferred scopes.
- Keep standards references as support for method framing, not as implied proof that ACE is already delivering certification-grade floating wind design.

## 9. Buyer-Facing Engineering Outputs

This scope note should feed a practical set of reusable deliverables.

### Near-term outputs ACE can package now

1. FOWT engineering scope note
   - defines boundary, tools, standards basis, and escalation logic

2. FOWT screening starter packet
   - early-stage concept screening package for buyers, developers, or investors

3. Mooring and anchor concept screening memo
   - compares concept options and identifies principal risks / follow-on needs

4. Tow-out / hook-up engineering note
   - outlines marine operations logic, key interfaces, and weather-sensitive steps

5. Technical assurance / red-flag review
   - independent review of whether a floating concept appears credible at the current maturity level

6. Bankability-oriented gap register
   - explicit list of what has and has not been demonstrated at screening fidelity

### Expected characteristics of buyer-facing outputs

- short, decision-oriented, and engineering-first
- explicit assumptions and known limits
- no implied certification-grade validity
- clear escalation path to higher fidelity or partner-led detailed design
- directly reusable for website pages, proposals, and screening-packet collateral

## 10. Assumptions and Limitations

This ACE FOWT scope depends on several assumptions that should be stated every time the offering is described.

### Assumptions

- the near-term task is concept screening, option ranking, or technical-assurance review rather than final design verification
- sufficient early-stage floater, mooring, site, and metocean inputs are available to support a defensible screening study
- the client understands that screening outputs support decision gating, not final certification or procurement
- RAFT + MoorPy fidelity is appropriate for the immediate question being asked

### Limitations

- mooring outputs are near-term best suited to quasi-static and concept-level work, not full dynamic verification
- RAFT-based response screening is useful for concept comparison but is not a substitute for full nonlinear time-domain simulation where certification or final design decisions are involved
- installation and operability statements remain dependent on assumptions about metocean, vessel spread, execution method, and project-specific constraints
- fatigue and integrity commentary at this stage should be framed as planning inputs and risk identification, not final life verification
- floating wind concepts are sensitive to turbine controls, coupled loads, and detailed hydrodynamics that are outside the current ACE near-term delivery claim

## 11. Can Say Now / Cannot Claim Yet

### Can say now

- ACE can support floating offshore wind at the engineering screening level, especially where the work centers on mooring, anchor strategy, installation logic, integrity planning, and technical assurance.
- ACE's near-term FOWT analysis path is RAFT + MoorPy, supported by offshore mooring standards and existing offshore engineering capability.
- ACE can help buyers compare concepts, identify engineering red flags, and determine when a concept should be escalated into higher-fidelity analysis.
- ACE can translate offshore oil-and-gas mooring and installation experience into floating wind screening work, with clear recognition that FOWT is not identical to O&G floaters.
- ACE can produce buyer-facing screening notes and engineering packets that explain what is known, what is assumed, and what still requires deeper study.

### Cannot claim yet

- ACE should not claim full certification-grade coupled aero-hydro-servo-elastic design capability.
- ACE should not imply that RAFT + MoorPy screening is equivalent to full WEIS/OpenFAST verification.
- ACE should not market full IEC design load case execution or class / certifier-ready FOWT design support as an established standalone service yet.
- ACE should not claim mature controller co-design, full turbine optimization, or final load-verification capability.
- ACE should not imply that all floating wind design disciplines are currently in-house simply because mooring and offshore installation capabilities are strong.

## 12. Recommended Positioning Statement

ACE's near-term floating offshore wind offer is an engineering screening and technical-assurance scope centered on mooring, anchor strategy, offshore execution logic, and integrity planning, using RAFT + MoorPy as the practical analysis path now available. It is not yet a claim of full certification-grade coupled floating wind design capability.

## 13. Reuse Guidance

This note should serve as the source document for:

- `docs/gtm/fowt-screening-packet.md`
- future FOWT website copy
- proposal scope language for early-stage floating wind studies
- buyer-facing one-pagers on mooring / installation transfer from O&G to FOWT

If derivative GTM material diverges from the engineering boundary defined here, this note should control.
