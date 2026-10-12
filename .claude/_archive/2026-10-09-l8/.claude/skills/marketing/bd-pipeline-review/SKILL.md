---
name: bd-pipeline-review
description: Run the weekly marketing/BD review that turns activity into tracked, advancing
  opportunities. Pull a funnel snapshot against the KPI spine, enforce pipeline hygiene,
  focus on priority + at-risk deals, and end with written, owned action items. Guards against
  vanity metrics and leads falling through the cracks.
version: 1.0.0
category: marketing
applies-to:
- hermes
- claude
- codex
- gemini
trigger: weekly
auto_execute: false
tags:
- marketing
- pipeline
- review
- kpi
- metrics
- bd
- cadence
---

# BD Pipeline Review

The **REVIEW** stage of the marketing operating system (see [`../INDEX.md`](../INDEX.md)).
The weekly loop that keeps the whole engine honest and advancing.

## Use when
It's the weekly review, or the user asks to "review the pipeline", "check marketing/BD
metrics", "update the dashboard", or "see what's moving / stalled".

## Goal
A short, fixed-cadence review that converts activity into **advancing opportunities** — every
open item has an owner and a next step, and reporting is tied to pipeline outcomes, not likes.

## Inputs to gather
1. The funnel snapshot for the period (from
   [`linkedin-funnel-ops`](../linkedin-funnel-ops/SKILL.md) +
   [`targeted-outreach-sequence`](../targeted-outreach-sequence/SKILL.md)).
2. The KPI targets from [`marketing-campaign-plan`](../marketing-campaign-plan/SKILL.md) and
   the [shared KPI spine](../_shared/kpi-spine.md).
3. The open-opportunity list with stage + last activity + next step.

## Method
1. **Snapshot the funnel** against the KPI spine: awareness → engagement → followers →
   conversations → qualified → registrations/RFQs → won. One primary metric per stage.
2. **Hygiene gate first**: flag empty fields, stale stages, and any open item with no next
   step or a vague one. Clean before you analyze — a review off dirty data is theatre.
3. **Focus on the few**: the 3–5 priority deals + everything at-risk/stalled, not the whole
   list.
4. **Decide + assign**: for each, the next action, owner, and date — written down.
5. **Report outcomes, not vanity**: lead with conversations, qualified leads, registrations,
   RFQs, won work; show follower/impression trends only as leading indicators.
6. **Close the loop**: confirm last week's action items were done; carry forward what wasn't.
7. Keep it ≤30 minutes on a fixed day.

## Output
An updated dashboard/metrics table (emails · replies · followers · conversations ·
registrations · RFQs · won) + a written action list (item · owner · date). Store in the
engagement's BD folder; surface a one-screen momentum view for management.

## Definition of done
- [ ] Funnel snapshot against the KPI spine.
- [ ] Hygiene pass done (no stale stages / missing next steps).
- [ ] Priority + at-risk deals reviewed.
- [ ] Written, owned, dated action items.
- [ ] Last week's actions closed-looped.
- [ ] Outcomes (not vanity metrics) lead the report.

## Guardrails / pitfalls
- **Vanity metrics** as headline = the cardinal sin; tie everything to pipeline.
- **Dirty CRM** makes the review useless — hygiene is step 2, before analysis.
- **Reviewing the whole list** wastes the meeting; review the few that matter.
- **No close-loop** — unverified action items quietly die.

## Related skills
Closes the loop on [`marketing-campaign-plan`](../marketing-campaign-plan/SKILL.md);
consumes output from [`linkedin-funnel-ops`](../linkedin-funnel-ops/SKILL.md) and
[`targeted-outreach-sequence`](../targeted-outreach-sequence/SKILL.md). KPI definitions in
[`../_shared/kpi-spine.md`](../_shared/kpi-spine.md).
