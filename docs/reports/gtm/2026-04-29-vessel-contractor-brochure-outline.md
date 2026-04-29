# Vessel-Contractor Brochure — Outline

> **Issue:** #2556 (brochure assembly + send tracker)
> **Sibling issues:** #2554 (contractor matrix), #2555 (capability charts), #1669 (parent campaign)
> **Status:** outline (planning artifact). The brochure-as-source Markdown lands at `docs/strategy/gtm/vessel-installation-contractors/brochure-source.md` after `status:plan-approved`.
> **Authoritative inputs:** `docs/gtm/capability-summary.md`, `docs/gtm/email-outreach-templates.md`, `docs/strategy/engineering-chatbot-oilgas-pitch.md`, `docs/gtm/prospect-demo-sop.md`.
> **Date:** 2026-04-29

---

## 1. Purpose

A 3–4 page brochure that a senior engineer at a vessel installation contractor can scan in under 60 seconds and decide whether to take a 20-minute walkthrough call. Tone matches `email-outreach-templates.md`: senior engineer to senior engineer; technical; zero marketing fluff.

This is **the** brochure shipped as a link (not attachment) inside cold-email Template 1 / 4 / 7 from the existing template library. PDF is generated for prospects who explicitly ask for an offline copy.

## 2. Page-by-page section map

