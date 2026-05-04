---
name: linkedin-post-to-gtm-ingestion
description: Review external LinkedIn posts and fold reusable insights into ACE-style
  GTM docs, capability maps, and content calendars.
version: 1.0.0
category: marketing
applies-to:
- hermes
- Codex
- codex
- gemini
trigger: manual
auto_execute: false
tags:
- linkedin
- gtm
- messaging
- content-strategy
- aceengineer
---

# LinkedIn Post to GTM Ingestion

Use when the user shares one or more LinkedIn posts and asks to "add this to GTM", improve messaging, or update capability docs/content plans based on external market signals.

## Goal
Turn external LinkedIn posts into concrete GTM improvements, not just summaries.

## Inputs to gather
For each post, capture:
1. Topic/domain (subsea ops, naval structures, FOWT, installation, etc.)
2. Core message
3. Visual/marketing angle
4. Hidden differentiator or weakness
5. What ACE should add/change in:
   - capability messaging
   - website/service pages
   - LinkedIn content calendar
   - conversion pipeline / audience targeting

## Working method
1. Load the public LinkedIn post with browser tools.
2. Dismiss sign-in/join overlays.
3. Use browser snapshot to extract visible post text/comments.
4. Use browser vision when the visual itself matters (video, carousel, diagrams, subsea imagery).
5. Translate the post into GTM implications:
   - positioning angle
   - proof-point gap
   - capability gap
   - audience/CTA/content opportunity
6. Update the most relevant GTM docs directly.

## Default docs to inspect/update
Prefer these docs in ACE/workspace-hub GTM work:
- `docs/gtm/linkedin-content-calendar.md`
- `docs/gtm/client-conversion-pipeline.md`
- `docs/gtm/capability-summary.md`
- `docs/gtm/capability-map.md`
- `docs/gtm/expert-network-profiles.md` when the new angle affects market/profile positioning

## Mapping rules

### If the post emphasizes offshore execution credibility
Add/update:
- engineering-led execution messaging
- real offshore decision framing (weather window, vessel choice, lift/no-go, VIV limits)
- quantified outcome language over generic capability claims
- reserve LinkedIn posts responding with stronger technical authority

### If the post is an educational mechanics explainer
Add/update:
- engineer-grade explainer content lane
- requirement for technically correct diagrams, equations, and assumptions
- bridge from theory to service lines (transport, seafastening, ballast, structural checks)

### If the post is about floating offshore wind / energy transition
Add/update:
- FOWT capability row in capability docs if absent
- O&G-to-FOWT transfer language (moorings, installation, integrity, bankability)
- renewable buyer audience/collateral ideas
- reserve content for FOWT commercialization themes

### If the post is about installation-analysis fidelity
Add/update:
- installation-analysis detail under demo/capability sections
- segmented hydrodynamic loading vs single-point loading
- splash-zone/water-entry realism
- full geometry, flow interaction, and perforation/open-area effects where relevant
- messaging around trustworthy weather limits / workability

## Good output pattern
Do more than summarize. Typical useful changes include:
- add a new capability bullet/row
- add a new audience segment in the conversion pipeline
- add reserve LinkedIn posts based on the external signal
- add specific technical differentiators to existing demo descriptions

## Verification
Before finishing:
1. Review the actual diff for all edited GTM docs.
2. Check counts/totals if a capability matrix changed (e.g. 15 -> 16 disciplines).
3. Make sure new messaging is additive and specific, not generic fluff.
4. Ensure each inserted idea ties to a concrete ACE service/capability.

## Pitfalls
- Do not stop at "summary of the post"; convert it into GTM artifacts.
- Do not rely only on text when the post’s visual is the differentiator; use vision.
- When adding a new capability like FOWT, update downstream counts and gap sections too.
- If a post exposes a modeling nuance (e.g. segmented loading), add it to the relevant demo/capability description rather than burying it only in content ideas.

## Proven examples
This pattern worked for:
- subsea/ROV execution posts -> engineering-led execution GTM positioning
- ship shear-force/bending-moment explainer posts -> engineer-grade explainers with technical-visual rigor
- FOWT lessons-transfer posts -> explicit FOWT capability packaging and O&G-to-renewables messaging
- lifting segmentation posts -> installation-analysis detail around hydrodynamic segmentation and trustworthy weather limits
