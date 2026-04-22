# GTM Content -> Core Engineering Work Conversion

Purpose: convert the recent LinkedIn-inspired GTM ideas into engineering-first work packages that can be executed with resources already present in the workspace.

## Available Resources We Can Use Now

### Existing GTM/demo assets
- `docs/gtm/capability-map.md` — current service/capability inventory
- `docs/gtm/capability-summary.md` — compact buyer-facing positioning
- `docs/gtm/client-conversion-pipeline.md` — service-line and funnel framing
- `docs/gtm/linkedin-content-calendar.md` — message backlog and reserve posts
- `docs/gtm/gif-screencast-scripts.md` — storyboard and demo recording guidance
- `digitalmodel/examples/demos/gtm/` — 5 existing GTM demo workflows and reports

### Floating wind resources already available
- `docs/research/weis-floating-wind-eval.md` — phased recommendation already grounded in RAFT + MoorPy + WEIS
- `docs/resources/marine-resources.md` — tracked resources for RAFT, MoorPy, MoorDyn, OpenFAST, API 2SK, DNV OS E301, offshore-marine references
- Installed/validated direction from research:
  - RAFT standalone is practical near-term
  - MoorPy is practical near-term
  - full WEIS/OpenFAST stack is deferred/high-complexity

### Installation-analysis resources already available
- Demo 3 in `digitalmodel/examples/demos/gtm/` for deepwater installation / lift screening
- Existing GTM narrative around splash-zone slamming and weather-window screening
- GIF/report workflow already documented in `docs/gtm/gif-screencast-scripts.md`

## Core Engineering Workstreams

These replace generic marketing tasks with engineering deliverables that can later feed LinkedIn posts, website pages, PDFs, and proposals.

---

## Workstream 1 — FOWT Screening Starter Packet

### Engineering goal
Create a technically real, near-term floating-offshore-wind capability packet using tools we can actually stand up now: RAFT + MoorPy + existing mooring/offshore standards knowledge.

### Why this is the right cut
We already have research showing RAFT and MoorPy are the practical near-term path, while full WEIS/OpenFAST remains deferred. That means the engineering work should start with screening and concept-comparison workflows, not full certification-grade coupled simulations.

### Scope
1. Define the ACE FOWT engineering boundary:
   - mooring concept screening
   - anchor strategy framing
   - tow-out / hook-up installation logic
   - integrity/fatigue planning inputs
   - O&G-to-FOWT transfer notes
2. Build a simple reference-study template around one representative floater case.
3. Produce one engineering note or benchmark showing what RAFT/MoorPy can answer now.
4. Capture the exact gaps that still require OpenFAST/WEIS or external partner capability.

### Inputs already available
- `docs/research/weis-floating-wind-eval.md`
- `docs/resources/marine-resources.md`
- mooring capability in `docs/gtm/capability-map.md`
- expert-network/renewables positioning in `docs/gtm/expert-network-profiles.md`

### Engineering outputs
- `docs/gtm/fowt-engineering-scope.md`
- `docs/gtm/fowt-screening-packet.md`
- optional: `docs/research/fowt-raft-moorpy-benchmark.md`

### Concrete engineering questions
- What FOWT questions can RAFT answer at screening fidelity?
- What mooring questions can MoorPy answer without dynamic time-domain coupling?
- What installation/integrity statements are defensible today vs deferred?
- What standards/regulatory references should be listed now?

### Definition of done
- One written FOWT scope note grounded in actual installed/available tools
- One buyer-usable screening packet outline
- One explicit “can do now / cannot claim yet” boundary section

---

## Workstream 2 — Installation Analysis Fidelity Upgrade Packet

### Engineering goal
Turn the new segmented-loading / splash-zone messaging into a real installation-analysis offering backed by the existing Demo 3 path and a clearly defined next engineering enhancement.

### Why this is the right cut
We already have installation GTM assets, but the new LinkedIn signal adds a sharper technical differentiator: segmented hydrodynamic loading, full geometry, water-entry realism, and perforation/open-area effects. That should become an engineering-method note first, not just marketing copy.

### Scope
1. Document the current installation-analysis baseline from Demo 3.
2. Define the fidelity gap between current screening and higher-fidelity segmented loading.
3. Specify the next enhancement path:
   - segmented load representation
   - splash-zone / water-entry phase separation
   - heave/pitch response emphasis
   - perforation/open-area modifier handling
4. Turn that into an engineering-method capability note plus a scoped enhancement backlog.

