# Installation Analysis Method Note

Purpose: define ACE's current installation-analysis screening method, its present decision value, and the next fidelity upgrade path without overstating what is already implemented.

This note is written as an engineering reference first. It is intended to be reusable as source material for future website copy, proposals, and buyer-facing capability summaries.

## Grounding

This note is based on the current GTM and engineering scoping documents:
- `docs/gtm/core-engineering-work-conversion.md` — Workstream 2: Installation Analysis Fidelity Upgrade Packet
- `docs/gtm/capability-map.md` — current Demo 3 scope, outputs, and identified fidelity gap
- `docs/gtm/gif-screencast-scripts.md` — Demo 3 storyboard framing around vessel / structure / depth go-no-go screening and weather-window support

## 1. Scope

The focus here is offshore lift and lowering screening for deepwater subsea structures where vessel capability, rigging configuration, and sea state determine whether an operation is operable, marginal, or clearly outside acceptable limits.

The method note covers two distinct layers:

1. Current ACE screening capability
   - represented today by Demo 3
   - intended for rapid go/no-go screening across a matrix of structures, vessels, rigging choices, and sea states
   - useful for early vessel selection, preliminary weather limits, and identification of governing load drivers

2. Next ACE fidelity upgrade path
   - not claimed as implemented today unless separately built and verified in workflow/code
   - intended to improve realism in splash-zone transit and water-entry behavior
   - focused on segmented hydrodynamic loading, fuller geometry representation, and perforation/open-area handling

## 2. Current Method Baseline

The current baseline is the Demo 3 installation screening workflow described in the capability map.

Current documented sweep:
- structure mass
- sling configuration
- vessel crane
- Hs/Tp sea states

Current documented outputs:
- dynamic amplification factor (DAF)
- sling loads
- crane utilisation
- weather window

Current documented framing from the demo storyboard:
- vessel / structure / depth compatibility screening
- go/no-go classification
- weather-window decision support

What this means in practical engineering terms:
- the current method is a screening-level parametric lift assessment
- it is designed to compare alternatives quickly and highlight combinations that are obviously feasible, obviously infeasible, or operationally marginal
- it is already useful when the client decision is about ranking options, narrowing the candidate vessel set, or identifying where deeper study is justified

## 3. Explicit Boundary: Current Screening vs. Next Fidelity Upgrade

### 3.1 Current ACE screening capability

ACE can credibly say today that Demo 3 supports:
- rapid comparison of vessel / structure / rigging combinations
- screening of sea-state sensitivity using Hs/Tp cases
- estimation of DAF, sling loads, crane utilisation, and weather-window implications at screening level
- generation of go/no-go style decision matrices for tendering, concept selection, and early procedure development
- identification of cases where splash-zone effects are likely to govern and where DAF-only thinking is insufficient

### 3.2 Next fidelity upgrade path

ACE should describe the following as the intended enhancement path, not as a currently deployed baseline:
- segmented hydrodynamic loading across the lifted structure
- explicit phase separation for air, first water contact, splash-zone transit, lowering, and landing
- greater attention to heave and pitch realism during water entry and splash-zone passage
- representation of full lifted geometry rather than only total mass and centre-point hydrodynamics
- treatment of perforation / open-area effects where they materially alter loading

That boundary matters because the existing documents explicitly warn against marketing segmented hydrodynamic loading as already implemented in Demo 3 unless the method exists in code/workflow.

## 4. What Demo 3 Can Answer Now

At current screening fidelity, Demo 3 can answer buyer-relevant engineering questions such as:

- Which vessel crane capacities are clearly sufficient, marginal, or insufficient for a given structure set?
- How does the go/no-go picture change as structure mass increases?
- Which sling configurations materially improve or worsen utilisation and dynamic response?
- Which Hs/Tp combinations remain within screening limits for a given lift setup?
- Which combinations appear to be governed by splash-zone effects rather than static hook load alone?
- Where is a larger vessel justified, and where is it unnecessary at screening level?
- Which candidate lifts should advance into higher-fidelity procedure engineering?

This is useful for:
- bid-stage feasibility checks
- pre-FEED and FEED option screening
- vessel shortlist development
- identifying likely weather-sensitive lifts before detailed modelling begins
- focusing detailed engineering effort on the cases that actually govern the campaign

## 5. What Demo 3 Does Not Answer

The current screening method should not be presented as answering the following in a detailed or certification-grade sense:

- local load variation across a complex lifted geometry during water entry
- phase-resolved impact and transient loading at first water contact
- distributed hydrodynamic effects that drive differential motion, attitude change, or localized peak loads
- perforation/open-area effects at member or panel level
- detailed flow interaction around complex subsea frames, mudmats, manifolds, or perforated structures
- final procedure sign-off for execution-critical splash-zone behavior
- detailed landing impact or seabed contact mechanics
- full coupled dynamic installation simulation suitable to replace specialist high-fidelity modelling

