---
name: content-calendar
description: Produce a planned, on-voice content pipeline from a few content pillars —
  map each piece to a funnel stage + persona, atomize one core asset into many derivatives,
  schedule with owner/status, attach a distribution plan, and pass a quality gate. Built
  for steady B2B technical-content cadence (incl. data-backed seasonal series).
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
- content
- calendar
- linkedin
- cadence
- distribution
- b2b
---

# Content Calendar

The **PRODUCE** stage of the marketing operating system (see [`../INDEX.md`](../INDEX.md)).
Turns the campaign plan's message into a repeatable, on-voice content pipeline.

## Use when
The user asks to "build a content calendar", "plan posts", "set a posting cadence",
"create a seasonal/data-backed series", or wants a steady stream of LinkedIn/newsletter
content tied to the campaign.

## Goal
A scheduled pipeline where **every item maps to a pillar + persona + funnel stage**, a core
asset is repurposed into many derivatives, and each piece ships with a distribution plan —
not a backlog of orphan post ideas.

## Inputs to gather
1. The campaign plan (objective, ICP, message) from
   [`marketing-campaign-plan`](../marketing-campaign-plan/SKILL.md).
2. **Content pillars** — 3–6 recurring buyer problems the firm is credible on.
3. Voice/brand notes and any approved-claims library (see
   [`../_shared/claims-library.md`](../_shared/claims-library.md)).
4. Source material for data-backed pieces (datasets, incident stats, standards, case data).
5. Cadence + channels (page, personal profiles, newsletter), and the publish owner.

## Method
1. **Set 3–6 pillars**, each tied to a buyer problem and a service line.
2. **Pick formats by performance**: document/carousel PDFs and polls reach + dwell highest;
   native video next; plain text/image lowest; avoid external links in-post (put the link
   in a comment or the page CTA).
3. **Atomize**: take one core asset (a study, a calculator, a case) and derive several
   posts, a carousel, a poll, a newsletter edition.
4. **Map every row** to pillar + persona + funnel stage so the calendar serves the funnel,
   not just the feed.
5. **Schedule** with owner + status. Cadence: ~2–5 posts/week across page + personal
   profiles; best windows midweek mornings local; the first ~60 minutes drive reach.
6. **Attach a distribution plan per piece** (who reshares, employee advocacy, newsletter
   push, comment-seeding). Plan roughly as much effort for distribution as creation.
7. **Quality gate** before queueing (below).
8. For **data-backed series**: cite the dataset, keep claims defensible, use a consistent
   visual/format, and stamp the data vintage.

## Output
A calendar (table: date · pillar · persona · funnel stage · format · hook · owner · status ·
distribution) plus drafted/queued items. Store in the engagement's content folder.

## Definition of done
- [ ] Every item maps to pillar + persona + funnel stage.
- [ ] ≥1 core asset repurposed into several derivatives.
- [ ] Format chosen for reach/dwell, not habit.
- [ ] Distribution plan per piece (not just a publish date).
- [ ] Voice/brand + accuracy check passed; data-backed claims cited + vintage-stamped.
- [ ] Owner + status visible for every row.

## Guardrails / pitfalls
- **Create-but-don't-distribute** is the #1 waste — distribution is part of done.
- **Cadence drift** kills compounding; protect the rhythm even when posts are short.
- **Voice drift** — run every piece against the voice + claims library.
- **No vanity-only pieces** — each item should move someone toward a conversation.
- **Public/PII hygiene** — no client names/figures in public content without clearance.

## Related skills
Fed by [`marketing-campaign-plan`](../marketing-campaign-plan/SKILL.md) and
[`linkedin-post-to-gtm-ingestion`](../linkedin-post-to-gtm-ingestion/SKILL.md). Distributed
through [`linkedin-funnel-ops`](../linkedin-funnel-ops/SKILL.md). Heavy assets are built by
[`capability-collateral`](../capability-collateral/SKILL.md).
