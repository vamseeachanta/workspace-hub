---
name: linkedin-funnel-ops
description: Run the LinkedIn organic funnel — reactions/likes → page follows → engaged
  followers → conversations. Covers the concrete platform levers (invite-to-follow, the
  Premium-page auto-invite of reactors, comment-gating, newsletters, page CTA buttons,
  personal-profile reach) and the compliant ways to pull contact data. Converts engagement
  into tracked conversations, not vanity metrics.
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
- linkedin
- funnel
- followers
- engagement
- lead-gen
- social
---

# LinkedIn Funnel Ops

The **REACH** stage of the marketing operating system (see [`../INDEX.md`](../INDEX.md)).
Operates the likes → follow → follower → conversation funnel on LinkedIn.

## Use when
The user asks to "grow LinkedIn", "convert likes to followers", "turn followers into leads",
"run the LinkedIn page", or wants the operational mechanics behind the campaign's reach goal.

## Goal
Systematically walk each reaction down the funnel using LinkedIn's actual levers, and log
every conversation — so engagement becomes pipeline, not a follower vanity count.

## The levers (what actually moves each transition)
**Like/comment → follow (the key lever):**
- **Premium company page** auto-invites everyone who reacted to/commented on a post in the
  last ~30 days to follow — **free, no credit cost.** This is the single highest-leverage
  mechanic for "convert likes to follows" and the main reason to upgrade the page.
- **Free company page**: admins can only *Invite connections* (1st-degree), capped at a small
  monthly credit pool; credits return when an invite is accepted.
- **Comment-gate** posts ("comment WORD and I'll send it") — boosts reach and builds a list
  of warm hands to invite/DM.
- Verify current limits/credits in the page admin view before promising volume.

**Follow → engaged follower:**
- Launch a **LinkedIn newsletter** (eligible past a small follower threshold) — each edition
  pushes an email + in-app notification to subscribers.
- Set the **page CTA button** to *Request services* / *Contact us*.
- Keep a consistent proof cadence (handled by [`content-calendar`](../content-calendar/SKILL.md)).

**Engaged follower → conversation:**
- Deliver a lead magnet by **DM**, capture the email, then book the call.
- Add an **organic Lead-Gen Form** on the page for "send me the capability pack."
- Mine commenters + profile-viewers into [`targeted-outreach-sequence`](../targeted-outreach-sequence/SKILL.md).

**Reach amplifiers:** personal profiles typically out-reach the company page — post from
founders/SMEs and have employees reshare in the first ~60 minutes.

## Getting contact data (compliant only)
- **Native "Get a copy of your data"** → connections CSV (name, company, position, profile
  URL, connect date; email only if the contact shared it; 1st-degree, no phones).
- **Sales Navigator** lead/account lists + CRM sync.
- **Company-page analytics** for follower/visitor demographics.
- **Never scrape.** It breaches LinkedIn's terms and carries real legal/account risk; use the
  native exports and consented opt-ins (lead-magnet DMs) instead.

## Method
1. Confirm page tier + current invite-credit balance.
2. Publish per the calendar; engage back in the first hour.
3. Run the follow-conversion lever appropriate to the page tier (Premium auto-invite or
   connection invites + comment-gate).
4. Move engaged followers toward a newsletter sub and a conversation.
5. **Log every conversation/DM/form-fill** into the pipeline tracker — that's the real KPI.

## Definition of done
- [ ] Follow-conversion lever running (and the page-tier decision made/surfaced).
- [ ] Newsletter + CTA button live; lead magnet + capture path defined.
- [ ] Contact data sourced only via compliant exports.
- [ ] Conversations logged to the pipeline, not just follower counts.

## Guardrails / pitfalls
- **Vanity metrics**: followers/likes are leading indicators; report conversations + SQLs.
- **No scraping / no mass blind DMs** — targeted, consented, tracked.
- **One ask per touch.**
- **Public/PII hygiene** in anything posted publicly.

## Related skills
Distributes [`content-calendar`](../content-calendar/SKILL.md) output; feeds
[`targeted-outreach-sequence`](../targeted-outreach-sequence/SKILL.md); reports into
[`bd-pipeline-review`](../bd-pipeline-review/SKILL.md). KPI definitions in
[`../_shared/kpi-spine.md`](../_shared/kpi-spine.md).

> Platform limits/feature availability (credit caps, Premium features, newsletter
> thresholds) change — verify in-product before committing to specific numbers.