In short: Demo 3 is a credible screening tool, not yet a substitute for a dedicated high-fidelity installation model when offshore consequences depend on local transient effects.

## 6. Lift Phases That Should Be Treated Separately

A higher-confidence installation method should treat the following phases separately because the governing physics and controlling parameters change from phase to phase.

### 6.1 Air phase
- Hook load, rigging geometry, crane capacity, and vessel motions dominate.
- Hydrodynamic loading is absent, but DAF, rigging load sharing, and crane margin still matter.
- This phase is often the least ambiguous at screening level.

### 6.2 First water contact
- Initial wetting can create a rapid shift from dry lifted mass to fluid-interaction-driven loading.
- Transient entry effects may create short-duration peaks not captured by simple single-point representations.
- Geometry orientation begins to matter more strongly here.

### 6.3 Splash-zone transit
- This is commonly the critical phase for larger subsea structures.
- The capability map already captures the key current insight: for 200 te+ structures, splash-zone slamming can govern and DAF alone can be misleading.
- This is the phase most likely to benefit from segmented hydrodynamic loading and stronger heave/pitch treatment.

### 6.4 Lowering phase
- Once fully submerged, the lift can become more stable, but depth-dependent response, hydrodynamic drag, and vessel motion transfer still affect loads and operability.
- Screening still needs to account for sea-state sensitivity and vessel/rigging compatibility.

### 6.5 Landing phase
- Final placement introduces seabed approach, orientation control, touchdown tolerance, and landing impact considerations.
- For many structures this requires separate treatment from general lowering because local support conditions and installation tolerances govern.

## 7. Why Segmented Loading Matters

The engineering case for segmented hydrodynamic loading is straightforward: large subsea structures do not behave like point masses during water entry and splash-zone passage.

A single-point or centre-based representation can miss:
- vertical load variation across the geometry
- pitch-inducing moment effects when one part of the structure engages water before another
- phase-dependent wetted area changes
- local drag and inertia differences between dense solid regions and open framed regions
- transitions where the governing response is attitude-driven rather than purely mass-driven

That is why the capability map positions segmented loading as the next method improvement. The expected benefit is not cosmetic model complexity; it is better physical realism in:
- heave response
- pitch response
- splash-zone and water-entry weather limits
- interpretation of which part of the structure actually governs the operation

The right technical claim today is therefore:
- segmented loading is the logical next enhancement path because it should improve realism and make weather limits more trustworthy
- segmented loading should not be claimed as a current Demo 3 baseline unless implemented and verified

## 8. Geometry and Perforation / Open-Area Effects

For large subsea structures, total lifted mass is not enough to define the governing installation response.

Geometry matters because:
- projected area changes with orientation
- members at different elevations enter the water at different times
- offset buoyancy and drag can create moments as well as direct vertical load effects
- frame depth, panel arrangement, and local shielding can shift the dominant response mode

Perforation and open-area effects matter because:
- two structures with similar mass can experience materially different hydrodynamic loading if one is more open than the other
- porous or perforated panels can reduce some load components relative to solid surfaces
- highly open frames can still produce non-uniform distributed loading, especially during partial submergence
- local flow interaction may alter both magnitude and distribution of loads

Engineering implication:
- the current screening method can indicate where these effects are likely important
- the next fidelity step should explicitly represent them where they materially change load distribution, motions, or weather limits

## 9. Operational Outputs the Method Should Support

Whether at current screening fidelity or after enhancement, the method is only valuable if it improves actual offshore decisions.

### 9.1 Weather limit
The method should support statements such as:
- approximate screening weather limit for a vessel / structure / rigging combination
- sensitivity of operability to Hs/Tp changes
- identification of whether the governing limit appears to be crane utilisation, rigging load, or splash-zone dynamics

Current honesty boundary:
- screening-level weather windows can be generated now
- higher-confidence splash-zone and water-entry weather limits depend on the planned fidelity upgrade

### 9.2 Vessel choice
The method should support:
- ranking candidate vessels against the same lift scope
- identifying where extra crane capacity provides real operability benefit versus unnecessary cost
- highlighting when a vessel change is driven by dynamic behavior rather than static capacity alone

This aligns directly with Demo 3's current go/no-go vessel matrix framing.

### 9.3 Procedure confidence
The method should support:
- deciding whether a lift looks straightforward, marginal, or sensitive enough to require deeper engineering
- identifying which phase likely governs the procedure
- deciding whether a simplified screening result is sufficient for planning, or whether a higher-fidelity analysis is required before procedure freeze

Current honesty boundary:
- Demo 3 can improve confidence in early decision-making
- it should not yet be sold as final procedure assurance for complex splash-zone-sensitive lifts

