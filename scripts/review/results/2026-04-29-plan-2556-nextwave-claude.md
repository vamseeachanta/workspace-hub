## Verdict
MAJOR

## Provenance note
Single-author Claude self-review (r1, "nextwave"). The expected three-provider fanout was attempted via `scripts/review/plan-review-fanout.sh` from this session; the workspace-hub harness permission gate rejected the bash dispatch (documented pattern — see `feedback_permission_gate_blocks_cross_review.md`). Per that precedent, this artifact is Claude-authored adversarial review with explicit absence stubs for Codex and Gemini. Multi-provider consensus is **not** established by this batch. Run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` from an un-sandboxed terminal before promoting this plan past `status:plan-review`.

## Retrieval
- Read `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` end-to-end.
- Read `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` end-to-end.
- Read `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md` end-to-end.
- `ls -la docs/strategy/gtm/vessel-installation-contractors/` — directory contains `email-templates.md` (5,157 bytes, 2026-04-02). The plan asserts the directory is empty.
- `ls -la docs/gtm/intake/` — directory exists with `canonical-vessels/`, `IMPLEMENTATION-STATUS.md`, `prospect-schema.json`, `prospect-template.yaml`, `README.md`.
- `ls -la docs/gtm/capability-summary.md docs/gtm/email-outreach-templates.md docs/gtm/prospect-demo-sop.md docs/gtm/deliveries-log.md docs/gtm/outreach-candidate-briefs-2026-04-28.md docs/strategy/engineering-chatbot-oilgas-pitch.md` — all exist.
- `ls -la docs/gtm/installation-analysis-method-note.md` — exists (17,720 bytes, 2026-04-22) and is cited in brochure outline §3.3 Chart C, but is **not** listed in plan §Resource Intelligence "Documents consulted".
- `ls -la digitalmodel/examples/demos/gtm/` — confirms `demo_01_dnv_freespan_viv.py`, `demo_02_wall_thickness_multicode.py`, `demo_03_deepwater_mudmat_installation.py`, `demo_04_shallow_water_pipelay.py`, `demo_05_deepwater_rigid_jumper_installation.py`. The brochure outline cites "demo_01" / "demo_02" / etc. without the suffix — mismatch noted.
- `gh issue view 2554 / 2555 / 2016` — all OPEN with labels confirmed; `gh issue view 1669` — OPEN, label set is `cat:business`, `cat:strategy`, `domain:gtm` (no `priority:high` despite plan referring to it as the parent campaign).
- `ls docs/reports/gtm/` — confirms `2026-04-29-vessel-capability-chart-storyboard.md` (the #2555 deliverable is currently a storyboard, not actual charts).

## Findings

1. **Gap-proof contradicts filesystem reality (plan §Resource Intelligence → "Gap proofs").**
   Plan claim: *"`ls /mnt/local-analysis/workspace-hub/docs/strategy/gtm/vessel-installation-contractors/` returns empty (no `README.md`, no `prospect-list.md`, no `value-proposition.md`, no `email-templates.md`, no `capability-summary.md`)"*. Reality: `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` exists (5,157 bytes, last modified 2026-04-02). The "no `email-templates.md`" claim is false. This poisons the gap analysis: the plan proposes a brochure-source artifact at `docs/strategy/gtm/vessel-installation-contractors/brochure-source.md` and outbound copy variants pulled from `docs/gtm/email-outreach-templates.md`, while the canonical-campaign-folder `email-templates.md` (an older copy from 2026-04-02) is unmentioned. Reviewer cannot tell whether the existing file should be deprecated, replaced, or merged.

2. **Public-brochure proof claims are unverified by the plan's own TDD (brochure outline §3.4, plan §TDD Test List).**
   The brochure outline asserts a five-row case-count table (Demo 1: 680; Demo 2: 72; Demo 3: 180; Demo 4: 60; Demo 5: 300; total 1,292) and ties this to `digitalmodel/examples/demos/gtm/demo_0X`. The plan's TDD list contains `brochure_provenance_check` (claims must cite a path), but no check that walks each cited demo to verify the case-count number. `BUSINESS_BRAIN.md` line 120 forbids "any public/client-facing GTM claim that exceeds repo evidence". Without a proof-count provenance pass, the brochure's headline 1,292-cases claim ships as reviewer-discipline-only.

3. **`outline_chart_slots_match_2555` is unverifiable at plan-approval time (plan §TDD Test List).**
   The check requires "each chart slot in the outline is named to match a deliverable produced by #2555". Today, #2555 is OPEN; the only #2555 artifact under `docs/reports/gtm/` is `2026-04-29-vessel-capability-chart-storyboard.md` — a storyboard document, not chart PNG/SVG outputs. The plan's TDD entry states "cross-reference table in outline; reviewer-verifiable" but the cross-reference target does not exist yet. Either declare a hard order-of-operations dependency (#2555 must ship deliverables A/B/C before this plan can promote past plan-review), or rewrite the check to validate against the storyboard's slot IDs only.

4. **Retrieval-contract gap: `installation-analysis-method-note.md` cited in outline but not in plan's Documents-consulted list (plan §Resource Intelligence "Documents consulted" vs brochure outline §3.3).**
   Outline §3.3 Chart C caption requirement: *"cites the methodology note in `docs/gtm/installation-analysis-method-note.md`"*. The plan's Documents-consulted list (lines 41–48 of the plan) omits this file. Per the issue-planning-mode retrieval contract, every document referenced by a child artifact must appear in the parent plan's Resource-Intelligence summary so the reviewer can audit completeness.

5. **Demo-path strings in outline §3.4 do not match real filesystem paths.**
   Outline cites `digitalmodel/examples/demos/gtm/demo_01`, `demo_02`, etc. as bare directories. Real filesystem entries are `demo_01_dnv_freespan_viv.py`, `demo_02_wall_thickness_multicode.py`, `demo_03_deepwater_mudmat_installation.py`, `demo_04_shallow_water_pipelay.py`, `demo_05_deepwater_rigid_jumper_installation.py`. The outline's "Source" column is therefore not directly grep-able from a reviewer's terminal — fix path strings or declare the convention.

6. **Existing `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` (the canonical-campaign-folder copy, 2026-04-02) creates a duplicate-source risk that the plan does not address.**
   Plan §Files to Change creates `brochure-source.md` and `brochure-source.pdf` in this directory but is silent on the existing `email-templates.md`. Two outcomes are possible: (a) reviewers assume the existing file is authoritative and the plan's reference to `docs/gtm/email-outreach-templates.md` (the `docs/gtm/` copy) is a layering bug, or (b) the existing canonical-folder file is stale and should be removed. The plan must declare the disposition before approval.

7. **`send_tracker_state_enum` and `send_tracker_legal_gate` are deferred to "future issue scope" (plan §TDD Test List), but the plan's own Acceptance Criteria treat them as in-scope ("Send tracker exists and distinguishes public artifact paths from private contact details", "Legal/evidence sanity review is complete before public/client-facing distribution").**
   The plan documents the rule but does not name the runtime enforcement — no script path, no CI step, no pre-commit hook. The Acceptance Criteria therefore reduce to reviewer-discipline-only gates, which is exactly the failure mode `BUSINESS_BRAIN.md` line 124 warns against. Either name the runtime-enforcement issue and link it as `Depends on:` or downgrade the Acceptance Criteria to reflect the current verification surface (manual review + grep).

## Blockers

- Finding 1 — gap-proof factual error invalidates the plan's stated "what does not exist" rationale. Block until corrected: re-read the canonical-campaign folder, declare the disposition of the existing `email-templates.md`, and update the plan's Resource-Intelligence summary.
- Finding 3 — `outline_chart_slots_match_2555` cannot pass at plan-approval time. Either declare `Depends on: #2555` and record a hard-ordering constraint, or rewrite the check.
- Finding 6 — duplicate-source risk between `docs/gtm/email-outreach-templates.md` and the canonical-folder `email-templates.md` must be resolved before brochure-source.md is created in the same folder.

Findings 2, 4, 5, 7 are MINOR-MAJOR borderline; recommend addressing during plan-review revision pass before the user grants approval.
