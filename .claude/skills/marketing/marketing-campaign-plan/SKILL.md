---
name: marketing-campaign-plan
description: Turn a marketing/BD objective into a measurable, time-boxed campaign plan
  with ICP, message + proof, channel mix, asset list, a conversion funnel + flowchart,
  KPI targets with a named tracking mechanism, and an owner/RACI. The spine the other
  marketing skills execute against.
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
- campaign
- gtm
- strategy
- funnel
- planning
- b2b
---

# Marketing Campaign Plan

The **PLAN** stage of the marketing operating system (see [`../INDEX.md`](../INDEX.md)).
Every other marketing skill executes against the plan this skill produces.

## Use when
The user asks to "plan a campaign", "build a marketing/GTM plan", "maximize outreach",
"put together a LinkedIn/BD plan", or wants a strategy doc for a launch, season, service
line, or client engagement.

## Goal
Convert a fuzzy objective ("get more work", "more visibility") into **one measurable,
time-boxed plan** with a funnel, hooks, owners, KPI targets, and a named tracking
mechanism — not a list of tactics.

## Inputs to gather (ask if missing; pick sensible defaults and state them)
1. **Objective** — tied to a pipeline outcome (RFQs / registrations / qualified
   conversations / won work), not "awareness".
2. **ICP / segments** — who exactly (industry, role/seniority, geography, warm vs cold).
3. **Proof shelf** — case studies, past performance, credentials, metrics, work samples.
4. **Channels available** — company page, personal profiles, email, events, directories.
5. **Constraints** — time/budget, brand/voice, what must stay private (client PII),
   approval owner.
6. **Time box** — start/end. Warm campaigns 7–10 business days; cold outbound 14–21.

## Method
1. **Lock one objective** and its single primary KPI (the outcome metric).
2. **Name the ICP/segments** and rank them **warm-first** (relationships convert fastest).
3. **Write the core message** = credibility line → 1–3 relevant proof points → one clear ask.
4. **Pick the channel mix** and assign each channel a job in the funnel (reach vs convert).
5. **List the assets** each channel needs (posts, one-pagers, sequences) → hand off to
   the PRODUCE skills ([`content-calendar`](../content-calendar/SKILL.md),
   [`capability-collateral`](../capability-collateral/SKILL.md)).
6. **Draw the conversion funnel** with an explicit **hook at every stage transition**
   (reach → engagement → audience → conversation → qualify → outcome). The hook is the
   action that pulls a person to the next stage; nothing is left to chance. Render it as a
   simple flowchart (left = stage, right = hook). See
   [`references/funnel-and-hooks.md`](references/funnel-and-hooks.md).
7. **Set KPI targets per funnel stage AND name the tracking mechanism** for each (where
   the number is recorded and who updates it). Use the
   [shared KPI spine](../_shared/kpi-spine.md). A target without a tracking mechanism is
   not done.
8. **Assign RACI** — one Accountable owner, Responsible doers, Consulted (legal/SME),
   Informed. Route approvals to the Accountable owner.
9. **Schedule** the 30/60/90 (or campaign-length) cadence and the review loop
   ([`bd-pipeline-review`](../bd-pipeline-review/SKILL.md)).

## Output
A single plan document (Markdown, or HTML→PDF via
[`capability-collateral`](../capability-collateral/SKILL.md) when it's for management).
Structure: short summary on page 1; detail + funnel flowchart on following pages; a
"decisions we need" table at the end. Store in the engagement's marketing strategy folder.

## Definition of done
- [ ] Exactly one objective, tied to a pipeline outcome.
- [ ] Named ICP/segments, ranked warm-first.
- [ ] Core message with ≥1 concrete proof point.
- [ ] Channel mix with a funnel job per channel + an asset list.
- [ ] Funnel with a deliberate hook at every transition (flowchart included).
- [ ] KPI target **and** tracking mechanism per stage.
- [ ] One Accountable owner; approvals routed to them.
- [ ] Defined start/end and a review cadence.

## Guardrails / pitfalls
- **No vanity objectives.** "Awareness/followers" is a leading indicator, never the goal.
- **Warm-first, not spray.** Cold mass-targeting goes to a slow background track.
- **Public-repo / client-PII hygiene.** Keep client names, contacts, and figures out of any
  shared/public surface; real contact data lives in the private engagement repo only.
- **Honest posture.** Don't imply active projects, vendor status, or bids that don't exist.
- **One ask per touch.** Multiple asks halve response.

## Related skills
Inputs from [`linkedin-post-to-gtm-ingestion`](../linkedin-post-to-gtm-ingestion/SKILL.md)
(market signals). Feeds [`content-calendar`](../content-calendar/SKILL.md),
[`capability-collateral`](../capability-collateral/SKILL.md),
[`linkedin-funnel-ops`](../linkedin-funnel-ops/SKILL.md),
[`targeted-outreach-sequence`](../targeted-outreach-sequence/SKILL.md). Reviewed by
[`bd-pipeline-review`](../bd-pipeline-review/SKILL.md).
