# Adversarial Plan Review Request: workspace-hub #2555

## Role
You are an independent adversarial reviewer. Be skeptical. Find missing acceptance criteria, evidence gaps, public/private data risks, workflow-gate errors, and false readiness claims. Do not rubber-stamp.

## Context
This is part of the Business Brain / GTM vessel-contractor wave. The repository uses hard gates: Issue -> Plan -> Adversarial Review -> status:plan-review -> USER APPROVES -> status:plan-approved -> Implementation/TDD -> Verification -> Close.

The current move is planning/review-readiness only. No outreach should be sent, no private contact data should be added to public repo files, and `UNAVAILABLE` provider artifacts must not be counted as live non-Claude review evidence.

## Issue under review
- Issue: workspace-hub #2555
- Title: Vessel capability charts review-readiness
- Review focus: chart/storyboard acceptance criteria, render-entry location, headline-number verification, API/code-reference caution, provider-review gate, and whether the plan is ready for status:plan-review.

## Required output format
Start with exactly one line:
`Verdict: APPROVE|MINOR|MAJOR`

Then provide:
1. Summary rationale.
2. Severity-ranked findings grouped as CRITICAL/HIGH/MEDIUM/LOW.
3. Explicit answer: Is this ready for `status:plan-review`? Why or why not?
4. Exact must-fix patches if verdict is MAJOR or MINOR.
5. Any user inputs needed before downstream #2556 brochure/outbound work.

## Plan artifact: docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md

```markdown
# Plan for #2555: feat(gtm): vessel capability charts for contractor brochure

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2555
> **Review artifacts:** scripts/review/results/2026-04-29-plan-2555-claude.md (TBD) | ...-codex.md (TBD) | ...-gemini.md (TBD)
> **Sibling overnight prompt:** `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/2555-capability-charts.md`
> **Storyboard artifact:** `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json` — 2 representative S-lay vessel classes (Large PLV, Shallow Water Barge) with tensioner capacity, stinger config, water-depth range, pipe-size range, sea-state limits. Header explicitly states "representative of real vessel classes" — not exact named-vessel specs. Acceptable public/inferred dataset for the chart inputs.
- Found: `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json` — 2 representative CSV/HLV classes (Large CSV ~Aegir/Borealis, Medium CSV ~Normand Maximus/Seven Arctic) with crane SWL curve, RAO peaks, operational limits. Same representative-class disclaimer.
- Found: `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` — pre-computed cross-demo go/no-go matrix across 4 vessels for mudmat installation, jumper installation, and shallow pipelay. Includes head-to-head comparison narratives. This is the primary chart-feed.
- Found: `digitalmodel/examples/demos/gtm/results/structure_comparison_matrix.json` — by-vessel structure comparison with crane utilisation values at fixed depth. Useful for utilisation-margin chart.
- Found: `digitalmodel/examples/demos/gtm/output/demo_04_shallow_pipelay_report.html` — already renders a Plotly Go/No-Go heatmap (`chart-go_nogo`) for shallow pipelay at line 1086. Demonstrates that chart-rendering scaffolding exists.
- Found: `digitalmodel/examples/demos/gtm/report_template.py` — templating module that the existing 5 demo reports share. New brochure-bound charts should reuse this template path rather than introduce a new renderer.
- Gap: no consolidated brochure-ready capability chart pack exists across `digitalmodel/`, `docs/gtm/`, or `docs/reports/`. `docs/reports/gtm/` did not exist before this plan and is created here.
- Gap: the future chart-rendering entry point outside `digitalmodel/` was previously unnamed; this patch locks the intended implementation home to a new follow-on wrapper script at `scripts/gtm/render_brochure_charts.py`, which may import existing `digitalmodel/examples/demos/gtm/report_template.py` helpers without editing `digitalmodel/` source.

### Standards
| Standard | Status | Source |
|---|---|---|
| DNV-ST-F101 (Submarine Pipeline Systems) | referenced (Demo 4 inputs) | `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json:5` |
| DNV-RP-H103 (Marine Operations modelling) | referenced (Demos 3/5 inputs) | `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json:5` |
| DNV-ST-N001 (Marine Operations & Marine Warranty) | referenced (Demos 3/5 inputs) | `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json:6` |
| API RP 1111 (Offshore Hydrocarbon Pipelines) | referenced (Demo 4 inputs) | `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json:7` |

Standards are already cited in the upstream data files. This plan does not introduce new standards work; it inherits the existing chain. Citation contract `.claude/rules/calc-citation-contract.md` remains binding for any *new* numeric constants used by future brochure annotations.

### LLM Wiki pages consulted
- No relevant wiki pages — capability charts are GTM artifacts, not domain knowledge promotion. Wiki promotion is explicitly out-of-scope per `.claude/rules/calc-citation-contract.md` and the deny-list policy on vendor-derivative content.

### Documents consulted
- `docs/BUSINESS_BRAIN.md:106-112` — confirms the April-1 weekly target is "produce vessel capability charts and send a good brochure to all researched vessel contractors." Sets the scope boundary: charts feed the brochure/send issue (#2556), do not stand alone.
- `docs/BUSINESS_BRAIN.md:122-132` — Legal Sanity Gates for Public Artifacts. Public-promotion sanity gate enumerated: source provenance recorded, public/private inputs identified, methodology and standards citations attached, tests/review state known, legal scan run, no confidential/client content. This plan binds those gates to chart promotion.
- `docs/gtm/capability-map.md` — already documents per-demo "Hero chart" framing for Demos 1-5 (lines 92, 98, 103, 112, 118). Brochure charts must compose with these hero charts, not duplicate them.
- `docs/plans/_template-issue-plan.md` — canonical template followed here. Resource Intelligence + Evidence + Pseudocode + Acceptance Criteria sections retained.
- Issue #1799 (OPEN) — public pipelay vessel specs collection. Source for any *additional* vessel classes the chart pack wants to add beyond the 4 representative classes already coded. Currently OPEN, so any chart-pack expansion is gated on #1799.
- Issue #1669 (OPEN) — Tier-1/2/3 vessel installation contractor target list. Defines downstream brochure recipients; sibling #2554 (contractor matrix) decomposes the recipient surface.
- Issue #2016 (OPEN) — GTM client-conversion pipeline parent. Confirms #1669 depends on demos + outreach infrastructure (Tier-3 ordering at line 91). Charts produced under #2555 are the hero-asset slice that #2016 marks as "Needs: parametric demo reports".
- Sibling: `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/2554-contractor-matrix.md`, `2556-brochure-send.md`, `2557-productivity-review.md` — all sibling weekly-target prompts. #2555 must hand off chart artifacts to #2556 without requiring the operator to reassemble context.

### Gaps identified
1. No chart pack exists at `docs/reports/gtm/` (the directory did not exist before this plan).
2. No brochure-bound caption/narrative copy exists for any chart.
3. No legal/evidence sanity-scan record exists for charts about to be sent to external contractors. Required gate per `docs/BUSINESS_BRAIN.md:122-132` and `scripts/legal/legal-sanity-scan.sh`.
4. No defined output-format manifest (PNG/SVG/PDF dimensions, colour palette, typography) exists for brochure-grade exports. Existing demo HTML reports use Plotly defaults — too rich for a 1-2 page brochure.
5. No "headline number" computed from the comparison matrix exists yet (e.g., "Shallow Water Barge: 100% pass rate at 7-30 m water depth, all pipe sizes 8-20 in, 16-row evidence trail"). Headline numbers are the brochure's first hook.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29 via `gh issue view`):
- `#2555` — OPEN — feat(gtm): vessel capability charts for contractor brochure (labels: priority:high, cat:business, cat:strategy, domain:gtm)
- `#1799` — OPEN — DATA: Collect public pipelay barge/vessel specs for shallow water GTM demo
- `#1669` — OPEN — [WRK] GTM: Vessel Installation Contractor Email Outreach Campaign
- `#2016` — OPEN — feat(gtm): client conversion pipeline -- turn repo capability into paying clients