## 10. Assumptions and Limitations

The current baseline should be presented with explicit assumptions and limitations.

### 10.1 Screening-level assumptions
- the workflow is intended for rapid comparison across many cases, not one-off high-fidelity reconstruction of every transient event
- sea states are represented through Hs/Tp screening inputs
- the present method is documented around vessel crane, structure mass, sling configuration, and sea-state variation
- outputs are intended to guide option selection and escalation to deeper study where needed

### 10.2 Limitations to state clearly
- current Demo 3 documentation does not establish segmented hydrodynamic loading as implemented baseline capability
- geometry-specific distributed loading is not yet described as part of the live screening workflow
- local perforation/open-area treatment is identified as important, but not yet documented as operationalized in the current demo
- splash-zone criticality is recognized, but the current tool should still be framed as screening-level support rather than full execution assurance
- landing/seabed interaction and other local end-state effects are outside what should be implied by the current demo framing

## 11. Recommended Enhancement Backlog

The next engineering backlog should focus on improvements that materially change decision quality rather than adding complexity for its own sake.

### Priority 1 — Phase-separated installation model
- Separate air, first water contact, splash-zone transit, lowering, and landing in the method logic.
- Make governing phase explicit in outputs.
- Benefit: clearer procedure risk identification and more honest weather-limit statements.

### Priority 2 — Segmented hydrodynamic load representation
- Break the lifted structure into physically meaningful load segments.
- Track distributed wetted area development during water entry and splash-zone transit.
- Benefit: improved heave/pitch realism and more trustworthy splash-zone limits.

### Priority 3 — Geometry-aware input definition
- Add geometry descriptors beyond total mass and simple global properties.
- Enable modelling of structures where plan area, depth, asymmetry, or appendages materially affect response.
- Benefit: better transfer from generic screening to structure-specific engineering.

### Priority 4 — Perforation / open-area modifiers
- Introduce a controlled way to represent porous, perforated, or open-frame behavior.
- Prioritize structure classes where these effects are known to shift loads materially.
- Benefit: more realistic treatment of subsea frames, mudmats, and panelized structures.

### Priority 5 — Output refinement for buyers and procedure teams
- Report governing phase, governing mechanism, and confidence level alongside go/no-go status.
- Distinguish clearly between screening weather window and upgraded-analysis weather window.
- Benefit: avoids over-interpretation and makes the output more actionable.

### Priority 6 — Validation and benchmark note
- Compare the upgraded method against one or more representative installation cases or trusted references.
- Document where the upgraded method changes conclusions relative to simple DAF-led screening.
- Benefit: gives ACE a defensible basis for stronger future public claims.

## 12. Can Say Now / Cannot Claim Yet

### 12.1 Can say now
- ACE has a production Demo 3 workflow for deepwater installation / lift screening.
- The current screening sweep covers structure mass, sling configuration, vessel crane, and Hs/Tp sea states.
- Current outputs include DAF, sling loads, crane utilisation, and weather window.
- The current method supports vessel / structure / depth go/no-go screening and weather-window decision support.
- Current screening indicates that splash-zone slamming can govern for 200 te+ structures and that DAF alone can be misleading.
- ACE can use the method to screen alternatives quickly and identify which cases deserve deeper engineering.

### 12.2 Cannot claim yet
- That segmented hydrodynamic loading is already implemented in the current Demo 3 workflow.
- That full geometry interaction is already captured in the current screening baseline.
- That perforation/open-area effects are already modelled in the documented live method.
- That current Demo 3 results alone provide final procedure sign-off confidence for complex splash-zone-sensitive lifts.
- That the present screening workflow replaces dedicated high-fidelity installation simulation for execution-critical decisions.

## 13. Recommended Positioning Statement

A technically honest positioning statement for ACE today is:

ACE currently provides rapid installation screening for offshore lifts using vessel, rigging, structure, and sea-state parametrics to generate DAF, sling-load, crane-utilisation, and weather-window decision support. The present method is strong for early go/no-go screening and vessel comparison. The next fidelity upgrade path is to add segmented hydrodynamic loading, phase-separated water-entry treatment, and geometry/open-area effects so splash-zone and water-entry limits can be stated with higher confidence.

## 14. Bottom Line

The present ACE installation capability is already valuable if it is sold and used as a screening method.

Its real engineering value today is speed, comparison power, and honest identification of what governs. Its next value step is not generic “more detailed modelling,” but a specific fidelity upgrade focused on the parts of the lift where simplified representations are most likely to mislead: first water contact, splash-zone transit, geometry-driven attitude response, and perforation/open-area effects.

That is the correct foundation for future website copy and for any higher-confidence installation-analysis offering ACE chooses to build next.
