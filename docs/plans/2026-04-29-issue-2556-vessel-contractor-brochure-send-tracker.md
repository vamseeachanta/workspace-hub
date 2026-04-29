# Plan for #2556: Vessel-Contractor Brochure and Outbound Send Tracker

> **Status:** draft (plan-revision r2 — 2026-04-29 next-wave-autofeed-followup; ready for re-review, NOT for approval)
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2556
> **Depends on:** [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555) (chart deliverables; this plan cannot promote past `status:plan-review` until #2555 lands real chart artifacts under `docs/reports/gtm/charts/`); soft input from [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) (contractor matrix — drives first-batch ready-to-send list shape).
> **Review artifacts:** `scripts/review/results/2026-04-29-plan-2556-nextwave-claude.md` (MAJOR, single-author Claude self-review) | `...-codex.md` (UNAVAILABLE, [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) + permission gate) | `...-gemini.md` (UNAVAILABLE, permission gate)

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
- Found: `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` (5,157 bytes, 2026-04-02) — pre-existing canonical-campaign-folder template document. Predates and overlaps `docs/gtm/email-outreach-templates.md` (244 lines, 7 templates, more recent). **Disposition declared in §Files to Change:** retire the canonical-folder copy by replacing its body with a deprecation header that redirects to `docs/gtm/email-outreach-templates.md` as the single source-of-truth for outbound copy variants. This eliminates the duplicate-source risk surfaced in Claude r1 finding #6 before `brochure-source.md` lands in the same folder.
- Gap: `docs/strategy/gtm/vessel-installation-contractors/` is otherwise sparse — `README.md`, `prospect-list.md`, `value-proposition.md`, `capability-summary.md` called for in #1669 still do not exist. The single existing file is the `email-templates.md` retire candidate above.
- Gap: No outbound send tracker exists today; only the inbound `deliveries-log.md`.
- Gap: No brochure-as-source artifact (Markdown or HTML) exists; only the 1-page summary and a stale PDF.

### Standards

Not applicable — GTM/business issue. Engineering claims surfaced in the brochure must cite their existing evidence sources (DNV/API standards already referenced in `capability-summary.md`).

### LLM Wiki pages consulted

Not applicable to this issue — wiki content is consumed downstream when chart claims (#2555) or methodology claims need provenance, not at brochure-assembly stage. The legal-sanity gate still runs before publication.

### Documents consulted

- `docs/BUSINESS_BRAIN.md` — confirms current weekly target ("for the week of April 1, produce vessel capability charts and send a good brochure to all researched vessel contractors"); legal-sanity gates section enumerates the public-promotion checklist this brochure must pass.
- `docs/gtm/installation-analysis-method-note.md` (17,720 bytes, 2026-04-22) — methodology note required by brochure outline §3.3 Chart C caption. Added per Claude r1 finding #4 (retrieval-completeness gap).
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
- EXISTS: `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` (5,157 bytes, 2026-04-02) — pre-existing template file (retire path declared in §Files to Change)
- EXISTS: `docs/gtm/installation-analysis-method-note.md` (17,720 bytes, 2026-04-22) — methodology note for brochure outline §3.3 Chart C
- EXISTS: `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` — current #2555 deliverable (storyboard only; chart artifacts pending)
- MISSING (this plan creates): `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`
- MISSING (this plan creates): `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md`
- MISSING (this plan creates, downstream of approval): `docs/strategy/gtm/vessel-installation-contractors/brochure-source.md`
- MISSING (this plan creates, downstream of approval): `docs/gtm/intake/send-tracker.public.yaml`
- MISSING (gitignored, NEVER tracked): `docs/gtm/intake/send-tracker.private.yaml`

**Gap proofs:**
- `ls /mnt/local-analysis/workspace-hub/docs/strategy/gtm/vessel-installation-contractors/` returns ONE file: `email-templates.md` (5,157 bytes, 2026-04-02). MISSING: `README.md`, `prospect-list.md`, `value-proposition.md`, `capability-summary.md` — confirms #1669 Phase 1 is partial: only the template doc exists, and it is the older copy (the `docs/gtm/email-outreach-templates.md` 244-line doc is the more recent and richer version). Plan §Files to Change declares the retire-and-redirect disposition for the existing canonical-folder file.
- `ls /mnt/local-analysis/workspace-hub/docs/reports/gtm/` returns the #2555 storyboard only — no chart artifact files. Confirms #2555 has not yet shipped chart deliverables; this plan's `outline_chart_slots_match_2555_artifacts` check is hard-blocked behind #2555 closure.

<!-- Source count: 6 distinct sources (issue body + #2554/#2555/#1669/#2016 + BUSINESS_BRAIN + 9 GTM files including installation-analysis-method-note.md added in r2). Meets ≥3 requirement. -->

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
| Modify (retire+redirect) | `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` | Resolves Claude r1 finding #6 duplicate-source risk. Replace body with a one-screen deprecation header pointing at `docs/gtm/email-outreach-templates.md` as the single source-of-truth for outbound copy variants; preserve the file as a redirect stub so any downstream reader landing on the canonical-folder path is routed to the up-to-date copy. Do NOT delete (history is referenced from #1669 Phase 1). |
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
| outline_chart_slots_match_2555_storyboard | Each chart slot in the outline matches a slot ID in the existing #2555 storyboard at `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` | Cross-reference table in outline lists storyboard slot IDs; reviewer-verifiable today |
| outline_chart_slots_match_2555_artifacts | Each chart slot resolves to a real chart artifact (PNG/SVG) under `docs/reports/gtm/charts/` produced by #2555 | **Hard-blocked behind #2555 closure.** This check moves from "deferred" to "passing" only after #2555 lands chart files; promotion past `status:plan-review` is gated on this. |
| brochure_proof_count_provenance | Each per-demo case-count claim cited in brochure outline §3.4 (Demo 1: 680 / 2: 72 / 3: 180 / 4: 60 / 5: 300 / total 1,292) is traceable to a literal in `digitalmodel/examples/demos/gtm/demo_0X_*.py` or its README | Each number traces by `grep` to a cited demo file or its generated output; failed traces block publication. Resolves Claude r1 finding #2 (1,292-cases reviewer-discipline-only). |
| brochure_demo_path_full_filenames | Outline §3.4 cites canonical filenames (`demo_01_dnv_freespan_viv.py`, `demo_02_wall_thickness_multicode.py`, `demo_03_deepwater_mudmat_installation.py`, `demo_04_shallow_water_pipelay.py`, `demo_05_deepwater_rigid_jumper_installation.py`) — not bare `demo_01`/`demo_02` shorthand | Reviewer can ctrl-click each to source; `grep -F` against the outline returns the full filenames. Resolves Claude r1 finding #5. |
| copy_variants_per_tier | Outline includes ≥3 outbound copy variants (Tier 1/2/3) sourced from `docs/gtm/email-outreach-templates.md` (NOT the retired canonical-folder copy) | 3+ variants, each named to template-id; provenance comments cite the `docs/gtm/` source only |

---

## Acceptance Criteria

Mapped to the GitHub issue's acceptance criteria:

- [ ] Brochure has an evidence-bounded value proposition and (slots for) vessel capability visuals from #2555. → covered by `brochure_provenance_check` + `outline_chart_slots_match_2555`.
- [ ] Outreach copy is personalized by contractor tier/segment. → covered by `copy_variants_per_tier`; populated from `docs/gtm/email-outreach-templates.md`.
- [ ] Send tracker **schema document** exists (at `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md`) and the schema distinguishes public artifact paths from private contact details (PII). → covered by `send_tracker_pii_split` + `send_tracker_gitignore` (file-presence + grep checks). **Note:** runtime enforcement of the `send_state` enum and the `last_legal_scan_utc` legal gate is documentation-surface only in this plan; binding runtime enforcement is out of scope and tracked under §Risks "runtime-enforcement follow-up". Resolves Claude r1 finding #7.
- [ ] Legal/evidence sanity review is complete before public/client-facing distribution. → covered by `legal_sanity_scan` (existing script over the brochure-source diff) + `send_tracker_legal_gate` schema rule (documentation-surface only — runtime enforcement deferred to follow-up issue).

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
| Claude (single-author r1, 2026-04-29 nextwave) | MAJOR | (1) Gap-proof claims `docs/strategy/gtm/vessel-installation-contractors/` is empty, but `email-templates.md` (2026-04-02, 5,157 bytes) exists there — duplicate-source risk vs `docs/gtm/email-outreach-templates.md`. (2) Brochure proof-counts (Demo 1: 680 / 2: 72 / 3: 180 / 4: 60 / 5: 300, total 1,292) ship with no provenance check in TDD. (3) `outline_chart_slots_match_2555` is unverifiable today — #2555 has only a storyboard, no chart deliverables; declare `Depends on: #2555` or rewrite check. (4) `installation-analysis-method-note.md` cited in outline §3.3 but missing from plan §Resource Intelligence "Documents consulted". (5) Demo path strings in outline §3.4 (`demo_01`...`demo_05`) do not match real filenames (`demo_01_dnv_freespan_viv.py`...). (6) Disposition of existing `vessel-installation-contractors/email-templates.md` not declared. (7) `send_tracker_state_enum` / `send_tracker_legal_gate` deferred to "future issue scope" but Acceptance Criteria treat them as in-scope — name the runtime-enforcement issue. |
| Codex | UNAVAILABLE | Bash permission gate in this planning-only autofeed session blocked `scripts/review/plan-review-fanout.sh` dispatch (`feedback_permission_gate_blocks_cross_review.md`); even if dispatched, codex-cli 0.124.0 hangs on stdin per [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) and downgrade does not help from inside Claude Code's Bash tool. Run from un-sandboxed terminal after `npm install -g @openai/codex@0.123.0`. |
| Gemini | UNAVAILABLE | Same Bash permission-gate; Gemini wrapper itself is healthy after the 2026-04-24 `GEMINI_CLI_TRUST_WORKSPACE` fix. Run from un-sandboxed terminal. |

**Overall result:** SINGLE-AUTHOR MAJOR — multi-provider consensus is not yet established. Plan must remain at `status: draft` until at least one additional provider (Codex via downgrade, or Gemini) lands a structured artifact under `scripts/review/results/`. Three Claude findings (#1 gap-proof error, #3 #2555 ordering, #6 duplicate-source) are blocking; the plan-revision r2 below addresses them in-document but does NOT establish multi-provider consensus.

Per `docs/BUSINESS_BRAIN.md` lines 89–97, promoting to `status:plan-approved` requires *"repeated APPROVE/MINOR adversarial-review outcomes across Claude/Codex/Gemini with no unresolved MAJOR findings"* — current artifacts do not satisfy that criterion.

**Revisions made (plan-revision r2 — 2026-04-29 next-wave-autofeed-followup):**

| Finding | Severity | Resolution in r2 |
|---|---|---|
| #1 — gap-proof factual error (claimed `vessel-installation-contractors/` directory empty) | MAJOR / blocking | §Resource Intelligence "Existing repo code", "Evidence → File existence", and "Gap proofs" rewritten to acknowledge the existing 5,157-byte `email-templates.md` (2026-04-02) and declare the retire-and-redirect disposition |
| #2 — 1,292-cases proof claim shipped without provenance check | MINOR | Added `brochure_proof_count_provenance` TDD row that grep-traces each per-demo number to `digitalmodel/examples/demos/gtm/demo_0X_*.py` |
| #3 — `outline_chart_slots_match_2555` unverifiable until #2555 ships chart artifacts | MAJOR / blocking | Front-matter declares `Depends on: #2555`. TDD row split into `_storyboard` (passable today) and `_artifacts` (hard-blocked behind #2555 closure; gates promotion past `status:plan-review`) |
| #4 — `installation-analysis-method-note.md` cited in outline §3.3 but missing from plan's Documents-consulted | MINOR | Added to §Resource Intelligence "Documents consulted" and "File existence" |
| #5 — demo-path strings in outline §3.4 do not match real filenames | MINOR | Added `brochure_demo_path_full_filenames` TDD row that requires canonical filenames; outline body fix is downstream of plan-approval (cannot edit outline from this patch lane) |
| #6 — disposition of canonical-folder `email-templates.md` undeclared | MAJOR / blocking | New row in §Files to Change: "Modify (retire+redirect)" replaces body with deprecation header pointing at `docs/gtm/email-outreach-templates.md` as single source-of-truth; preserves history without leaving a duplicate-source trap |
| #7 — `send_tracker_state_enum` / `_legal_gate` deferred to future issue but ACs treat them as in-scope | MINOR | Acceptance Criteria rephrased to verify documentation-surface only (schema doc + grep checks); runtime enforcement explicitly deferred and called out in §Risks as a follow-up to file before any human-initiated outbound send executes |

**Provider coverage after r2:** Unchanged. Codex remains UNAVAILABLE (#2479 + this session's permission gate); Gemini remains UNAVAILABLE (permission gate). r2 is a single-author plan-revision pass, NOT a re-review. The plan is ready for re-review only — not for `status:plan-review` and definitely not for `status:plan-approved`. Operator must run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` from an un-sandboxed terminal (after `npm install -g @openai/codex@0.123.0` per #2479) to land real Codex + Gemini artifacts before the Business-Brain consensus criterion can be met.

---

## Risks and Open Questions

- **Risk:** #2554 (matrix) and #2555 (charts) are still OPEN. The brochure references their outputs; if either ships incomplete, the brochure has empty slots. Mitigation: outline names slots by sibling-issue ID so missing pieces are visible in review, not papered over.
- **Risk:** `docs/gtm/capability-summary.pdf` is older than its `.md` counterpart; reusing the PDF as-is would silently ship a stale artifact. Mitigation: regenerate PDF from the new brochure source; do not ship the historical PDF.
- **Risk:** Personalization hooks pulled from `outreach-candidate-briefs-2026-04-28.md` may include scraped material that has not passed legal sanity. Mitigation: the legal-sanity gate runs against the brochure source AND each personalization hook before it is committed to the public tracker.
- **Risk:** Send-tracker schema bifurcation is only as strong as the `.gitignore` enforcement and reviewer discipline; an accidental `git add -f` could leak the private file. Mitigation: pre-commit hook check (future issue scope) + explicit naming pattern (`*.private.yaml`) that already pattern-blocks easily.
- **Risk:** ACE Engineer brand voice in `email-outreach-templates.md` is established; rewriting it for the brochure may drift the voice. Mitigation: the brochure outline lifts copy directly where it can; new copy is bounded to chart captions and proof slots.
- **Risk (ordering, declared in front-matter):** This plan depends on #2555 chart deliverables. `outline_chart_slots_match_2555_artifacts` cannot pass until #2555 lands real chart files under `docs/reports/gtm/charts/`. Mitigation: front-matter `Depends on: #2555`; promotion past `status:plan-review` is gated on #2555 closure; `_storyboard` variant of the same check provides interim verification against the existing storyboard.
- **Risk (duplicate-source):** Two `email-templates`/`email-outreach-templates` documents currently coexist (`docs/strategy/gtm/vessel-installation-contractors/email-templates.md` 2026-04-02, 5,157 bytes vs `docs/gtm/email-outreach-templates.md` 2026-04-29-ish, 244 lines). Mitigation: the `Modify (retire+redirect)` row in §Files to Change replaces the older canonical-folder copy with a deprecation header before any new collateral lands in that directory.
- **Runtime-enforcement follow-up (must file before any send executes):** `send_tracker_state_enum` (state-machine guard) and `send_tracker_legal_gate` (mandatory `last_legal_scan_utc` populated before any row can flip to `SENT`) are documented in this plan but enforced only by reviewer discipline. Before any human-initiated outbound send executes against a populated tracker, a sibling issue must be filed to (a) write a tracker-validator script that fails closed when state-machine or legal-gate invariants are violated, (b) wire it into pre-commit and into a hypothetical `gh-action: gtm-send-validator`, and (c) define the precommit hook path. This plan does not file that issue (planning-only patch lane); the operator must file it at user-approval time. Resolves Claude r1 finding #7 by making the deferred surface explicit instead of implicitly in-scope.
- **Open:** Should the brochure ship as PDF only, HTML only, or both? Recommended default: Markdown source + PDF for cold sends, HTML for the gated-URL surface defined in `prospect-demo-sop.md`. Flag for user decision at approval time.
- **Open:** Should the public send tracker be Markdown table or YAML? The schema document defaults to YAML for tooling-friendliness; Markdown rendered table can be auto-generated from YAML if the user prefers visual review.
- **Open:** Tracker write-frequency — append-on-event (every send) vs. batch nightly. Affects whether agent-driven sends are allowed at all. Default: append-on-event, human-initiated only.

---

## Complexity: T2

**T2** — produces multiple new artifacts (brochure outline, send-tracker schema, brochure source, tracker YAMLs) plus an index and `.gitignore` change; no library code, no calculation/standards work. Not a single-line change (T1), not multi-module architectural (T3).
