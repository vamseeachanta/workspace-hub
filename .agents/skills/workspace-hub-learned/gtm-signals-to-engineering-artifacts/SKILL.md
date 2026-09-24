---
name: gtm-signals-to-engineering-artifacts
description: Convert external GTM signals (LinkedIn posts, competitor messaging, market
  themes) into engineering-first ACE artifacts before drafting marketing copy.
version: 1.0.0
category: workspace-hub-learned
applies-to:
- hermes
- claude
- codex
- gemini
trigger: manual
auto_execute: false
tags:
- gtm
- engineering
- fowt
- installation-analysis
- linkedin
- capability-packaging
---

# GTM Signals -> Engineering Artifacts

Use when the user asks to review external posts/content (especially LinkedIn) and "add it to GTM," but wants the result grounded in real ACE engineering capability rather than generic marketing language.

## When to use
- Reviewing competitor or adjacent-industry posts for GTM improvements
- Turning market-facing ideas into real capability packaging
- Converting proposed LinkedIn posts / website copy into engineering work
- Adding new capability areas (for example FOWT) without overclaiming current readiness

## Core principle
Do not stop at messaging. First convert the GTM signal into an engineering artifact:
- scope note
- method note
- benchmark / validation note
- enhancement backlog
- screening packet outline
Only after that should website copy or social posts be derived.

## Proven workflow

### 1. Extract the signal from the external content
For each post, identify:
- the engineering theme
- the operational/business claim
- the differentiator being implied
- the proof gap (what is said visually or rhetorically but not quantified)

Useful buckets from this session:
- engineering-led offshore execution
- engineer-grade explainers with technically correct graphics
- FOWT as O&G-to-renewables transfer (moorings, installation, integrity)
- installation-analysis fidelity (segmented loading, splash-zone realism, geometry/perforation effects)

### 2. Inventory existing resources before proposing work
Ground everything in repo evidence. Read the closest source docs first.

In this session, the most useful anchors were:
- `docs/gtm/capability-map.md`
- `docs/gtm/capability-summary.md`
- `docs/gtm/client-conversion-pipeline.md`
- `docs/gtm/linkedin-content-calendar.md`
- `docs/gtm/gif-screencast-scripts.md`
- `docs/research/weis-floating-wind-eval.md`
- `docs/resources/marine-resources.md`
- `docs/gtm/expert-network-profiles.md`

### 3. Convert each GTM idea into a workstream
Use a short engineering-first conversion doc to define:
- engineering goal
- why this is the right near-term cut
- inputs already available
- outputs to create
- concrete engineering questions
- definition of done

Proven output path from this session:
- `docs/gtm/core-engineering-work-conversion.md`

### 4. Enforce honesty boundaries
For each new capability, separate:
- what ACE can say now
- what ACE cannot claim yet
- what is the next fidelity upgrade path

Critical examples from this session:
- Do not claim full WEIS/OpenFAST certification-grade FOWT capability yet.
- Do not claim segmented hydrodynamic loading is already implemented in Demo 3 unless code/workflow actually exists.
- Do not publish mechanics graphics until sign conventions and boundary conditions are technically correct.

### 5. Prefer engineering notes before website pages
Create engineering-first source docs such as:
- `docs/gtm/fowt-engineering-scope.md`
- `docs/gtm/installation-analysis-method-note.md`

These become the canonical source for:
- website pages
- screening packets
- proposals
- LinkedIn posts
- one-pagers

### 6. Use parallel subagents for independent notes
If two notes are independent (for example FOWT scope + installation method note), dispatch them in parallel with `delegate_task(tasks=[...])`.
Pass exact grounding files and explicit honesty constraints into each subagent.

Proven pattern:
- one subagent writes the installation note grounded in Demo 3, capability map, and GTM demo docs
- one subagent writes the FOWT scope note grounded in WEIS/RAFT/MoorPy research and marine resources
- main agent reviews both and keeps them as canonical engineering sources

## Recommended artifact sequence

### For FOWT
1. Engineering scope note
2. Screening packet outline
3. Optional RAFT/MoorPy benchmark note
4. Website page / outreach collateral derived from the above

### For installation analysis
1. Method note describing current baseline honestly
2. Enhancement backlog for higher-fidelity upgrades
3. Website/service page derived from the note
4. Social/content pieces derived from the note

## Good deliverables
- Scope note with explicit near-term boundary
- Method note distinguishing screening vs detailed analysis
- Enhancement backlog listing the next engineering improvements
- Conversion document that maps GTM ideas to engineering workstreams

## Pitfalls
- Writing marketing copy first and engineering notes later
- Treating a useful GTM idea as if it proves implementation readiness
- Blurring current screening capability with planned higher-fidelity capability
- Adding FOWT messaging without checking actual tool/resource readiness
- Reusing technically weak third-party educational diagrams instead of creating reviewed ACE versions

## Exit condition
This workflow is complete when:
- the GTM signal has been translated into one or more engineering artifacts
- each artifact is grounded in actual repo resources or documented research
- capability claims are split into "can say now" vs "cannot claim yet"
- downstream website/post work is clearly derivative of the engineering notes rather than the other way around
