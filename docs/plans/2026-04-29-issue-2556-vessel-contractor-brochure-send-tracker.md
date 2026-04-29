# Plan for #2556: Vessel-Contractor Brochure and Outbound Send Tracker

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2556
> **Review artifacts:** `scripts/review/results/2026-04-29-plan-2556-claude.md` | `...-codex.md` | `...-gemini.md` (none yet — adversarial review pending)

---

## Resource Intelligence Summary

This is a GTM/business issue (`cat:business`, `cat:strategy`, `domain:gtm`); the universal-minimum bundle plus prior GTM artifacts apply. No engineering-calculation or document-intelligence retrieval is required.

### Existing repo code

This issue produces collateral artifacts and a tracker schema; no library code is added.

- Found: `docs/gtm/capability-summary.md` — current ACE Engineer 1-page capability summary (43 lines, last touched 2026-04-22). Good brochure precursor; needs expansion to a multi-page brochure with capability charts and proof slots.
- Found: `docs/gtm/capability-summary.pdf` (315 KB, 2026-04-20) — historical PDF; provenance/regeneration path TBD.
- Found: `docs/gtm/email-outreach-templates.md` (7 templates for vessel-installation contractors; tier strategy already encoded). Direct input for the send-tracker outbound copy variants.
- Found: `docs/gtm/prospect-demo-sop.md` — the 48-hour prospect-demo runbook (#2346). Provides the dual-delivery state machine, gated-URL mechanics, and `deliveries-log.md` row schema that the send tracker should align with.
- Found: `docs/gtm/deliveries-log.md` (44 lines, 2026-04-23) — existing delivery ledger; the new send tracker layers above this for *outbound* sends, not inbound prospect demos.
- Found: `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (1,300+ lines) — recent overnight-generated outreach candidate briefs. Source of personalization hooks per contractor.
- Found: `docs/gtm/overnight-client-ready-material-2026-04-28.md` — overnight-generated client-ready content; candidate brochure source material.
- Found: `docs/strategy/engineering-chatbot-oilgas-pitch.md` — the AI-engineering pitch that frames Tier 1/2 brochure messaging.
- Found: `docs/gtm/gtm-plan-30day.md` — 30-day GTM plan; brochure-send is one channel within it.
- Gap: `docs/strategy/gtm/vessel-installation-contractors/` directory is empty. The campaign README/prospect-list/value-proposition deliverables called for in #1669 do not exist yet.
- Gap: No outbound send tracker exists today; only the inbound `deliveries-log.md`.
- Gap: No brochure-as-source artifact (Markdown or HTML) exists; only the 1-page summary and a stale PDF.

### Standards

Not applicable — GTM/business issue. Engineering claims surfaced in the brochure must cite their existing evidence sources (DNV/API standards already referenced in `capability-summary.md`).

### LLM Wiki pages consulted

Not applicable to this issue — wiki content is consumed downstream when chart claims (#2555) or methodology claims need provenance, not at brochure-assembly stage. The legal-sanity gate still runs before publication.

### Documents consulted

- `docs/BUSINESS_BRAIN.md` — confirms current weekly target ("for the week of April 1, produce vessel capability charts and send a good brochure to all researched vessel contractors"); legal-sanity gates section enumerates the public-promotion checklist this brochure must pass.
- Issue #2556 body — scope, deliverables, acceptance criteria.
- Issue #2554 body — sibling research/matrix work; brochure consumes its output (target list + tier).
- Issue #2555 body — sibling capability-charts work; brochure embeds its outputs.
- Issue #1669 body — parent campaign; defines tier strategy, prospect-list/value-prop/templates structure, and email-sequence cadence (Day 0/3/7/14/30).
- Issue #2016 body — GTM conversion umbrella; #1669 is the outreach lever, demo materials are the show-don't-tell levers (Tier 1).
- `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` (referenced via SOP) — defines `state` enum, retry budget, and gated-URL mechanics that the send tracker mirrors for symmetry.

### Gaps identified

What this plan must produce that does not exist yet:

1. A canonical brochure-as-source artifact (Markdown + a build path to PDF).
2. A canonical brochure outline document with section/chart/proof slots, CTA contract, and outbound copy variants per tier.
3. A public send-tracker schema (no PII) plus a gitignored private-companion schema for the contact-detail fields.
4. A first-batch ready-to-send list shape (rows reference contractor IDs assigned by #2554; no contact details in the public artifact).
5. A legal-sanity gate hookup mirroring `BUSINESS_BRAIN.md` minimum requirements before any send executes.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29 via `gh issue view`):
- `#2556` — OPEN — feat(gtm): vessel contractor brochure and outbound send tracker — labels: `priority:high`, `cat:business`, `cat:strategy`, `domain:gtm`.
- `#2554` — OPEN — feat(gtm): weekly vessel contractor outreach matrix for April target.
- `#2555` — OPEN — feat(gtm): vessel capability charts for contractor brochure.
- `#1669` — OPEN — [WRK] GTM: Vessel Installation Contractor Email Outreach Campaign.
- `#2016` — OPEN — feat(gtm): client conversion pipeline -- turn repo capability into paying clients.

**File existence** (`ls -la` 2026-04-29):
- EXISTS: `docs/gtm/capability-summary.md` (43 lines)
- EXISTS: `docs/gtm/capability-summary.pdf` (315 KB)
- EXISTS: `docs/gtm/email-outreach-templates.md` (244 lines, 7 templates)
- EXISTS: `docs/gtm/prospect-demo-sop.md` (314 lines)
- EXISTS: `docs/gtm/deliveries-log.md` (44 lines)
- EXISTS: `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (49,249 bytes)
- EXISTS: `docs/strategy/engineering-chatbot-oilgas-pitch.md`
- EXISTS: `docs/strategy/gtm/vessel-installation-contractors/` (directory; empty)
- MISSING (this plan creates): `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`
- MISSING (this plan creates): `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md`
- MISSING (this plan creates, downstream of approval): `docs/strategy/gtm/vessel-installation-contractors/brochure-source.md`
- MISSING (this plan creates, downstream of approval): `docs/gtm/intake/send-tracker.public.yaml`
- MISSING (gitignored, NEVER tracked): `docs/gtm/intake/send-tracker.private.yaml`

**Gap proofs:**
- `ls /mnt/local-analysis/workspace-hub/docs/strategy/gtm/vessel-installation-contractors/` returns empty (no `README.md`, no `prospect-list.md`, no `value-proposition.md`, no `email-templates.md`, no `capability-summary.md`) — confirms #1669 Phase 1 deliverables are not yet present at the canonical campaign location.
- `ls /mnt/local-analysis/workspace-hub/docs/reports/gtm/` was missing; this plan's first action is `mkdir -p docs/reports/gtm/`.

<!-- Source count: 5 distinct sources (issue body + #2554/#2555/#1669/#2016 + BUSINESS_BRAIN + 8 GTM files). Meets ≥3 requirement. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` |
| Brochure outline (this batch) | `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` |
| Send-tracker schema (this batch) | `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md` |
| Brochure source (post-approval) | `docs/strategy/gtm/vessel-installation-contractors/brochure-source.md` |
| Brochure rendered PDF (post-approval) | `docs/strategy/gtm/vessel-installation-contractors/brochure-source.pdf` |
| Public send tracker (post-approval) | `docs/gtm/intake/send-tracker.public.yaml` |
| Private send tracker (gitignored, never committed) | `docs/gtm/intake/send-tracker.private.yaml` |
| Plan review — Claude | `scripts/review/results/2026-04-29-plan-2556-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-29-plan-2556-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-29-plan-2556-gemini.md` |
| Index update | `docs/plans/README.md` (this row) |

---

## Deliverable

After this issue is done, ACE has: (a) a brochure-as-source Markdown plus a rendered PDF assembled from existing capability summary, the #2555 charts, and proof slots that cite repo evidence; (b) a public/private split send tracker that records every outbound send without any PII in the public repo; and (c) a documented first-batch ready-to-send list keyed to the #2554 contractor matrix, gated behind the BUSINESS_BRAIN legal-sanity checklist before the user authorizes a send.

This issue does **not** itself execute the send. The implementation step produces artifacts; the user (or a future approved-for-execution issue) initiates the actual outbound batch.

---

## Pseudocode

```
build_brochure(capability_summary, charts_2555, proofs):
    sections = [
        cover_with_value_proposition,
        what_we_do_table,        # from capability-summary.md
        capability_charts,        # 3 chart slots; sources from #2555
        proof_points,             # 1,292 cases + per-demo case counts
        engagement_tiers,         # screening / detailed / operations
        cta_block,                # 20-min walkthrough + sample case offer
        legal_disclaimer          # P.E. credentials, no client logos
    ]
    enforce: every numeric claim cites a repo path or public source
    enforce: no client-identifying content
    enforce: zero contact details on the brochure cover (only info@aceengineer.com)
    render to PDF via pandoc or md-to-pdf skill

build_outbound_copy_variants(templates, tier):
    for tier in [1, 2, 3]:
        pick_subject_lines(library)         # 3 A/B candidates per tier
        pick_body(templates.cold_intro)     # template 1
        attach_personalization_slots        # [COMPANY], [VESSEL_CLASS], [HOOK]
        no_attachment_on_cold               # link only
    return tier_map

build_send_tracker_schema():
    public = {
        prospect_id_hash,        # salted SHA-256; no name in public file
        contractor,              # company name (public)
        tier,                    # 1|2|3
        segment,                 # heavy_lift|pipelay|subsea_construction|wind|...
        target_role_class,       # role family, NOT person name (e.g. eng_mgr)
        evidence_source_url,     # public; verified URL
        personalization_hook,    # short string referencing fleet/recent_project
        artifact_id,             # brochure_v1, demo_3, ...
        send_state,              # SCHEDULED|SENT|REPLIED|MEETING|CLOSED|FAILED
        send_channel,            # email_personal | linkedin
        send_date_utc,
        followup_due_utc,
        response_class,          # POSITIVE|NEUTRAL|NEGATIVE|NO_REPLY
        fallback_applied,        # nullable; aligns with prospect_demo_sop F1-F5
        last_legal_scan_utc      # required before any state can flip to SENT
    }
    private = public + {
        contact_name, contact_email, contact_phone, contact_linkedin_url,
        source_of_contact, last_human_touch_notes
    }
    private path is gitignored; presence is enforced by .gitignore line; tests confirm.

legal_sanity_gate(send_row):
    require: artifact provenance recorded
    require: public-vs-private inputs identified
    require: methodology citations attached
    require: legal-sanity scan run on brochure source
    require: no client-identifying content in published brochure
    block send if any check fails
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` | Canonical brochure outline (sections, chart slots, proof slots, CTA, outbound copy variants) |
| Create | `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md` | Public/private split send-tracker schema documentation |
| Create | `docs/strategy/gtm/vessel-installation-contractors/brochure-source.md` | Brochure-as-source Markdown (post-approval) |
| Create | `docs/strategy/gtm/vessel-installation-contractors/brochure-source.pdf` | Rendered PDF (post-approval; via pandoc/md-to-pdf) |
| Create | `docs/gtm/intake/send-tracker.public.yaml` | Public outbound tracker (no PII) (post-approval) |
| Create (untracked) | `docs/gtm/intake/send-tracker.private.yaml` | Private companion (gitignored) (post-approval) |
| Modify | `.gitignore` | Add `docs/gtm/intake/send-tracker.private.yaml` and `*.private.yaml` glob under `docs/gtm/intake/` |
| Update | `docs/plans/README.md` | Add this plan's row to the Plan Index |
| Update | `docs/gtm/deliveries-log.md` | Optional: append a comment block clarifying that this log is for inbound prospect-demo deliveries; outbound sends are tracked in the new send-tracker (cross-link only, no schema change) |
| Create | `scripts/review/results/2026-04-29-plan-2556-{claude,codex,gemini}.md` | Adversarial review artifacts (after plan is reviewed) |

Brochure source and tracker artifacts (`docs/strategy/gtm/...`, `docs/gtm/intake/...`) materialize only after `status:plan-approved` per the issue-planning-mode workflow. The two `docs/reports/gtm/` documents land **with this draft plan** because they are themselves the planning/scoping artifacts (outline + schema), not the execution outputs.

---

## TDD Test List

This issue is artifact-driven, not module-driven. The "tests" are checklist gates that run against the produced artifacts. No `pytest`/`uv run` test code is added unless a future implementation slice introduces a tracker-validator script.

| Check | What it verifies | Pass condition |
|---|---|---|
| brochure_provenance_check | Every numeric/standards claim in the brochure source cites a repo path or external public source | All claims grep-locatable to a citation in the same file |
| brochure_no_client_logos | Brochure does not embed client logos, client project names, or seal/certification of third parties | Visual inspection + grep against `client_projects/` indices |
| legal_sanity_scan | `scripts/legal/legal-sanity-scan.sh --diff-only` over brochure-source diff | Exit 0 |
| send_tracker_pii_split | Public tracker contains zero contact-name, email, phone, or LinkedIn-URL fields | grep `(contact_name|contact_email|contact_phone|linkedin)` against public file → 0 matches |
| send_tracker_gitignore | Private tracker path is matched by `.gitignore` | `git check-ignore docs/gtm/intake/send-tracker.private.yaml` returns the path |
| send_tracker_state_enum | `send_state` field uses the allowed enum exclusively | Schema doc lists enum; future validator script enforces |
| send_tracker_legal_gate | No row may transition to `SENT` without `last_legal_scan_utc` populated | Schema doc states the rule; runtime enforcement is a future-issue scope |
| brochure_pdf_renderable | The Markdown source renders to PDF via the `data:md-to-pdf` skill or `pandoc` without errors | Successful PDF output, ≥3 pages, all chart slots replaced |
| outline_chart_slots_match_2555 | Each chart slot in the outline is named to match a deliverable produced by #2555 | Cross-reference table in outline; reviewer-verifiable |
| copy_variants_per_tier | Outline includes ≥3 outbound copy variants (Tier 1/2/3) sourced from `email-outreach-templates.md` | 3+ variants, each named to template-id |

---

## Acceptance Criteria

Mapped to the GitHub issue's acceptance criteria:

- [ ] Brochure has an evidence-bounded value proposition and (slots for) vessel capability visuals from #2555. → covered by `brochure_provenance_check` + `outline_chart_slots_match_2555`.
- [ ] Outreach copy is personalized by contractor tier/segment. → covered by `copy_variants_per_tier`; populated from `docs/gtm/email-outreach-templates.md`.
- [ ] Send tracker exists and distinguishes public artifact paths from private contact details. → covered by `send_tracker_pii_split` + `send_tracker_gitignore`.
- [ ] Legal/evidence sanity review is complete before public/client-facing distribution. → covered by `legal_sanity_scan` + `send_tracker_legal_gate`.

Plan-level acceptance:

- [ ] Brochure outline (`docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`) exists and lists every section, chart slot, proof requirement, CTA, and outbound template variant.
- [ ] Send-tracker schema document (`docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md`) defines public columns, gitignored private companion, and the legal-sanity gate.
- [ ] Plan-index row added to `docs/plans/README.md`.
- [ ] Adversarial review artifacts posted under `scripts/review/results/` from at least two providers; no unresolved MAJOR.
- [ ] No emails are sent and no contact details land in any public file as part of this issue's execution slice.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | (not yet) | — |
| Codex  | (not yet) | — |
| Gemini | (not yet) | — |

**Overall result:** PENDING — adversarial review has not been dispatched as part of this draft.

This plan is intentionally held at `status: draft` per the prompt's strict rules ("Only add status:plan-review if you completed a canonical plan plus adversarial review evidence"). Promotion to `status:plan-review` is the next operational action; the user must dispatch the cross-review wave or authorize an agent to do so via `scripts/review/cross-review.sh` (or the `submit-to-codex.sh` / `submit-to-gemini.sh` per-provider wrappers).

---

## Risks and Open Questions

- **Risk:** #2554 (matrix) and #2555 (charts) are still OPEN. The brochure references their outputs; if either ships incomplete, the brochure has empty slots. Mitigation: outline names slots by sibling-issue ID so missing pieces are visible in review, not papered over.
- **Risk:** `docs/gtm/capability-summary.pdf` is older than its `.md` counterpart; reusing the PDF as-is would silently ship a stale artifact. Mitigation: regenerate PDF from the new brochure source; do not ship the historical PDF.
- **Risk:** Personalization hooks pulled from `outreach-candidate-briefs-2026-04-28.md` may include scraped material that has not passed legal sanity. Mitigation: the legal-sanity gate runs against the brochure source AND each personalization hook before it is committed to the public tracker.
- **Risk:** Send-tracker schema bifurcation is only as strong as the `.gitignore` enforcement and reviewer discipline; an accidental `git add -f` could leak the private file. Mitigation: pre-commit hook check (future issue scope) + explicit naming pattern (`*.private.yaml`) that already pattern-blocks easily.
- **Risk:** ACE Engineer brand voice in `email-outreach-templates.md` is established; rewriting it for the brochure may drift the voice. Mitigation: the brochure outline lifts copy directly where it can; new copy is bounded to chart captions and proof slots.
- **Open:** Should the brochure ship as PDF only, HTML only, or both? Recommended default: Markdown source + PDF for cold sends, HTML for the gated-URL surface defined in `prospect-demo-sop.md`. Flag for user decision at approval time.
- **Open:** Should the public send tracker be Markdown table or YAML? The schema document defaults to YAML for tooling-friendliness; Markdown rendered table can be auto-generated from YAML if the user prefers visual review.
- **Open:** Tracker write-frequency — append-on-event (every send) vs. batch nightly. Affects whether agent-driven sends are allowed at all. Default: append-on-event, human-initiated only.

---

## Complexity: T2

**T2** — produces multiple new artifacts (brochure outline, send-tracker schema, brochure source, tracker YAMLs) plus an index and `.gitignore` change; no library code, no calculation/standards work. Not a single-line change (T1), not multi-module architectural (T3).
