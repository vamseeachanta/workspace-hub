---
name: gtm-signal-to-engineering-artifact-conversion
description: Convert external GTM signals (LinkedIn posts, conference programme pages, industry pages) into engineering-first ACE artifacts, then derive wiki and GTM updates with explicit evidence boundaries.
version: 1.0.0
category: workspace-hub-learned
tags:
  - gtm
  - engineering
  - wiki
  - linkedin
  - conference-signals
  - parallel-agents
applies-to:
  - hermes
  - claude
  - codex
trigger: manual
auto_execute: false
---

# GTM Signal -> Engineering Artifact Conversion

Use when the input is an external market/content signal (LinkedIn post, conference programme, industry page) and the user wants ACE GTM/wiki work updated without drifting into hype.

## Core rule
Treat public posts/programmes as:
- topic signals
- market-interest validation

Do NOT treat them as:
- design evidence
- standards basis
- numerical criteria source

Always convert the signal into an engineering artifact first, then derive GTM/web copy later.

## When to use
- User shares LinkedIn posts and asks to "add this to GTM"
- User shares conference programme pages and asks what can be extracted
- User wants new ACE capability areas added from market signals
- User wants llm-wiki updates tied to LNG/FOWT/marine/offshore themes

## Proven workflow

### 1. Extract only supported signal content
Use browser tools to capture:
- exact session/topic titles
- explicit themes named on-page
- what is clearly stated vs inferred

Summarize in two buckets:
- useful signal
- not enough for engineering claims

### 2. Check existing GTM and wiki coverage
Read the current ACE docs first:
- `docs/gtm/capability-map.md`
- `docs/gtm/client-conversion-pipeline.md`
- `docs/gtm/linkedin-content-calendar.md`
- `docs/gtm/core-engineering-work-conversion.md`

For wiki work, inspect:
- target wiki `index.md`
- target wiki `log.md`
- related entity/concept/source pages already present

### 3. Convert to engineering-first deliverables
Before drafting posts or website copy, create one or more of:
- engineering scope note
- method note
- screening packet outline
- enhancement backlog
- concept/synthesis wiki page

Good examples from this session:
- `docs/gtm/fowt-engineering-scope.md`
- `docs/gtm/installation-analysis-method-note.md`
- `docs/gtm/marine-terminal-engineering-scope.md`
- `docs/gtm/lng-berth-operability-framing.md`

### 4. Keep capability boundaries explicit
Every new scope note should include:
- what ACE can do now
- what requires project-specific inputs
- what needs deeper tools or partners
- can-say-now / cannot-claim-yet

Examples learned here:
- FOWT: near-term claim = RAFT + MoorPy screening, not full WEIS/OpenFAST certification-grade design
- installation analysis: segmented hydrodynamic loading is an enhancement path, not a current implemented baseline unless code/workflow exists
- marine terminals: LNG conference programmes justify topic relevance only; real terminal conclusions require vessel, berth, metocean, transfer, and criteria data

### 5. Update the wiki as a concept cluster, not a one-off page
For new domains, create:
- one source page for the signal itself
- one synthesis concept page
- 2-3 follow-on concept pages if the cluster is already justified

For marine terminals, the proven cluster was:
- source: `lng2026-tp04-shipping-marine-port-operations.md`
- concept: `lng-marine-terminal-engineering.md`
- follow-ons:
  - `lng-berth-operability.md`
  - `lng-transfer-system-envelope.md`
  - `fsru-marine-terminal-interface.md`

Update:
- `index.md`
- `log.md`
- related existing pages for cross-links

### 6. Then update GTM docs
After the engineering artifact exists, update GTM docs with engineering-first wording:
- capability line in `capability-summary.md`
- discipline row + overlay in `capability-map.md`
- service line and audience in `client-conversion-pipeline.md`
- reserve post idea in `linkedin-content-calendar.md`
- workstream entry in `core-engineering-work-conversion.md`

## Parallel-agent pattern
Use parallel subagents when the two tracks are independent:
1. wiki expansion
2. GTM doc integration

Then use parallel subagents again for derived scope-note drafting.

Recommended pairings:
- Wave 1:
  - agent A: deepen wiki cluster
  - agent B: update GTM docs
- Wave 2:
  - agent A: draft engineering scope note
  - agent B: draft buyer-usable framing note

## Output pattern that worked well
For any new capability area, produce this ladder:
1. signal/source summary
2. wiki concept cluster
3. GTM capability integration
4. engineering scope note
5. buyer-facing framing note
6. only later: website page or LinkedIn post

## Pitfalls
- Do not let conference pages become pseudo-standards
- Do not claim implemented modeling fidelity that is only proposed
- Do not add generic marketing language before the engineering note exists
- In this repo, `knowledge/wikis/*` may be gitignored; remember future commits may require `git add -f`
- Re-read files after subagent edits before further patching to avoid stale-context mistakes

## Reusable summary
If the user says “add this external post/page to GTM,” the safest, highest-value response is:
- extract supported signals
- create engineering-first notes
- expand the wiki cluster
- then update GTM docs with explicit evidence boundaries
