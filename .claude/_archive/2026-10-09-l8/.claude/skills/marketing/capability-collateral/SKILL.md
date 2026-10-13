---
name: capability-collateral
description: Produce and refresh branded, single-page capability one-pagers, pamphlets, and
  management decks/plans — brief → who/what/why-us + concrete proof → segment tailoring →
  brand/voice + claims check → clean layout → render HTML to PDF. Reuses an approved-claims
  library so claims are written once and reused (incl. proposal/expert-witness support).
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
- collateral
- one-pager
- pamphlet
- pdf
- branding
- proposal
---

# Capability Collateral

The **PRODUCE** stage of the marketing operating system (see [`../INDEX.md`](../INDEX.md)).
Turns the campaign message + proof into sendable, branded assets.

## Use when
The user asks for a "one-pager", "capability statement", "pamphlet/brochure", "leave-behind",
"work-sample sheet", or a "PDF for management/clients", or to refresh existing collateral.

## Goal
A **single-page (or tight multi-page), on-brand asset** that says who/what/why-us with
concrete proof, tailored to its audience, and rendered to a clean PDF — reusing pre-cleared
claims rather than re-writing them.

## Inputs to gather
1. **Brief**: audience/segment, use-context (cold intro vs live pursuit), the win-theme.
2. **Proof**: past performance, metrics, credentials, testimonials, work samples — pulled
   from [`../_shared/claims-library.md`](../_shared/claims-library.md) where possible.
3. Brand assets: logo, palette, contact block, voice.
4. Output format: web page, print PDF, or both.

## Method
1. **Write the brief** (one paragraph): who it's for, where it's used, the single win-theme.
2. **Draft the spine**: headline → who we are (credibility line) → what we do (scoped) →
   why us (differentiators + proof) → one clear CTA.
3. **Pull proof from the claims library**; if a claim isn't cleared, flag it — don't invent
   numbers or imply work/relationships that don't exist.
4. **Tailor to the segment** (operators vs EPCs vs legal/insurance vs renewables) — a general
   version plus a targeted variant for live pursuits.
5. **Lay out** in the house style: keep page 1 short/scannable; detail on following pages;
   use cards, a hooks/funnel diagram, or a comparison table where it earns its space.
6. **Brand + voice + accuracy check.**
7. **Render to PDF** via headless Chrome — see
   [`references/html-to-pdf.md`](references/html-to-pdf.md).
8. **Version + store** in the collateral library; provide a clickable link to the PDF.

## Output
HTML source + rendered PDF (and any QR/links). Store both in the engagement's collateral
folder; keep the HTML so it can be re-rendered and versioned.

## Definition of done
- [ ] Single clear audience + win-theme.
- [ ] Who/what/why-us + ≥1 concrete, cleared proof point.
- [ ] Segment-tailored (general + targeted variant where there's a live pursuit).
- [ ] On-brand; voice + accuracy checked.
- [ ] Clean PDF rendered; page 1 scannable.
- [ ] Versioned in the library; claims sourced from the claims library.

## Guardrails / pitfalls
- **No invented or uncleared claims** — opposing counsel and procurement both check.
  Especially for the expert-witness lane, keep CV/profile/collateral identical + verifiable.
- **PII / public hygiene** — sanitize before any public or external surface; real client
  detail stays in the private engagement repo.
- **Don't bury the ask** — one CTA, prominent.
- **Reuse, don't re-write** — feed and pull from the claims library.

## Related skills
Fed by [`marketing-campaign-plan`](../marketing-campaign-plan/SKILL.md) (message/proof) and
[`content-calendar`](../content-calendar/SKILL.md) (asset list). Used by
[`targeted-outreach-sequence`](../targeted-outreach-sequence/SKILL.md) as the attachment.
