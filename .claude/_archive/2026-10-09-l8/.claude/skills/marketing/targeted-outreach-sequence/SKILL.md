---
name: targeted-outreach-sequence
description: Build warm-first, ICP-matched outreach sequences that book conversations and
  drive vendor/supplier registrations and RFQs. Validate the list against the ICP, research
  a real trigger per contact, run a multi-touch multi-channel cadence with reply branching,
  and guarantee no contact exits without a logged next step. Honest, tracked, relationship-aware.
version: 1.0.0
category: marketing
applies-to:
- hermes
- claude
- codex
- gemini
trigger: manual
auto_execute: false
tags:
- marketing
- outreach
- sales
- bd
- cadence
- vendor-registration
- pipeline
---

# Targeted Outreach Sequence

The **CONVERT** stage of the marketing operating system (see [`../INDEX.md`](../INDEX.md)).
Turns warmed audiences and target lists into booked conversations and registrations.

## Use when
The user asks to "do outreach", "build an outreach sequence/cadence", "reach out to
[segment]", "get on supplier/vendor lists", "reactivate dormant clients", or "draft warm
intros".

## Goal
A repeatable engine where each owner works the targets they can actually win, every touch
carries credibility + a relevant proof point + one clear ask, and every contact has a logged
next step — converting to **vendor registrations · RFQs · qualified conversations · won work**.

## Inputs to gather
1. The campaign plan + ICP from [`marketing-campaign-plan`](../marketing-campaign-plan/SKILL.md).
2. **Target list** with warm/cold flag and the owner who has the relationship.
3. Per-target **trigger/relevance** (shared history, a live project, a portal, a referral path).
4. The matching **collateral** from [`capability-collateral`](../capability-collateral/SKILL.md).
5. Where contacts/replies get logged (the pipeline tracker / per-target threads).

## Method
1. **ICP-gate the list** — every contact matches the profile; quality beats size. Drop or
   demote misfits to a slow background track.
2. **Rank warm-first** and split into owner **lanes** (e.g. an engineering lane and a
   legal/relationship lane) — different audiences, run in parallel.
3. **Research a real trigger per contact** — personalization tied to something true, not
   generic flattery.
4. **Draft each touch** to the rule: *credibility line → 1–3 relevant proof points → one
   clear ask.* Lead warm contacts with the note, not the brochure.
5. **Sequence the cadence**: multi-touch (≈7–13 over a few weeks), multi-channel (email +
   LinkedIn + call), front-loaded in the first few days; define **reply branches** (interested
   / not now / wrong person / no reply) and objection handling.
6. **Honest posture** for cold/registration outreach: no implied active project or vendor
   status; ask for the correct supplier-registration / category-routing contact; copy the
   relationship owner once the route is verified.
7. **Vendor/supplier registration path**: maintain a portal inventory (open / invite / TBD),
   reuse a standard answers/claims library, record credentials + renewal dates, and route any
   resulting RFQ straight into the pipeline.
8. **Log every send/reply** and the next step. **No contact exits the sequence without a
   logged next step or a disposition.**

## Output
An outreach pack: per-target rows (owner · lane · trigger · touch · sent · reply · next step)
+ ready-to-send drafts with `[brackets]` to fill. Keep real names/contacts in the **private**
engagement repo; templates stay PII-free.

## Definition of done
- [ ] 100% of contacts match the ICP.
- [ ] Warm-first, split into owner lanes.
- [ ] A real trigger + one clear ask per touch.
- [ ] Multi-touch, multi-channel cadence with reply branches defined.
- [ ] Honest posture; registration routing + renewal tracking where relevant.
- [ ] Every contact logged with a next step; nothing falls through.

## Guardrails / pitfalls
- **Spray-and-pray** — off-ICP blasts burn the brand; gate the list.
- **No follow-up** — the fortune is in touches 2–7; never single-touch-and-drop.
- **No tracking** — unlogged outreach can't be reviewed or improved.
- **Mis-aimed lanes** — point each owner at the network they can actually win, not at cold
  names someone else owns.
- **Honesty/compliance** — never imply work/vendor status that doesn't exist; respect
  confidentiality for any legal/expert-witness lane.

## Related skills
Fed by [`marketing-campaign-plan`](../marketing-campaign-plan/SKILL.md),
[`capability-collateral`](../capability-collateral/SKILL.md), and warm leads from
[`linkedin-funnel-ops`](../linkedin-funnel-ops/SKILL.md). Reviewed weekly by
[`bd-pipeline-review`](../bd-pipeline-review/SKILL.md).