| Page | Section | Content origin | Length budget |
|---|---|---|---|
| 1 | Cover + value proposition | Adapted from `capability-summary.md` lead | ≤ 70 words |
| 1 | Proof point — overnight scale | `capability-summary.md` proof block | 1 line |
| 2 | What we do (capability matrix) | `capability-summary.md` items 1–7 | 7-row table |
| 2 | Capability charts (3 slots from #2555) | Sibling issue #2555 outputs | 3 chart slots |
| 3 | Proof points — case counts | `digitalmodel/examples/demos/gtm/` demos 1–5 | 1 table |
| 3 | Engagement tiers + pricing | `capability-summary.md` "How We Work" | 1 table |
| 4 | CTA block | Custom (per template tier) | ≤ 60 words |
| 4 | Standards + software credentials | `capability-summary.md` "Standards" + "Software" | 2 short lines |
| 4 | Footer (P.E. + contact + URL) | `capability-summary.md` final line | 1 line |

Total: 4 pages, ≤ 1,200 words, ≥ 3 charts, ≤ 1 logo (ACE Engineer mark only — no client logos).

## 3. Section content specifications

### 3.1 Cover + value proposition

- One headline (no more than 12 words). Working draft: *"Parametric installation engineering for vessel contractors — overnight scale, P.E.-stamped."*
- Subhead names the audience explicitly: *"For vessel installation, pipelay, and heavy-lift contractors."*
- Below: a single proof line lifted verbatim from `capability-summary.md` ("1,292 parametric engineering cases screened overnight…").
- Cover carries no contact details beyond `info@aceengineer.com` and `aceengineer.com`. No phone number on the cover. Phone numbers live only in the email-template Send footer or the gated-URL HTML, never on the public PDF.

### 3.2 What we do — capability matrix

Lift the table from `capability-summary.md` lines 9–17 verbatim, with the standards reference in column 2 retained (DNV-RP-H103, DNV-ST-F101, DNV-RP-F105, API RP 2SK, API 579, DNV-RP-B401). Each row stays one line; do not expand into prose.

### 3.3 Capability charts (3 slots, sourced from #2555)

The brochure embeds **three** chart slots. The brochure outline does not specify chart content — that is #2555's deliverable. The slot contract is:

| Slot | Working title | Source | Provenance / caption requirement |
|---|---|---|---|
| Chart A | Vessel-class capability envelope (water depth × payload) | #2555 | Caption must cite public RAO/spec source or explicit "class-typical, not vessel-specific" disclaimer per `prospect-demo-sop.md` §5 |
| Chart B | Parametric screening turnaround (manual vs automated) | #2555 (or #2016 demos) | Caption cites per-demo case counts from `digitalmodel/examples/demos/gtm/` |
| Chart C | Operability window — seastate × splash-zone slamming | #2555 | Caption cites the methodology note in `docs/gtm/installation-analysis-method-note.md` |

Each chart in the brochure source uses a labelled placeholder (`{{CHART_A}}`, `{{CHART_B}}`, `{{CHART_C}}`); the Markdown→PDF render replaces with PNG/SVG output from #2555. If a slot is empty at brochure-render time, the build fails — **do not** ship a brochure with placeholder text in a public-facing surface.

### 3.4 Proof points — case counts

A 5-row table that matches `docs/strategy/gtm/vessel-installation-contractors/` to demo IDs:

| Study | Cases | Source |
|---|---|---|
| Demo 1 — freespan / VIV | 680 | `digitalmodel/examples/demos/gtm/demo_01` |
| Demo 2 — wall thickness comparison (API/DNV/PD8010) | 72 | `digitalmodel/examples/demos/gtm/demo_02` |
| Demo 3 — mudmat installation screening | 180 | `digitalmodel/examples/demos/gtm/demo_03` |
| Demo 4 — shallow-water pipelay screening | 60 | `digitalmodel/examples/demos/gtm/demo_04` |
| Demo 5 — rigid jumper installation | 300 | `digitalmodel/examples/demos/gtm/demo_05` |

Total of these = 1,292, matching the `capability-summary.md` proof line. Reviewers can verify the case counts directly against the referenced demo directories.

### 3.5 Engagement tiers + pricing

Lift verbatim from `capability-summary.md` "How We Work":

| Tier | Scope | Timeline & price |
|---|---|---|
| Screening | Parametric analysis, go/no-go report | 48 hours, $5K–15K |
| Detailed | OrcaFlex/FEA model, sensitivity studies | 2–4 weeks, $25K–75K |
| Operations | Real-time decision support | Ongoing, $10K/month |

Pricing must remain consistent with `email-outreach-templates.md` Template 4 ("Service Tier Reference") to avoid prospect-facing inconsistency.

### 3.6 CTA block

CTA varies by which email-template the brochure ships under:

- **Cold intro (Template 1)** — *"20-minute walkthrough using your fleet's data. Send vessel name + structure type + water-depth range; first screening turnaround is 48 hours."*
- **Warm-lead reply (Template 4)** — *"Send vessel name or class, structure type and weight range, and water-depth range. I'll queue the screening within 48 hours."*
- **Re-engage (Template 7)** — *"Latest demo: rigid jumper installation across 300 cases. Worth a 20-minute walkthrough?"*

Each CTA includes a single channel of response (reply-to-email or Calendly link), never both — to keep call-to-action unambiguous.

### 3.7 Standards + software credentials

One line each from `capability-summary.md`:
- *Standards: DNV | API | ASME | ISO | BS 7608*
- *Software: OrcaFlex | OrcaWave | ANSYS | Python/digitalmodel*

### 3.8 Footer

`info@aceengineer.com | aceengineer.com | Licensed P.E. — Houston, TX`

Match `capability-summary.md` line 43 verbatim. No personal phone number on the public brochure.

## 4. Outbound copy variants (per tier)

The send-tracker (issue #2556 deliverable) drives **which** template to use; the brochure is the artifact linked. Three baseline variants from `docs/gtm/email-outreach-templates.md`:

| Variant ID | Tier | Template (in `email-outreach-templates.md`) | Subject line slot | Hook focus |
|---|---|---|---|---|
| V1 | 1 — Major EPIC | Template 1 (cold intro) + Template 5A (LinkedIn note) | "180 vessel-structure combinations screened overnight — methodology note" | Fleet-wide automation + consistency |
| V2 | 2 — Specialist Vessel Ops | Template 1 (cold intro) + Template 5B (LinkedIn note) | "Parametric installation screening for [VESSEL_CLASS] operations" | Win tenders with faster, more defensible analysis |
| V3 | 3 — Regional/Niche | Template 1 (cold intro) + Template 5C (LinkedIn note) | "Reducing installation engineering turnaround from weeks to hours" | Senior capability without overhead of a full eng dept |

Each variant must include:
- Personalization hook from #2554 contractor matrix (column: `personalization_hook`).
- Brochure link (gated-URL or public PDF — per `prospect-demo-sop.md` gating rules).
- Reply-to email or Calendly slot — never both.
- No attachments on cold sends; PDF offered only after a positive reply (Template 4 path).

Subject line A/B test pool: pick from `email-outreach-templates.md` "Subject Line Library" rows 1–14. Track which subject won via the send tracker's `response_class` column.

## 5. Proof requirements (legal / evidence sanity)

Before any send, the brochure source must pass:

| Check | Source / contract |
|---|---|
| Every numerical claim cites a repo path or external public source | `BUSINESS_BRAIN.md` legal-sanity gates section |
| No client-identifying content | `BUSINESS_BRAIN.md` minimum public-promotion sanity gate |
| Methodology citations attached for each capability claim | `BUSINESS_BRAIN.md` |
| `scripts/legal/legal-sanity-scan.sh --diff-only` exits 0 on the brochure-source diff | Codified in plan TDD list |
| Standards references match the form used in `capability-summary.md` (e.g. DNV-RP-F105, not "DNV-RP-F105 (2017)") | Consistency-check against existing repo artifact |
| All chart captions name the chart's data source explicitly | `prospect-demo-sop.md` §5 (canonical-vessel disclaimer pattern) |

A brochure that fails any check **does not ship**, even if a send is otherwise queued.

## 6. CTA contract (sent vs. published surfaces)

| Surface | Carries CTA? | Carries phone? | Carries PDF? |
|---|---|---|---|
| Public PDF brochure | yes — single-channel | no | n/a (it IS the PDF) |
| Gated-URL HTML (per `prospect-demo-sop.md` `/private/<hash>/<slug>.html`) | yes — single-channel | optional | downloadable PDF link |
| Cold email body (Template 1) | yes — link to gated URL | text-form in template footer only | no |
| LinkedIn connection note (Template 5) | no — connection-only | no | no |

The brochure itself is one of the artifacts referenced by the email; it is not the email's substitute.

## 7. Open questions for plan-review

1. **Brochure format split:** PDF only, HTML only, or both? Default proposal: Markdown source → PDF (cold-email link target) + HTML (gated-URL surface). Decide at plan-review.
2. **Personalization-hook source of truth:** does the brochure carry a tier-specific page, or does the brochure stay generic and personalization happen exclusively in the email body? Default proposal: brochure is generic per tier; personalization stays in email. Less risk of leaking client-identifying content into the public PDF.
3. **Render toolchain:** `data:md-to-pdf` skill (Chrome headless) vs `pandoc` vs LaTeX. Default proposal: `data:md-to-pdf` because it already exists and matches existing reports surface.
4. **Inclusion of pricing on cover vs internal page:** existing `capability-summary.md` shows pricing in tier table. Carry over to brochure or move pricing to a "next-step" page only sent post-reply? Default proposal: keep pricing in brochure — matches current 1-pager and reduces back-and-forth.
5. **Distribution gate:** does send-tracker `send_state=SENT` require a human-initiated action, or can a scheduled job execute approved batches? Default proposal: human-initiated only at the first batch; revisit after first batch metrics.

## 8. Cross-references

- Sibling deliverable that supplies chart slots: #2555 (`feat(gtm): vessel capability charts for contractor brochure`).
- Sibling deliverable that supplies the contractor matrix and personalization hooks: #2554 (`feat(gtm): weekly vessel contractor outreach matrix for April target`).
- Parent campaign: #1669.
- Conversion umbrella: #2016.
- Operational delivery infrastructure (re-used patterns, **not** re-implemented here): `docs/gtm/prospect-demo-sop.md` and `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md`.
- Send-tracker schema (companion document): `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md`.

## 9. Out of scope (this outline)

- Authoring chart content (#2555).
- Compiling the contractor list and personalization hooks (#2554).
- Building a PII-resolver service or contact-CRM integration (future issue).
- Implementing a send-execution worker or cron (future issue; gated by user authorization per `BUSINESS_BRAIN.md`).
- Reply-classification ML or auto-reply drafting (future issue).