### Inputs already available
- Demo 3 storyboard and report framing in `docs/gtm/gif-screencast-scripts.md`
- installation positioning in `docs/gtm/capability-map.md`
- current GTM narrative in `docs/gtm/linkedin-content-calendar.md`

### Engineering outputs
- `docs/gtm/installation-analysis-method-note.md`
- `docs/gtm/installation-analysis-enhancement-backlog.md`

### Concrete engineering questions
- What does Demo 3 currently screen vs not screen?
- Which lift phases need separate treatment: air, first water contact, splash-zone transit, lowering, landing?
- What minimum geometry segmentation is worth implementing first?
- Where do open-area/perforation effects materially change loads?
- What weather-limit statements are valid at current fidelity vs upgraded fidelity?

### Definition of done
- One engineering note that explains the current method honestly
- One enhancement backlog for higher-fidelity installation analysis
- One section mapping the method to client decisions: weather limits, vessel choice, procedure confidence

---

## Workstream 3 — Marine Structures / Load-Path Explainer as Engineering Reference

### Engineering goal
Convert the shear-force/bending-moment content lane into an internal reference and client-education engineering note focused on offshore transport, ballast/load changes, seafastening, and installation load paths.

### Why this is the right cut
The LinkedIn post showed the topic is attractive but vulnerable to credibility loss if diagrams are sloppy. So the first deliverable should be a technically correct ACE reference note with offshore examples.

### Scope
1. Create one clean engineering explainer note.
2. Use offshore examples rather than classroom-only beams.
3. Build the diagrams once, then reuse them in GTM and website assets.

### Inputs already available
- marine resource inventory in `docs/resources/marine-resources.md`
- ACE transport/installation positioning already embedded in GTM docs

### Engineering outputs
- `docs/gtm/marine-load-paths-explainer.md`
- optional derived figures under `docs/gtm/media/`

### Definition of done
- One technically correct explainer with sign conventions, load-path logic, and offshore examples
- Reusable figure list for website and LinkedIn adaptation

---

## Workstream 4 — Website Pages Derived from Engineering Notes, Not Vice Versa

### Engineering goal
Only build website copy after the engineering notes above exist.

### Why this is the right cut
The website should be a thin presentation layer over real engineering artifacts. That prevents overclaiming and keeps ACE’s public positioning tied to what can be executed now.

### Pages to derive after Workstreams 1-3
1. FOWT capability page
2. Installation analysis capability page
3. Marine structures / transport load-path explainer page

### Inputs
- engineering notes from Workstreams 1-3
- existing website-page pattern under `docs/gtm/website-pages/`

### Proposed outputs
- `docs/gtm/website-pages/fowt-capability.html`
- `docs/gtm/website-pages/installation-analysis.html`
- `docs/gtm/website-pages/marine-load-paths.html`

### Definition of done
Each page has:
- a real engineering scope section
- a “what we can answer quickly” section
- a “what requires deeper study” section
- one figure or table grounded in the engineering notes

---

## Execution Order

1. Workstream 2 — Installation Analysis Fidelity Upgrade Packet
   - fastest path because Demo 3 and GTM assets already exist
2. Workstream 1 — FOWT Screening Starter Packet
   - feasible now with RAFT/MoorPy/WEIS research already documented
3. Workstream 3 — Marine Structures / Load-Path Explainer
   - useful authority asset, but less directly tied to current demo pipeline
4. Workstream 4 — Website Pages
   - only after engineering notes exist

## What Not To Do Yet

- Do not claim full WEIS/OpenFAST FOWT design capability as a live ACE offering yet.
- Do not market segmented hydrodynamic loading as already implemented in Demo 3 unless the engineering method actually exists in code/workflow.
- Do not publish marine-structures graphics until sign conventions and end conditions have been reviewed.

## Recommended Next Engineering Actions

### Immediate
- Write `docs/gtm/installation-analysis-method-note.md`
- Write `docs/gtm/fowt-engineering-scope.md`

### Next
- Decide whether RAFT + MoorPy benchmark execution is worth doing now or remains research-only
- Decide whether Demo 3 should stay a screening product or get a new high-fidelity follow-on path

## Summary

If we convert “draft LinkedIn posts” and “website copy” into core engineering work, the right deliverables are:
- engineering scope notes
- method notes
- benchmark/validation notes
- enhancement backlogs
- only then public-facing website pages and post copy

That keeps GTM anchored to real capability already supported by the workspace rather than aspirational messaging.