**File existence** (`ls -la` 2026-04-29):
- EXISTS: `docs/BUSINESS_BRAIN.md`
- EXISTS: `docs/gtm/capability-map.md`
- EXISTS: `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json`
- EXISTS: `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json`
- EXISTS: `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json`
- EXISTS: `digitalmodel/examples/demos/gtm/results/structure_comparison_matrix.json`
- EXISTS: `digitalmodel/examples/demos/gtm/output/demo_04_shallow_pipelay_report.html` (already renders chart-go_nogo Plotly heatmap)
- MISSING (this plan creates): `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md`
- MISSING (this plan creates): `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2555-summary.md`
- MISSING (created on directory creation): `docs/reports/gtm/`

**Line excerpts** (`sed -n` 2026-04-29):

Confirms representative-class disclaimer in the vessel data — basis for the public/non-proprietary claim:
```
digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json:1-2
{
  "_description": "Construction Support Vessel (CSV) and Heavy Lift Vessel (HLV) database for GTM demos 3 and 5. Vessel parameters are representative of real vessel classes but are not exact specifications of any named vessel.",
```

Confirms BUSINESS_BRAIN target binding for week of April 1:
```
docs/BUSINESS_BRAIN.md:110
Current/next weekly target seed: **for the week of April 1, produce vessel capability charts and send a good brochure to all researched vessel contractors**.
```

Confirms existing chart scaffolding in demo 4 HTML output:
```
demo_04_shallow_pipelay_report.html:1086-1088
<div class="chart-container">
    <div class='chart-title'>Chart 1: Go/No-Go Installation Matrix</div>
    <div class='chart-subtitle'>Side-by-side vessel comparison across all pipe sizes and water depths.</div>
```

**Gap proofs**:
- `ls docs/reports/gtm/ 2>&1` → "No such file or directory" before this plan ran → confirms the chart storyboard surface must be created.
- `find docs/plans -name "*2555*"` → only `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/2555-capability-charts.md` (overnight prompt body, not a plan) → confirms this is the first canonical plan for the issue.
- `find scripts/review/results -name "*2555*"` → empty → no prior adversarial review evidence.

Distinct sources: 8 (issue #2555 body + 3 related issues #1799/#1669/#2016 + 5 in-repo files: pipelay_vessels.json, csv_hlv_vessels.json, vessel_comparison_matrix.json, BUSINESS_BRAIN.md, capability-map.md). Exceeds the ≥3 minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` |
| Chart storyboard | `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` |
| Existing data inputs | `digitalmodel/examples/demos/gtm/data/{pipelay_vessels,csv_hlv_vessels}.json` |
| Existing result feeds | `digitalmodel/examples/demos/gtm/results/{vessel,structure}_comparison_matrix.json` |
| Existing chart precedent | `digitalmodel/examples/demos/gtm/output/demo_04_shallow_pipelay_report.html` |
| Plan review — Claude | scripts/review/results/2026-04-29-plan-2555-claude.md (TBD) |
| Plan review — Codex | scripts/review/results/2026-04-29-plan-2555-codex.md (TBD) |
| Plan review — Gemini | scripts/review/results/2026-04-29-plan-2555-gemini.md (TBD) |
| Overnight result | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2555-summary.md` |
| Plan index update | `docs/plans/README.md` |

Out-of-scope (handed off):
- Contractor recipient list — sibling #2554.
- Brochure assembly + send mechanics — sibling #2556.
- Productivity-flow review — sibling #2557.
- New vessel-class data ingestion (#1799) — explicitly deferred; this plan's chart pack uses only the 4 representative classes already coded.

---

## Deliverable

A planning-only artifact pair (canonical plan + chart storyboard) under `docs/plans/` and `docs/reports/gtm/` that locks chart inventory, data inputs, evidence/legal gate, output format, and acceptance criteria for ≥3 brochure-ready vessel capability charts derivable from existing repo data — without changing `digitalmodel/` source code.

---

## Pseudocode

This is a planning artifact. The "code" here is the storyboard's chart-derivation contract, written so a downstream implementer (Codex, Claude exec, or operator) can produce assets in a single bounded slice.

```
For each chart concept C in {C1..Cn}:
    inputs = read(C.data_paths)            # all from existing JSON files only
    assert inputs.fields ⊇ C.required_fields
    assert all(inputs.disclaimer == "representative of real vessel classes")  # legal gate
    headline = compute_headline_number(inputs, C.headline_rule)
    figure   = render_via_scripts_gtm(inputs, headline)  # future entry point: scripts/gtm/render_brochure_charts.py; may import report_template.py without editing digitalmodel/
    caption  = C.caption_template.format(headline=headline,
                                         scope=C.scope_disclosure,
                                         standards=C.standards_cited)
    # Standards-citation completeness gate: every inherited standard from upstream JSON
    # `_references` arrays must appear in caption.standards OR be recorded in
    # C.omission_rationale (e.g., "API RP 1111 omitted: chart C3 covers crane-lift only,
    # no shallow-pipelay scope"). Defensibility-of-claims rule per .claude/rules/calc-citation-contract.md spirit.
    assert set(C.inherited_standards) <= set(caption.standards) | set(C.omission_rationale.keys())
    legal_scan(figure, caption, C.scope_disclosure)     # scripts/legal/legal-sanity-scan.sh
    # Asset-directory creation gate: brochure asset home must exist before export.
    # Directory is created by the follow-on implementation-slice plan (mkdir -p docs/reports/gtm/assets/),
    # not by this planning artifact. Render aborts cleanly if the gate is missing.
    assert exists("docs/reports/gtm/assets/"), "asset-directory gate not met; create via follow-on slice"
    export(figure, asset_home="docs/reports/gtm/assets/", formats=["png_brochure", "svg_print", "pdf_1page"])
```

Chart concepts and their headline-number rules are spec'd in the storyboard artifact so reviewers can assess plausibility without re-deriving them inline.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` | this plan |
| Create | `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` | chart inventory + caption drafts + format manifest |
| Create (future implementation slice) | `scripts/gtm/render_brochure_charts.py` | exact non-`digitalmodel/` chart-rendering entry point; may import demo rendering helpers without mutating them |
| Create (future implementation slice) | `docs/reports/gtm/assets/` | locked home for brochure PNG/SVG/PDF outputs unless adversarial review rejects it |
| Update | `docs/plans/README.md` | add draft index row |
| Create | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2555-summary.md` | overnight worker handoff |
| (Out of scope) | `digitalmodel/examples/demos/gtm/**` | NO edits in this plan |
| (Out of scope) | actual PNG/SVG/PDF chart assets | deferred to plan-approved implementation slice |

---

## TDD Test List

Planning-only deliverable. The tests below are *plan-readiness checks*, not unit tests:

| Check | Verifies | How |
|---|---|---|
| chart_count_ge_3 | Storyboard documents ≥3 chart concepts | grep `^### Chart C` count in storyboard |
| every_chart_has_data_inputs | Each chart names exact JSON file paths | per-chart "Data Inputs" subsection present |
| every_chart_has_evidence_note | Each chart has public-source/assumption note | per-chart "Evidence & Legal Scope" subsection present |
| every_chart_has_caption_draft | Each chart has draft caption text | per-chart "Caption Draft" subsection present |
| every_chart_has_format_spec | Each chart names target output formats | per-chart "Output Formats" subsection present |
| no_proprietary_input_paths | Storyboard cites only representative-class data | absence of `client_projects/`, `acma-projects/`, `seanation/`, `frontierdeepwater/` paths in storyboard |
| no_named_real_vessel_telemetry | Storyboard does not promise telemetry-from-named-named-vessel | absence of bare named-vessel claims like "Allseas Lorelay measured 3.2m heave on 2024-08-01" — claims must be classed as `representative_class` framings |
| acceptance_criteria_mapped | Each issue AC has at least one chart concept addressing it | traceability matrix in storyboard |

Implementation-time tests (deferred to a follow-on plan-approved slice) include rendering smoke tests against the comparison matrices and a brochure-export integration test.

---

## Acceptance Criteria

- [ ] Plan and storyboard exist under the paths in the Artifact Map.
- [ ] Storyboard inventory has ≥3 chart concepts, each addressing at least one issue AC.
- [ ] Each chart concept names: data inputs (existing repo paths only), required data fields, public-source/representative-class disclosure, standards citations inherited from upstream JSON, draft caption, headline-number rule, and output-format spec (PNG/SVG/PDF dimensions, palette).
- [ ] Storyboard explicitly enumerates the legal sanity-scan gate before any chart is exported for external use, and binds the gate to `scripts/legal/legal-sanity-scan.sh` per `docs/BUSINESS_BRAIN.md:124`.
- [ ] Storyboard has a traceability matrix mapping issue #2555 ACs to chart concepts.
- [ ] Plan index row added to `docs/plans/README.md`.
- [ ] Cross-provider adversarial review evidence is recorded before any `status:plan-review` label is applied: required evidence is Claude **and** Codex **and** Gemini live verdicts (each APPROVE or MINOR). UNAVAILABLE provenance is NOT sufficient for any of the three providers — a `*-nextwave-*` UNAVAILABLE artifact records that the lane could not exercise the provider but does **not** satisfy this AC. If Codex or Gemini is blocked on the host (codex-cli regression, lane-permission scope, sandbox restriction), status remains `draft` until a permitted lane on a working host produces the canonical live artifact at `scripts/review/results/2026-04-29-plan-2555-{codex,gemini}.md` (no `-nextwave` suffix). Until all three live verdicts exist, status remains `draft`.
- [ ] No edits to `digitalmodel/` source code during this plan's lifecycle.
- [ ] No proprietary/client telemetry referenced in any chart concept.
- [ ] Future implementation home is explicitly `scripts/gtm/render_brochure_charts.py` (new wrapper outside `digitalmodel/`), and brochure asset home is explicitly `docs/reports/gtm/assets/` unless adversarial review rejects that location.
- [ ] Future implementation-slice plan creates `docs/reports/gtm/assets/` via `mkdir -p` as an explicit Files-to-Change row before any render call. Render aborts cleanly if the directory is missing (asset-directory gate is enumerated in the Pseudocode `assert exists(...)` step). This planning artifact does NOT create the directory itself.
- [ ] Every chart caption cites the full inherited-standards set from the upstream JSON `_references` arrays (DNV-ST-F101, DNV-RP-H103, DNV-ST-N001, DNV-OS-H101 where applicable, API RP 1111 where shallow-pipelay screening is in scope). If a standard is intentionally omitted (e.g., scope-limited to deepwater-only or crane-lift-only jobs), the storyboard chart entry must record the omission rationale inline; bare omission is not acceptable.
- [ ] Storyboard distinguishes headline numbers verified in this planning wave from headline numbers that must be recomputed/verified during the later render slice.
- [ ] Rendering and brochure-export work is *not* attempted under this plan; a follow-on slice plan is created if implementation is desired.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (next-wave self-review, 2026-04-29) | MINOR | (1) TDD Test List row 1 grep `^## Chart C` is off-by-one heading depth vs. actual storyboard `^### Chart C`; literal pattern returns 0 instead of 4. (2) AC #5 (cross-provider review) unmet without Codex+Gemini live evidence. (3) Chart-rendering code-home unspecified — Files-to-Change marks `digitalmodel/**` out of scope but storyboard pseudocode reuses `report_template.py` which lives there; entry-point path needs naming. (4) Brochure-asset target `docs/reports/gtm/assets/` does not yet exist. (5) Caption draft for C1 cites three of four inherited standards; API RP 1111 omitted without justification despite shallow-S-lay job inheriting it. **Positive verification (not a finding):** Shallow Water Barge headline-number claim ("100% pass rate across 30 cases") matches `vessel_comparison_matrix.json` exactly. |
| Codex (next-wave) | UNAVAILABLE | Lane permission did not auto-approve fanout invocation; codex-cli 0.124.0 upstream regression also unverified on this host. See `scripts/review/results/2026-04-29-plan-2555-nextwave-codex.md`. |
| Gemini (next-wave) | UNAVAILABLE | Lane permission did not auto-approve fanout invocation. See `scripts/review/results/2026-04-29-plan-2555-nextwave-gemini.md`. |

**Overall result:** PENDING — `status:plan-review` cannot be applied this wave. Review evidence is still incomplete, so the plan stays `draft`. This patch wave resolves the document-level MINOR findings by correcting the readiness checks, naming the non-`digitalmodel/` render entry point, locking the brochure asset home, and clarifying provider-unavailable fallback plus headline-number verification scope; live provider artifacts are still required before any status escalation.

**Remaining tasks for the next permitted lane:**
- Obtain live Gemini **and** live Codex review artifacts. Both are required (UNAVAILABLE-documented does not satisfy the tightened cross-provider AC); `status:plan-review` cannot be applied until both canonical artifacts (no `-nextwave` suffix) carry APPROVE or MINOR verdicts.
- If reviewers reject `docs/reports/gtm/assets/` as the brochure asset home, update the plan/storyboard with the approved replacement before implementation.
- During implementation, create `scripts/gtm/render_brochure_charts.py` and `docs/reports/gtm/assets/` exactly as specified here; neither is created in this planning-only patch wave.

Revisions made based on review:
- Fixed the TDD heading-depth check from `^## Chart C` to `^### Chart C`.
- Clarified the provider-review acceptance criterion and documented the permitted unavailable-provider fallback (subsequently tightened — see next-wave patch row below).
- Named the future non-`digitalmodel/` render entry point as `scripts/gtm/render_brochure_charts.py` and locked brochure assets to `docs/reports/gtm/assets/` unless review rejects that home.
- Added an explicit acceptance criterion requiring the storyboard to mark which headline numbers are verified now versus regenerated later.

**Next-wave patch (2026-04-29, planning-only lane — `nextwave-followup-plan-patch-2555-20260429-1446.md`):**
- **Tightened cross-provider AC** so UNAVAILABLE provenance is NOT sufficient for `status:plan-review` for any of the three providers; required evidence is Claude + Codex + Gemini *live* verdicts (each APPROVE or MINOR). Reverses the earlier "permitted fallback" clause that admitted Claude + 1 live + 1 UNAVAILABLE-documented.
- **Added pseudocode mkdir gate** for `docs/reports/gtm/assets/` — render aborts cleanly via `assert exists(...)` if the asset directory is missing; directory creation belongs to the follow-on implementation-slice plan, not this artifact.
- **Added pseudocode standards-citation completeness check** so every inherited standard from upstream JSON `_references` either appears in caption.standards or is recorded in `C.omission_rationale` (defensibility-of-claims rule covering the API RP 1111 concern).
- **Added two acceptance criteria** binding the asset-directory gate and the caption-completeness/omission-rationale rule at plan-AC level.
- Verified during this patch wave: Finding 1 (TDD grep pattern) was already corrected to `^### Chart C` by a prior wave (see Test List row 1 in §"TDD Test List"). Finding 3 (rendering home) was already named to `scripts/gtm/render_brochure_charts.py` in §"Resource Intelligence Summary", §"Files to Change", and §"Acceptance Criteria". Finding 5 (API RP 1111 omitted) was already cited in storyboard C1 caption (line 82); this patch enforces the rule at plan-AC level.
- Patch lane intentionally did NOT (a) edit the storyboard/report files, (b) drive cross-provider fanout, (c) mutate any GitHub label, comment, or status, (d) apply `status:plan-review` or `status:plan-approved`. Cross-provider AC remains unmet and the plan stays `draft`.

Review evidence: `scripts/review/results/2026-04-29-plan-2555-nextwave-{claude,codex,gemini}.md` (this wave); canonical-fanout artifacts at `…/2026-04-29-plan-2555-{claude,codex,gemini}.md` (no `-nextwave` suffix) reserved for a permitted-lane re-run.

---

## Risks and Open Questions

- **Risk: representative-class data may be miscommunicated as named-vessel data.** Mitigation: storyboard mandates a "Scope & Disclosure" line on every chart caption stating the data is representative of vessel classes, not measured telemetry of any named vessel; legal scan gate before export.
- **Risk: charts that look "good enough" get sent to contractors without legal-scan completion.** Mitigation: acceptance criteria binds `scripts/legal/legal-sanity-scan.sh` as a hard gate; sibling #2556 (brochure-send) must verify the gate before transmission.
- **Risk: chart pack drifts from upstream demo numbers when demos rerun.** Mitigation: chart inputs are explicit JSON paths; rerun-and-regenerate is single-step. Storyboard documents the regen contract.
- **Risk: contractor-facing charts overclaim vessel capabilities ACE has not validated against client engagements.** Mitigation: caption template surfaces "screening-grade analysis envelope" framing — never "we have built and operated" framing.
- **Risk: sibling #2554 contractor matrix may add segments (e.g., FOWT installation vessels) that the existing 4-class data does not cover.** Mitigation: storyboard's traceability matrix flags coverage gaps; expansion to new vessel classes is gated on #1799 closure, not on this plan.
- **Risk: Codex review-runner regression** (per memory: codex-cli stdin-hang and sandbox-no-execution issues) **may block adversarial review.** Mitigation: live Codex evidence is required before any status escalation per the tightened AC §209 — Claude + Gemini cross-coverage does NOT satisfy the cross-provider gate when Codex is blocked. If Codex CLI 0.124.0 stdin-hang or sandbox-execution restrictions persist, escalate to the operator for a host-level pin or downgrade per `feedback_codex_cli_0_124_upstream_regression.md` (#2479). Document the UNAVAILABLE provenance for audit, but treat the plan as `draft` until a permitted lane on a working host produces the canonical live artifact at `scripts/review/results/2026-04-29-plan-2555-codex.md`.
- **Open:** Should chart pack default to a 4-class scope (existing data) or wait for #1799 to expand to 8-12 classes? Default in this plan: ship 4-class to unblock #2556; #1799 expansion is a follow-on.
- **Open:** Should rendered chart assets live under `docs/reports/gtm/` (workspace-hub) or `digitalmodel/examples/demos/gtm/output/`? Default: brochure-bound assets live under `docs/reports/gtm/` so they decouple from demo regeneration. Demo HTML reports continue to embed their hero charts as before.

---

## Complexity: T2

**T2** — multi-file planning artifact (canonical plan + storyboard + index update + summary), sources from 4 existing JSON files and 2 existing demo HTML reports, requires cross-provider adversarial review before any status escalation. Implementation slice (rendering + export + legal scan) is intentionally split into a follow-on plan once the storyboard is approved.

```

## Supporting artifact: docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md

```markdown
# Vessel Capability Chart Storyboard — Brochure Pack v0

> **Date:** 2026-04-29
> **Status:** draft (planning artifact — no rendered assets exist yet)
> **Issue:** [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555)
> **Plan:** [`docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md`](../../plans/2026-04-29-issue-2555-vessel-capability-charts.md)
> **Sibling lanes:** [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) (contractor matrix) · [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) (brochure send) · [#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557) (productivity review)

---

## Purpose

Lock the chart pack design for ACE Engineer's vessel-contractor brochure (week of April 1 GTM target). Produce ≥3 brochure-ready capability charts, each derived from existing repo data with explicit public-source/representative-class disclosure and a binding legal sanity gate before any external send.

This document is **planning-only**. No PNG/SVG/PDF assets are emitted by this artifact. Asset generation is a follow-on plan-approved implementation slice.

---

## Source-Data Surface (no client/proprietary data)

| Path | Provides | Disclosure |
|---|---|---|
| `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json` | Large PLV (Castorone/Seven Navica representative class), Shallow Water Barge (DLB representative class): tensioner capacity, stinger length/angle, water-depth range, pipe-size range, sea-state limits | Header: "representative of real vessel classes" |
| `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json` | Large CSV (Aegir/Borealis representative class), Medium CSV (Normand Maximus/Seven Arctic representative class): crane SWL curve, RAO peaks, lift operability limits | Header: "representative of real vessel classes but are not exact specifications of any named vessel" |
| `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` | Cross-demo go/no-go matrix across 4 vessels (mudmat, jumper, shallow pipelay), pass-rates, head-to-head narratives | Computed from above two sources via demos 3/4/5 |
| `digitalmodel/examples/demos/gtm/results/structure_comparison_matrix.json` | By-vessel crane utilisation values at 1500 m for mudmat S/M/L | Computed feed |
| Standards inherited (citations) | DNV-ST-F101, DNV-RP-H103, DNV-ST-N001, DNV-OS-H101, API RP 1111 | Cited in `_references` arrays of the JSON inputs |

**Out-of-bounds paths** (must NOT appear in any chart):
- `client_projects/**`
- `acma-projects/**`
- `seanation/**`
- `frontierdeepwater/**` (5% stake, not a public reference)
- Any vessel-name-keyed measured-telemetry claim sourced from an engagement.

---

## Output-Format Manifest

| Format | Use | Dimensions | Palette | Notes |
|---|---|---|---|---|
| `chart-name.brochure.png` | Brochure embed | 1600 × 900 px @ 2× | ACE primary (TBC against `aceengineer-website` brand), with the existing demo green/amber/red traffic light only for go/no-go cells | Flat — no Plotly hover; no interactive controls |
| `chart-name.print.svg` | Print-quality | vector | Same | Embedded fonts; CMYK-safe colour |
| `chart-name.1page.pdf` | Standalone leave-behind | 8.5 × 11 in | Same | Caption + scope disclosure rendered into the PDF, not just the brochure body |
| `chart-name.html` (optional) | Demo report embed | per `report_template.py` | Plotly defaults | Already exists for demo 4; reuse rather than rebuild |

The brochure assets live under `docs/reports/gtm/assets/` once rendered unless adversarial review explicitly rejects that home. Demo HTML reports remain at `digitalmodel/examples/demos/gtm/output/` and are not duplicated.

The future render entry point is a new wrapper script at `scripts/gtm/render_brochure_charts.py`. That wrapper may import `digitalmodel/examples/demos/gtm/report_template.py` helpers, but #2555 itself does not edit `digitalmodel/` source.

Per memory `aceengineer-website` brand hierarchy and visual-DNA were locked 2026-04-21 (project_claude_design_adoption). Asset palette must be re-confirmed against that contract before rendering.

---

## Chart Inventory

The four charts below cover all four issue acceptance criteria. C1, C2, C3 are the "must-render" set (≥3 required by AC1). C4 is recommended-but-optional and depends on whether the brochure has room.

---

### Chart C1 — Vessel-vs-Job Capability Heatmap (cross-demo)

**The hero chart.** Single grid that answers, for every (vessel × job) pair, "how does the screening-grade analysis say this goes?" — covering mudmat installation, rigid jumper installation, and shallow-water S-lay pipelay.

**Why it leads the brochure:** vessel contractors recognise the go/no-go matrix immediately and can scan their own vessel class against ACE's screening envelope without reading prose.

**Required data fields**
- vessel.name, vessel.type, vessel.crane_capacity_te (where defined), vessel.tensioner_capacity_te (where defined)
- per (job, vessel): pass_rate_pct, total_cases, limiting_factor

**Data inputs** (existing repo paths only)
- `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` — primary feed (pass-rate by capability)

**Headline-number rule**
- Pick the highest pass-rate vessel-job pair from the matrix. As of the 2026-04-15 demo run, the headline reads: **"Shallow Water Barge: 100% pass rate across 30 cases for 8-24 in pipe at 7-30 m water depth."**

**Verification scope (now vs later)**
- **Verified in this planning wave:** `vessel_comparison_matrix.json` confirms the Shallow Water Barge pair is the highest pass-rate vessel-job pair with `pass_rate_pct = 100.0` and `cases_total = 30`.
- **Deferred to render slice:** the pipe-size span (`8-24 in`) and water-depth span (`7-30 m`) must be re-verified from the latest pipelay input/result files at render time and then regenerated if demo outputs changed.

**Caption draft**
> Vessel-vs-job screening envelope from ACE Engineer's parametric analysis suite (108 cases across mudmat, jumper, and shallow-pipelay screening). Coloured cells show pass rate of cases meeting governing-load checks per DNV-RP-H103, DNV-ST-N001, DNV-ST-F101, and API RP 1111 where shallow-pipelay screening is involved. Vessel parameters reflect representative classes — not measured telemetry of any named vessel. Send-screening grade for shortlist purposes; detailed feasibility requires per-project metocean and rigging inputs.

**Evidence & legal scope**
- All 4 vessels are representative classes, disclosed in source JSON headers.
- All standards citations inherited from upstream JSON `_references` arrays.
- No client/named-vessel telemetry.
- Required: `scripts/legal/legal-sanity-scan.sh --diff-only` against the generated PNG/SVG/PDF before external send.

**Output formats:** PNG brochure, SVG print, PDF 1-page.

**Maps to issue ACs:** AC1 (≥3 brochure-ready charts — covers 3 jobs in one), AC2 (public-source disclosure), AC3 (legal-suitable framing), AC4 (feeds brochure without re-assembly).

---

### Chart C2 — Pipelay Operating Envelope (water depth × pipe size, by vessel)

**The "shallow water" wedge.** Pipelay-vessel contractors care most about the depth-vs-pipe-size operating window. This chart compares the Large PLV class against the Shallow Water Barge class on a single (water depth, pipe OD) plane, with go/marginal/no-go bands.

**Why it earns brochure space:** the PLV-vs-Barge crossover at ~7 m water depth is a concrete, defensible technical claim that separates ACE from a hand-wave consultancy pitch. The barge dominates ultra-shallow (100% pass rate); the PLV fails at 7 m for all sizes (vessel draft limit).

**Required data fields**
- vessel.name, vessel.tensioner_capacity_te, vessel.water_depth_range, vessel.pipe_capacity
- per (vessel × pipe size × water depth): GO / MARGINAL / NO_GO; limiting factor

**Data inputs**
- `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json`
- `digitalmodel/examples/demos/gtm/results/vessel_comparison_matrix.json` (`plv_comparison.head_to_head` block)

**Headline-number rule**
- Compute pass-rate ratio between barge and PLV in shallow water (≤30 m). As drafted today, the headline reads: **"Shallow Water Barge handles 8-24 in pipe at 7 m depth where the Large PLV cannot operate (vessel-draft limited)."**

**Verification scope (now vs later)**
- **Verified in this planning wave:** the cross-demo narrative and the Large PLV shallow-water limitation are directionally supported by the current comparison matrix and cited pipelay dataset.
- **Deferred to render slice:** the exact `8-24 in` and `7 m depth` phrasing must be recomputed from the latest demo 4 source/result files before export, because this planning wave did not exhaustively trace every plotted cell.

**Caption draft**
> Shallow-water S-lay envelope: where each vessel class can install which pipe size. Green cells indicate cases meeting tension, overbend, sagbend, and stinger checks per DNV-ST-F101 and API RP 1111. Marginal cells flag governing constraint within 5% of allowable. Source vessel parameters are representative-class — not exact specs of any named vessel. Detailed go/no-go for a specific project requires metocean, soil, and rigging inputs.

**Evidence & legal scope**
- Uses the same 2 representative-class vessels disclosed in source JSON.
- Limiting-factor labels (`tension`, `overbend`, `vessel_capability`) come directly from demo 4 results, not from interpretation.
- Legal-scan gate identical to C1.

**Output formats:** PNG brochure, SVG print, PDF 1-page.

**Maps to issue ACs:** AC1, AC2, AC3, AC4.

---

### Chart C3 — Crane-Utilisation Margin Map (lift jobs)

**The "we don't just say go/no-go, we tell you the headroom" chart.** Two-vessel comparison (Large CSV vs Medium CSV) showing crane utilisation % at 1500 m water depth for 50 / 100 / 200 te mudmats. Both vessels are GO across the matrix, but the utilisation deltas (Large CSV at 20.6% vs Medium CSV at 71.5% for 200 te) tell the operability story.

**Why it earns brochure space:** contractor decision-makers know "GO" doesn't mean "comfortable margin." This chart shows ACE doing what most screeners skip — surfacing the margin curve, not just the binary verdict.

**Required data fields**
- vessel.name, vessel.crane_main.swl_max_te, vessel.crane_main.crane_capacity_curve
- per vessel × structure: crane_util_at_1500m

**Data inputs**
- `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json`
- `digitalmodel/examples/demos/gtm/results/structure_comparison_matrix.json` (`by_vessel.*.crane_util_at_1500m`)

**Headline-number rule**
- Compute the largest utilisation delta between vessels for a single structure. As drafted today, the headline reads: **"At 200 te mudmat, 1500 m depth: Large CSV at 20.6% crane utilisation, Medium CSV at 71.5% — same go-decision, very different margin."**

**Verification scope (now vs later)**
- **Verified in this planning wave:** the intended metric source is locked to `structure_comparison_matrix.json` `by_vessel.*.crane_util_at_1500m`.
- **Deferred to render slice:** the exact utilisation percentages and the identity of the largest delta pair must be recomputed from the latest matrix before export.

**Caption draft**
> Crane-utilisation margin at 1500 m water depth for the 50 / 100 / 200 te mudmat installation cases. Both vessel classes pass go/no-go, but margin matters: lower utilisation reduces sensitivity to weight growth, rigging revisions, and weather stand-by. Vessel crane curves are representative-class. Per the DNV-RP-H103 dynamic amplification framework and the DNV-ST-N001 marine-operations governing-load envelope (both inherited from `csv_hlv_vessels.json` `_references`); full lift sensitivity requires project-specific RAO/sea-state inputs.

**Evidence & legal scope**
- Both vessels are representative-class; disclosure in source JSON.
- Utilisation values are direct demo 3 outputs, not interpretive.
- Legal-scan gate identical to C1.

**Output formats:** PNG brochure, SVG print, PDF 1-page.

**Maps to issue ACs:** AC1, AC2, AC3, AC4.

---

### Chart C4 — Capability Coverage Map (optional, recommended)

**The "what ACE is willing to take to screening today" chart.** A 17-row coverage map (cross-walked from `docs/gtm/capability-map.md`) showing for each discipline: production / available / planned readiness, demos / cases, and standards citations. Not vessel-vs-vessel — capability-vs-readiness instead.

**Why it earns brochure space:** answers the second question every contractor asks: "what else can you screen?"

**Required data fields**
- discipline name, module path, GTM demo, standards list, readiness, client-value text

**Data inputs**
- `docs/gtm/capability-map.md` (already produced)

**Headline-number rule**
- Headline reads: **"10 of 17 disciplines at production readiness today; 1,292 parametric cases across 5 demos."** (Source: lines 38-42 of capability-map.md.)

**Verification scope (now vs later)**
- **Verified in this planning wave:** the headline is sourced from the cited `docs/gtm/capability-map.md` lines.
- **Deferred to render slice:** re-check those counts against the latest capability map before brochure export in case readiness totals changed.

**Caption draft**
> ACE Engineer's screening-grade discipline coverage for offshore installation, integrity, and field-development scope. Production rows have parametric demos and traceable code-versus-code outputs ready for client review. Available rows have working modules without packaged demos. Planned rows have GitHub-tracked work with named dependencies. Per-discipline standards citations inherited from upstream.

**Evidence & legal scope**
- All entries cite repo paths and standards bodies; no client engagements claimed.
- No vessel-named telemetry.
- Legal-scan gate identical to C1.

**Output formats:** PNG brochure, SVG print, PDF 1-page (single-page summary).

**Maps to issue ACs:** AC4 primarily (brochure self-containment).

---

## Traceability Matrix (Issue ACs → Chart concepts)

| Issue #2555 AC | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| AC1 — ≥3 brochure-ready capability charts produced or planned with exact data inputs | ✓ | ✓ | ✓ | (optional) |
| AC2 — every chart has public-source/evidence notes or explicit assumption notes | ✓ | ✓ | ✓ | ✓ |
| AC3 — chart claims suitable for public-facing GTM collateral after legal/evidence sanity review | ✓ | ✓ | ✓ | ✓ |
| AC4 — outputs feed the brochure/send issue without requiring the user to reassemble context | ✓ | ✓ | ✓ | ✓ |

The C1+C2+C3 set alone covers all four ACs. C4 is added if brochure layout permits.

---

## Legal & Evidence Gate (binding)

Before any chart is exported for external use, all of the following must be true and recorded:

1. **Source provenance recorded** — chart's data-input paths cited in the export's accompanying caption/footnote.
2. **Public-vs-private inputs identified** — every data path is from `digitalmodel/examples/demos/gtm/**` (representative-class disclosure inherited) or `docs/gtm/capability-map.md`. No paths from `client_projects/`, `acma-projects/`, `seanation/`, `frontierdeepwater/`, or any private archive.
3. **Methodology and standards citations attached** — caption names DNV/API standards inherited from the JSON `_references`.
4. **Tests/review state known** — chart-render run cleanly; demo source data not regenerated since last cross-provider review.
5. **Legal scan run** — `scripts/legal/legal-sanity-scan.sh --diff-only` over the changed export files passes; output archived alongside the asset commit.
6. **No confidential/client-identifying content promoted** — automated check + manual eyeball before each send.

Provider-review readiness for this storyboard follows the paired plan: required evidence is Claude **and** Codex **and** Gemini live verdicts (each APPROVE or MINOR). UNAVAILABLE provenance documents a blocker (timestamp and blocking reason recorded in `scripts/review/results/2026-04-29-plan-2555-*.md`) but does NOT satisfy promotion for any of the three providers; the storyboard remains pre-promotion until canonical-fanout artifacts at `scripts/review/results/2026-04-29-plan-2555-{codex,gemini}.md` (no `-nextwave` suffix) carry live verdicts. Mirrors plan AC §209 ("Cross-provider adversarial review evidence...").

Per `docs/BUSINESS_BRAIN.md:122-132`, this gate is mandatory and cannot be waived for "small" sends.

---

## Operational Notes

- **Re-render trigger:** when any of the source JSONs change (typically a demo rerun), regenerate every chart and re-run the legal scan.
- **Brand alignment:** colour palette and typography must match the locked brand contract from #2426/2435 (per memory `project_claude_design_adoption`). Reconfirm against `aceengineer-website` brand assets before rendering.
- **Headline-number discipline:** only C1's `100% across 30 cases` pair is partially verified in this planning wave; every exact brochure headline must be recomputed against the latest source/result files during rendering, even when a draft number is quoted here.
- **Sibling handoff to #2556:** brochure-send agent reads this storyboard's chart inventory + caption drafts as the canonical chart spec. Headline-number values must be regenerated against the latest demo run before send, not copied from this draft.
- **Sibling handoff to #2554:** contractor recipient list determines whether the chart pack needs additional vessel classes. If recipients include contractors operating outside the 4 representative classes, escalate to #1799 before sending.

---

## Out of Scope (do not attempt under #2555)

- New vessel-class data ingestion → #1799.
- Brochure layout, copy, or send mechanics → #2556.
- Live website embed of charts → not requested by #2555 ACs.
- Per-client-project chart customisation → outside the public-collateral boundary.
- Editing `digitalmodel/` source code → explicitly forbidden by the #2555 plan rules.

```
