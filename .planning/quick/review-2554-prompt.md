# Adversarial Plan Review Request: workspace-hub #2554

## Role
You are an independent adversarial reviewer. Be skeptical. Find missing acceptance criteria, evidence gaps, public/private data risks, workflow-gate errors, and false readiness claims. Do not rubber-stamp.

## Context
This is part of the Business Brain / GTM vessel-contractor wave. The repository uses hard gates: Issue -> Plan -> Adversarial Review -> status:plan-review -> USER APPROVES -> status:plan-approved -> Implementation/TDD -> Verification -> Close.

The current move is planning/review-readiness only. No outreach should be sent, no private contact data should be added to public repo files, and `UNAVAILABLE` provider artifacts must not be counted as live non-Claude review evidence.

## Issue under review
- Issue: workspace-hub #2554
- Title: Vessel contractor outreach matrix review-readiness
- Review focus: evidence model, target prioritization, public/private boundary, provider-review gate, and whether the plan is ready for status:plan-review.

## Required output format
Start with exactly one line:
`Verdict: APPROVE|MINOR|MAJOR`

Then provide:
1. Summary rationale.
2. Severity-ranked findings grouped as CRITICAL/HIGH/MEDIUM/LOW.
3. Explicit answer: Is this ready for `status:plan-review`? Why or why not?
4. Exact must-fix patches if verdict is MAJOR or MINOR.
5. Any user inputs needed before downstream #2556 brochure/outbound work.

## Plan artifact: docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md

```markdown
# Plan for #2554: feat(gtm): weekly vessel contractor outreach matrix for April target

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2554
> **Review artifacts:** scripts/review/results/2026-04-29-plan-2554-claude.md | ...-codex.md | ...-gemini.md (PENDING — not yet generated)
> **Self-reference slug:** `2026-04-29-issue-2554-vessel-contractor-outreach-matrix`

---

## Resource Intelligence Summary

### Existing repo code / artifacts

- **Found:** `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` (139 lines, 2026-04-02) — three-step cold/follow-up/meeting outreach sequence with placeholder slots (`{{COMPANY}}`, `{{JOB_TITLE}}`, `{{PAIN_POINT_*}}`), Day 0/3/7 timing, A/B subject variants, and disqualification criteria. **Implication for #2554:** the matrix needs a per-target slot for `{{PAIN_POINT_1..3}}` derived from public fleet/project evidence, otherwise the templates render with stale generic copy.
- **Found:** `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (1015 lines, lane C2 output) — 10 buyer-segment briefs with `can-say-now` / `cannot-claim-yet` / `missing-proof` fields. Candidates 3, 4, and 5 are vessel-installation-segment (deepwater mudmat, shallow-water S-lay, rigid-jumper installation) and already carry shipped-demo evidence (`digitalmodel/examples/demos/gtm/demo_03|04|05_*.html`). **Implication:** the contractor matrix can adopt the eight-field brief template verbatim and inherit Demo 3/4/5 as the proof anchor for Tier-1 / Tier-2 vessel contractors.
- **Found:** `docs/gtm/capability-summary.md`, `docs/gtm/capability-map.md`, `docs/gtm/marine-terminal-engineering-scope.md`, `docs/gtm/fowt-engineering-scope.md` — capability framing already split by service line and adjacent segments. The contractor matrix should reference these via path, not re-author scope text.
- **Found:** Issue #1669 body (Apr 2) — pre-existing tier seed list (Tier-1 majors: Subsea7, TechnipFMC, Saipem, McDermott, Allseas, Heerema, Boskalis, Van Oord, DEME; Tier-2 specialists: DOF Subsea, Solstad, Bourbon, Sapura, EMAS/Ezra, Seaway7; Tier-3 niche: Helix, Superior Energy, DeepOcean, Gulf Offshore). **Implication:** the matrix takes #1669's tier list as the starting set and must reconcile (drop, retier, add) using the criteria below; #1669 has no evidence URLs attached to most names.
- **Found:** Issue #1799 body — pipelay barge spec collection target (Allseas Lorelay, Subsea 7 Seven Navica, Saipem Castorone, McDermott DB101, Sapura Constructor, Van Oord Stork, Boskalis lay barges). **Implication:** vessel-spec data anchors the "relevant fleet angle" column for ~7 contractors and is also a public-source seed for the matrix. #1799 itself is a separate data-collection issue — the matrix references its outputs without duplicating spec rows.
- **Found:** `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json` (referenced in Demo 3) — Large CSV (5,000 te) and Medium CSV (2,500 te) class-typical RAOs and crane envelopes. **Implication:** vessel matrix `relevant fleet angle` column should describe whether each contractor's flagship fits the demo's envelope or sits outside it, so outreach copy can claim defensibly.
- **Found:** `docs/gtm/intake/prospect-schema.json` (Draft-07 validated per #2346) — defines the YAML intake shape used to produce 48-hour custom demo reruns. **Implication:** the matrix `outreach priority` column should flag which contractors would be worth pre-staging an intake YAML for once their interest is confirmed.
- **Gap:** No existing single artifact merges (a) #1669 tier list, (b) public fleet evidence, (c) #1799 vessel-spec coverage, (d) per-target pain-point hypotheses, and (e) demo-anchor mapping into one outreach-ready matrix. `ls docs/reports/gtm/ 2>&1` returned "No such file or directory" — the target directory has to be created.
- **Gap:** No automated public/private boundary check exists for GTM matrices. `scripts/legal/legal-sanity-scan.sh --diff-only` exists per `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates" but has not yet been wired into a contractor-matrix promotion path.

### Standards

Not applicable. `cat:business`, `cat:strategy`, `domain:gtm`, `priority:high` — no engineering standards exercised, no calc constants emitted; `.claude/rules/calc-citation-contract.md` does not apply. `.claude/rules/coding-style.md` (relative paths, no hardcoded absolute paths in artifacts) and `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates for Public Artifacts" do apply.

### LLM Wiki pages consulted

- No wiki pages are direct inputs to this matrix. The matrix consumes public corporate fleet/project disclosures and the existing demo-derived proof paths. Wiki promotion of any contractor-specific synthesis is out of scope until a public-source-only methodology layer is approved separately (out-of-scope: legal sanity gate not yet run for vessel-contractor synthesis).

### Documents consulted

- Issue #2554 body — defines the deliverable shape (≥20 ranked targets, public evidence per target, public/private separation, follow-up issues for missing data) and ties scope back to #1669/#2016 and Demo 3/4/5 as proof anchors.
- Issue #1669 body — defines the seed tier list, the per-target prospect-list structure (`company / contact / title / email`), email-sequence cadence, value-prop angles, and Phase 1 / Phase 2 / Phase 3 decomposition. **The matrix in this plan is the Phase 1 "prospect list with company, segment/tier" deliverable, not the email send.**
- Issue #2016 body — parent GTM conversion umbrella; lists Tier-3 outreach sub-issues (#191, #117, #1669, #197) as blocked on demo readiness. With Demo 1–5 shipped (Apr 14), the demo-blocker on #1669 is now lifted, which is what makes #2554 actionable this week.
- Issue #1799 body — public pipelay-barge spec inventory; provides 7 vessel→operator mappings the matrix can reuse without re-research.
- `docs/BUSINESS_BRAIN.md` §"Interactive Weekly GTM Targets" (line 106-112) — confirms the April 1 weekly target is "produce vessel capability charts and send a good brochure to all researched vessel contractors". The matrix in this plan supplies the *researched-contractor* substrate that the brochure-send (#2556) consumes.
- `docs/BUSINESS_BRAIN.md` §"GTM-to-Code Readiness Loop" (lines 114-120) — confirms that public-facing GTM artifacts must carry source provenance and may not exceed repo-evidence claims. The matrix template includes evidence-URL and `can-say-now` columns to enforce this.
- `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates for Public Artifacts" (lines 122-132) — establishes that any client-derived or contact-list content must pass legal sanity before public promotion. **Decision in this plan:** the public matrix at `docs/reports/gtm/...` carries no individual contact details (titles, names, or emails). Per-target named contacts, if any, route to a private surface outside this repo.
- `docs/plans/_template-issue-plan.md` — the canonical template; this plan follows its section order and the embedded retrieval contract.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` (v3.1.0) — the planning workflow skill. Confirms draft → adversarial review → `status:plan-review` → user approval gating; no self-approval.
- `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/2554-contractor-matrix.md` (recovered from `git show HEAD:`) — the overnight task brief that scoped this work; explicitly forbids implementation code, email sends, and self-approval, and enforces public/private boundary preservation.
- Memory: `feedback_inline_gh_issue_url.md` — issue references must render as GitHub Markdown hyperlinks (`#2554` → `[#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554)`). Applied throughout this plan and the scaffold.
- Memory: `feedback_data_format_guidelines.md` — default to YAML for agent-facing structured data; Markdown for human-facing rendering. The scaffold ships as Markdown for review readability; a YAML companion is a follow-up if/when the matrix is consumed programmatically by a send pipeline.

### Gaps identified

- No reconciliation has been done between #1669's tier list and the live fleet/operator landscape since April 2. Matrix must mark tier moves explicitly (drop, retier, add).
- No per-target evidence URL set exists. Matrix scaffold ships with the URL columns and a coverage-target acceptance criterion (≥1 evidence URL per target before send).
- No documented mapping from contractor → relevant ACE demo (Demo 3/4/5) exists. Matrix scaffold introduces a `demo_anchor` column.
- No public/private boundary policy decision has been recorded for vessel-contractor outreach matrices specifically. Matrix scaffold and this plan establish the decision: public matrix carries `evidence_url` only; named contacts route privately.
- No "missing data" follow-up backlog has been opened. Acceptance criterion for the matrix execution phase requires opening per-row follow-up issues for any high-value target whose `outreach priority` is High but whose evidence URL coverage is insufficient.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29 via `gh issue view`):
- `#2554` — OPEN, `priority:high`, `cat:business`, `cat:strategy`, `domain:gtm` — feat(gtm): weekly vessel contractor outreach matrix for April target
- `#1669` — OPEN, `cat:business`, `cat:strategy`, `domain:gtm` — [WRK] GTM: Vessel Installation Contractor Email Outreach Campaign (parent campaign)
- `#2016` — OPEN, `priority:high`, `cat:business`, `cat:strategy`, `domain:gtm` — feat(gtm): client conversion pipeline -- turn repo capability into paying clients
- `#1799` — OPEN, `gtm` — DATA: Collect public pipelay barge/vessel specs for shallow water GTM demo

**File existence** (verified 2026-04-29):
- EXISTS: `docs/strategy/gtm/vessel-installation-contractors/email-templates.md`
- EXISTS: `docs/gtm/outreach-candidate-briefs-2026-04-28.md`
- EXISTS: `docs/gtm/capability-summary.md`, `docs/gtm/capability-map.md`
- EXISTS: `docs/plans/_template-issue-plan.md`, `docs/plans/README.md`
- EXISTS: `digitalmodel/examples/demos/gtm/demo_03_deepwater_mudmat_installation.py` (referenced by lane C2)
- MISSING (this plan creates): `docs/reports/gtm/` (parent dir), `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- MISSING (this plan creates): `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` (this file)

**Gap proofs**:
- `ls docs/reports/gtm/ 2>&1` → "No such file or directory" → confirms target directory does not exist; scaffold creation must include `mkdir -p`.
- `ls docs/strategy/gtm/vessel-installation-contractors/` → only `email-templates.md` (139 lines) → confirms there is no existing `prospect-list.md` to extend; matrix must be authored fresh.

<!-- Source count: issue body (#2554) + 5 sibling/parent issues (#1669/#2016/#1799/#2554/BUSINESS_BRAIN) + 6 repo file paths + 2 memory entries + plan template + planning skill = 16 distinct sources. Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` |
| Research scaffold | `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` |
| Plan review — Claude | `scripts/review/results/2026-04-29-plan-2554-claude.md` (pending) |
| Plan review — Codex | `scripts/review/results/2026-04-29-plan-2554-codex.md` (pending) |
| Plan review — Gemini | `scripts/review/results/2026-04-29-plan-2554-gemini.md` (pending) |
| Index update | `docs/plans/README.md` (one row appended) |
| Summary | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` |
| Existing reused | `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` (no edits) |
| Existing reused | `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (cross-linked) |
| Existing reused | `digitalmodel/examples/demos/gtm/demo_0[345]_*.html` (cited as demo anchors) |

---

## Deliverable

A repo-tracked vessel-contractor outreach matrix at `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` that ranks ≥20 vessel-installation contractors / operators by outreach fit, attaches at least one public evidence URL per target, maps each target to one or more shipped ACE demos as a proof anchor, and keeps individual contact details out of the public artifact — sufficient to feed the brochure-send lane (#2556) without re-research.

---

## Pseudocode

```
function build_contractor_matrix(seed_list, public_evidence_corpus, demo_anchors):
    targets = []
    for each seed in seed_list:                           # #1669 tier list
        candidate = {
            company: seed.company,
            tier_seed: seed.tier,                         # T1 / T2 / T3 from #1669
            tier_revised: null,                           # filled after evidence
            segment: null,                                # subsea install / pipelay / heavy-lift / wind / Gulf
            relevant_fleet: [],                           # public fleet refs
            demo_anchor: [],                              # Demo 3 / 4 / 5 / 6 / 7
            pain_point_hypothesis: null,                  # public-evidence-bounded
            pain_point_evidence: [],                      # public source or explicit demo-coverage inference
            corporate_root_evidence: [],                  # ≥1 official domain root required at plan-review
            deep_link_evidence: [],                       # official fleet/project/vessel page required before send
            can_say_now: [],                              # ACE-claim envelope
            cannot_claim_yet: [],                         # adjacent-claim guard
            outreach_priority: null,                      # High / Medium / Low / Defer
            private_data_route: null                      # never inline; pointer if exists
        }
        validate corporate_root_evidence is non-empty before promoting High priority in draft review
        require deep_link_evidence + pain_point_evidence before send-ready promotion
        validate no individual contact (name, title, email, phone) is present
        targets.append(candidate)

    rank(targets, key = (outreach_priority, demo_anchor_density, evidence_strength))
    drop targets with empty corporate_root_evidence and tier_seed = T3 (deferred to follow-up issue until official-domain proof exists)
    open follow-up issue per High-priority target with insufficient evidence

    return matrix  # markdown table + per-target brief blocks
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` | Primary deliverable — research scaffold |
| Create | `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` | This plan (canonical) |
| Update | `docs/plans/README.md` | Add Plan Index row pointing at the canonical plan |
| Create | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` | Lane summary for the overnight orchestrator |
| (Pending — execute-phase only) | `scripts/review/results/2026-04-29-plan-2554-{claude,codex,gemini}.md` | Adversarial review artifacts (Step 4) |

No production-code paths are touched. No edits to `digitalmodel/`, `assetutilities/`, or other Tier-1 repos. No edits to `docs/gtm/` (existing GTM corpus stays as-is and is referenced by path).

---

## Test List (research-artifact equivalent of TDD)

Because the deliverable is a research artifact rather than executable code, the test list below is a checklist of falsifiable, automatable assertions against the scaffold. Each row is a binary did/didn't check that must pass before `status:plan-review` can be requested.

| Check | What it verifies | How to execute |
|---|---|---|
| `count_targets ≥ 20` | Acceptance criterion #1 in #2554 | `grep -cE "^### Target [0-9]+ — " docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` |
| `each_target has ≥1 corporate-root evidence URL` | Acceptance criterion #2 at scaffold-review depth | per-target field `corporate_root_evidence:` non-empty (manual or grep-script) |
| `each live High-priority target has a deep-link backlog slot` | Corporate-root vs deep-link distinction is explicit | per-target field `deep_link_evidence:` present, even if marked `PENDING` in scaffold v1 |
| `each live target has pain-point evidence traceability` | Hypotheses are attributable, not freehand | per-target field `pain_point_evidence:` present |
| `no individual contact details inline` | Acceptance criterion #3 in #2554 + Legal Sanity Gate | `scripts/legal/legal-sanity-scan.sh --diff-only` returns clean for the new file |
| `each High-priority target has ≥1 demo anchor` | Outreach-readiness check (matrix usable for #2556) | per-target field `demo_anchor:` non-empty for `outreach_priority: High` |
| `tier_seed reconciliation is recorded` | Traceability to #1669 (no silent retiering) | each target's `tier_seed` and `tier_revised` fields both present |
| `cannot_claim_yet field is populated` | Inherits the proof-bounding contract from `outreach-candidate-briefs-2026-04-28.md` | per-target field `cannot_claim_yet:` non-empty |
| `follow-up issues opened for High + low-evidence` | Acceptance criterion #4 in #2554 | issue list at the bottom of the scaffold cross-links each filed issue |
| `high_priority_count_consistency` | Numeric count of High-priority rows agrees with the named list, both in the scaffold's Summary Counts block and in the lane-summary file | `grep -cE '\*\*outreach_priority\.\*\* \*\*High\*\*' docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` must equal the integer printed in the scaffold's "Targets in `outreach_priority: High`" bullet AND match the count printed in `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` |
| `provider fallback is documented without weakening gate order` | Review-readiness contract is explicit | AC text says `UNAVAILABLE` artifacts document a blocked provider but do not by themselves satisfy promotion |
| `public/private routing decision recorded` | Boundary policy applied per BUSINESS_BRAIN | scaffold header carries the explicit decision text |

These checks replace the standard `pytest` lines that would appear for an engineering plan. The acceptance criteria below restate them in user-facing form.

---

## Acceptance Criteria

- [ ] Scaffold lists at least 20 vessel-installation contractor or operator targets, each with `tier_seed`, `tier_revised`, `segment`, `outreach_priority`, and `demo_anchor` fields populated.
- [ ] Every live target has at least one official corporate-root evidence URL (`corporate_root_evidence:` non-empty), and High-priority rows carry an explicit `deep_link_evidence:` slot showing what still must be verified before send.
- [ ] No individual contact details (named persons, titles, direct emails, phone numbers) appear inline in the public artifact. The scaffold carries an explicit "private contact data routes outside this repo" note in its header.
- [ ] Each `outreach_priority: High` target maps to at least one shipped ACE demo (Demo 3, 4, or 5 as the immediate set; 6, 7 if/when shipped) under `demo_anchor:`.
- [ ] Review-routing contract is explicit: `status:plan-review` still requires Claude + at least one live non-Claude review at `scripts/review/results/2026-04-29-plan-2554-*.md`; if a provider is unavailable in a given wave, an `UNAVAILABLE` artifact is written at the same path family to document the blocked lane, but that fallback does not by itself satisfy promotion.
- [ ] Each live target carries a `pain_point_evidence:` slot that either cites a public source path / URL or explicitly says the current statement is an inference from demo coverage pending deeper public verification.
- [ ] High-priority count is consistent across artifacts: the integer printed in the scaffold's "Targets in `outreach_priority: High`" Summary Counts bullet equals the row-grep count (`grep -cE '\*\*outreach_priority\.\*\* \*\*High\*\*'` over the scaffold) AND equals the count printed in `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md`. A mismatch (e.g., scaffold body lists 10 but lane summary still says 9) is a blocker for `status:plan-review` and must be reconciled in the lane-summary file by a permitted lane before promotion. This gate exists explicitly because the 2026-04-29 next-wave Claude review found the scaffold body and lane summary diverged on this count; the plan-only patch lane that addressed the other MINOR findings was not authorized to edit the lane-summary artifact.
- [ ] Plan Index row exists in `docs/plans/README.md` reflecting the current plan status (`draft` until adversarial review lands, `plan-review` once it does).
- [ ] Lane summary at `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` records what shipped, what is blocked, and the exact next action for the user.
- [ ] No commits to production code paths (`digitalmodel/`, `assetutilities/`, etc.) and no email sends or external contacts initiated by this lane.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (next-wave self-review, 2026-04-29) | MINOR | (1) Test List row 1 grep `^### Target — ` is off-by-one separator vs. actual scaffold heading `^### Target N — `; literal pattern returns 0 instead of 22. (2) Internal inconsistency: scaffold §376 says 9 High-priority targets but the actual count is 10 (named list contains 10). (3) AC #5 unmet by any wave that lacks Codex+Gemini live evidence. (4) Pseudocode evidence-URL gate satisfied in letter (corporate-domain root) but not spirit (no deep-link verification). (5) `pain_point_hypothesis` rows lack a citable evidence slot. |
| Codex (next-wave) | UNAVAILABLE | Lane permission did not auto-approve fanout invocation; codex-cli 0.124.0 upstream regression also unverified on this host (`feedback_codex_cli_0_124_upstream_regression.md`). See `scripts/review/results/2026-04-29-plan-2554-nextwave-codex.md`. |
| Gemini (next-wave) | UNAVAILABLE | Lane permission did not auto-approve fanout invocation. See `scripts/review/results/2026-04-29-plan-2554-nextwave-gemini.md`. |

**Overall result:** PENDING — `status:plan-review` cannot be applied this wave. The review-routing contract remains: Claude + at least one live non-Claude review are required for promotion; `UNAVAILABLE` artifacts document blocked providers but do not satisfy the gate on their own. Plan stays `draft` until a later permitted wave lands Gemini or Codex evidence.

**Remaining patch tasks for the next permitted lane:**
- Drive a permitted-lane fanout that produces at least one of Codex/Gemini live verdicts so the unchanged promotion gate can be satisfied.
- Replace `deep_link_evidence: PENDING` placeholders in High-priority rows with verified official fleet/project/vessel links before any send-ready claim is made.
- Replace `pain_point_evidence:` inference placeholders with public fleet/project proof where available.

Revisions made based on review: fixed the target-heading grep pattern; corrected the evidence model to distinguish `corporate_root_evidence` vs. `deep_link_evidence`; added a required `pain_point_evidence` slot; clarified that `UNAVAILABLE` review artifacts document provider blockage but do not satisfy the live non-Claude review gate for `status:plan-review`. Subsequent plan-only patch lane (2026-04-29 next-wave autofeed, result file `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2554-20260429-1446.md`) added an explicit Test List + AC gate for High-priority count consistency across the scaffold body, scaffold Summary Counts block, and lane-summary file (Finding 2 of the next-wave Claude review). No outreach claims, contact data, or evidence URLs were invented; the gate is a structural consistency check only and any reconciliation of the lane-summary count from 9 → 10 must be performed by a permitted lane.

Review evidence: `scripts/review/results/2026-04-29-plan-2554-nextwave-{claude,codex,gemini}.md` (this wave); canonical-fanout artifacts at `…/2026-04-29-plan-2554-{claude,codex,gemini}.md` (no `-nextwave` suffix) reserved for a permitted-lane re-run.

---

## Risks and Open Questions

- **Risk:** the contractor matrix is only as defensible as its weakest evidence URL. If a shipped row cites a fleet page that goes dark or moves, the matrix decays. **Mitigation:** every URL is cited at extraction time with a fetch-date footnote in the scaffold; the matrix is designated a *snapshot* (dated filename) rather than a living index.
- **Risk:** the contractor list overlaps with corpus-confidential client-project data (Woodfibre, SESA per `outreach-candidate-briefs-2026-04-28.md` Candidate 6). **Mitigation:** the matrix scaffold scope is *vessel-installation contractors only*. Any LNG-terminal or FOWT crossover is explicitly deferred to the relevant capability scope notes (`docs/gtm/marine-terminal-engineering-scope.md`, `docs/gtm/fowt-engineering-scope.md`) and not duplicated.
- **Risk:** the brochure-send lane (#2556) depends on this matrix; if the matrix slips, #2555 capability charts and #2556 brochure both stall. **Mitigation:** the scaffold is producible from already-public information in this repo + #1669/#1799 seed sets without external research, so the artifact can ship inside a single planning session.
- **Risk:** sending outreach without a confirmed contact route is wasteful. **Mitigation:** `outreach_priority: High` is gated on having a private-route pointer recorded (e.g., LinkedIn search query, BD-ops handoff lane) even if the literal contact lives outside this repo.
- **Open:** is the OCS / Gulf of Mexico segment in scope at the same priority as the global Tier-1 majors? The seed in #1669 lists Helix, Superior, DeepOcean, Gulf Offshore as Tier-3; #2554 explicitly mentions "Gulf of Mexico/offshore adjacent work". The scaffold treats GoM-specialist contractors as a separate `segment: gulf-of-mexico-niche` flag with `outreach_priority: Medium` by default — flag for user confirmation during approval.
- **Open:** wind-installation-only contractors (DEME Offshore, Van Oord renewables arm, Cadeler) are inside the #1669 seed but ACE has no shipped FOWT installation demo yet — only a scope note (`fowt-engineering-scope.md`). The scaffold marks them `demo_anchor: scope-note-only` and defaults `outreach_priority: Medium` until the FOWT worked example (Candidate 7 in `outreach-candidate-briefs`) ships.

---

## Complexity: T2

**T2** — research-artifact deliverable spanning multiple files (plan, scaffold, README index update, lane summary), with falsifiable acceptance criteria and an adversarial review gate. No production code paths touched; no client-facing send executed by this lane. Classification follows the workspace-hub convention that "scope of artifacts touched + need for cross-review" determines complexity rather than line count.

```

## Supporting artifact: docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md

```markdown
# Vessel Contractor Outreach Matrix — Scaffold (2026-04-29)

> **Issue:** [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) — feat(gtm): weekly vessel contractor outreach matrix for April target
> **Parent campaign:** [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) — vessel installation contractor outreach
> **GTM umbrella:** [#2016](https://github.com/vamseeachanta/workspace-hub/issues/2016) — client conversion pipeline
> **Demo proof anchors:** Demo 3 (deepwater mudmat installation), Demo 4 (shallow-water S-lay), Demo 5 (deepwater rigid-jumper installation) — all shipped Apr 14
> **Authoring lane:** Claude planning/research worker, ace-linux-1, 2026-04-29
> **Status:** **scaffold v1 — not yet a send-ready list.** Per-target evidence is now split into `corporate_root_evidence` vs. `deep_link_evidence`, and `pain_point_evidence` is carried explicitly. High-priority rows currently satisfy only the corporate-root scaffold gate; deep-link confirmation, contact routing, and pain-point hardening remain matrix-fill execution work after plan approval.

---

## Public/Private Boundary Decision (mandatory header)

This artifact is **public repo-tracked content**.

- **In this file:** company names (already public), public segment / fleet category, official corporate-root evidence URLs, planned deep-link evidence slots, pain-point evidence slots, demo-anchor mappings, `can-say-now` / `cannot-claim-yet` envelopes, and outreach priority.
- **Not in this file:** named individual contacts, direct emails, phone numbers, LinkedIn URLs of named persons, BD-ops session notes, or any private-route data. Per-target private-routing pointers (e.g., "search LinkedIn for offshore-engineering-lead at [company]") are recorded *outside this repo* and referenced here only as `private_route: external` with no detail.
- **Legal sanity gate:** any future promotion of this file to a public-facing surface (aceengineer.com, brochure attachment, expert-network deck) must pass `scripts/legal/legal-sanity-scan.sh --diff-only` and a manual public/private boundary review, per `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates for Public Artifacts".

---

## How to read this matrix

Each target carries the eight-field contract used by `docs/gtm/outreach-candidate-briefs-2026-04-28.md`, adapted to a *contractor row* shape:

| Field | Purpose |
|---|---|
| `company` | Public corporate name |
| `tier_seed` | Tier from [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) (T1 / T2 / T3) |
| `tier_revised` | Tier after this scaffold's reconciliation |
| `segment` | Subsea install / pipelay / heavy-lift / wind install / IRM / Gulf-niche |
| `relevant_fleet` | Public vessel anchor (named in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) or [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed) |
| `demo_anchor` | Which ACE shipped demo speaks to this contractor's work |
| `pain_point_hypothesis` | Public-evidence-bounded — never invented |
| `pain_point_evidence` | Public source path/URL or explicit `inferred-from-demo-coverage` placeholder |
| `corporate_root_evidence` | Official corporate-domain anchor, required at scaffold-review depth |
| `deep_link_evidence` | Official fleet / project / vessel subpage to verify before send |
| `can_say_now` | Defensible ACE claim envelope for this contractor |
| `cannot_claim_yet` | Adjacent claims to flag in the proposal/disclaimer |
| `outreach_priority` | High / Medium / Low / Defer |
| `private_route` | `external` if a routing pointer exists privately; `none` otherwise |

**Evidence-handling note (anti-fabrication):** every `corporate_root_evidence` value below is an official corporate-domain anchor that any reader can verify resolves to the named company's site. `deep_link_evidence` is intentionally left as a planned verification slot unless an official fleet/project/vessel page has been confirmed. This avoids manufacturing URLs that may not match the live site while still making the missing proof surface explicit. `pain_point_evidence` is likewise separated so readers can distinguish public proof from current demo-coverage inference.

---

## Tier-1 — Major EPIC / Heavy-Lift / Subsea Installation Contractors

### Target 1 — Subsea7

- **company.** Subsea7 (UK / Norway / global)
- **tier_seed.** T1
- **tier_revised.** T1 (no change)
- **segment.** Subsea installation, deepwater EPIC, mooring / riser, rigid-jumper installation; renewables arm = Seaway7
- **relevant_fleet.** Seven Borealis (HLV — explicitly named in `outreach-candidate-briefs-2026-04-28.md` Candidate 3 demo input as a *class-typical* envelope), Seven Navica (PLV — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed)
- **demo_anchor.** Demo 3 (deepwater mudmat installation, CSV class-typical envelope), Demo 5 (rigid jumper installation), Demo 4 (S-lay screening — Seven Navica analogue)
- **pain_point_hypothesis.** Deepwater installation contractors face decision-cost pressure on go/no-go for marginal sea-states across the lift envelope; screening artifacts (180-case mudmat / 300-case jumper) reduce committee-review cycle time before a project-specific OrcaFlex run.
- **corporate_root_evidence.** https://www.subsea7.com/ (corporate root; fleet/project deep-links are matrix-fill work)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "We screened 180 deepwater mudmat installation cases against a Seven Borealis-class envelope overnight, and 300 rigid-jumper cases including a 50 mm tie-in alignment phase — both as auditable HTML." Source: `digitalmodel/examples/demos/gtm/output/demo_03_*.html`, `demo_05_*.html`.
- **cannot_claim_yet.** Vessel-specific RAOs; full DP envelope at landing; named-Subsea7-project case studies (we hold no such public license).
- **outreach_priority.** **High** — Tier-1 fit + named-vessel anchor in our shipped demo input.
- **private_route.** external (LinkedIn-routed; no detail in this repo).

### Target 2 — TechnipFMC (Subsea)

- **company.** TechnipFMC (US/UK/global; subsea installation segment)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Subsea EPIC, integrated subsea solutions (iEPCI), umbilical/flowline install
- **relevant_fleet.** Deep Energy (PLV), Coral do Atlantico (PLV) — named-vessel detail is matrix-fill work
- **demo_anchor.** Demo 4 (shallow-water S-lay — only the *concept* maps; deepwater PLV envelope sits outside Demo 4's water-depth set), Demo 1 (freespan VIV screening once the line is laid)
- **pain_point_hypothesis.** iEPCI workflows are sensitive to early concept-stage screening accuracy because rework downstream propagates across multiple disciplines; multi-code WT comparison + freespan screening at concept gate is high-leverage.
- **corporate_root_evidence.** https://www.technipfmc.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "DNV-ST-F101 / API RP 1111 / PD 8010-2 wall-thickness comparison across 72 cases for an 8″–20″ portfolio at concept stage."
- **cannot_claim_yet.** iEPCI integration depth; named-TechnipFMC project work; vessel-specific motion analysis without their RAOs.
- **outreach_priority.** **High** — Tier-1 fit; even without a vessel-anchored demo match, Demo 1 + Demo 2 are credible anchors.
- **private_route.** external.

### Target 3 — Saipem

- **company.** Saipem (Italy)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Subsea EPIC, pipelay (deep + shallow), heavy lift, drilling
- **relevant_fleet.** Castorone (PLV — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed; deep + shallow capable), FDS-2 HLV
- **demo_anchor.** Demo 4 (shallow-water S-lay — Castorone shallow envelope), Demo 3 (deepwater installation — FDS-2 analogue), Demo 5 (rigid-jumper)
- **pain_point_hypothesis.** Cross-water-depth fleet flexibility is a competitive lever; concept-stage screening that compares small-barge vs. larger-vessel feasibility frees engineering bandwidth on portfolio bidding.
- **corporate_root_evidence.** https://www.saipem.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "60-case shallow-water S-lay screening across 2 barge classes × 5 pipe sizes × 6 depths" (Demo 4); "180-case deepwater mudmat installation against Large-CSV / Medium-CSV envelopes" (Demo 3).
- **cannot_claim_yet.** Castorone-specific RAOs; named-Saipem project case studies.
- **outreach_priority.** **High**.
- **private_route.** external.

### Target 4 — McDermott International

- **company.** McDermott International (Houston)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Subsea EPIC, lay barge, GoM deepwater
- **relevant_fleet.** DB101 (lay barge — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed), Amazon (HLV), Lay Vessel 108
- **demo_anchor.** Demo 4 (S-lay shallow + transitional), Demo 5 (rigid jumper), Demo 1 (freespan/VIV)
- **pain_point_hypothesis.** GoM project economics + post-restructuring schedule pressure → screening artifacts that compress weeks of OrcaFlex pre-checks into hours align with internal cost discipline.
- **corporate_root_evidence.** https://www.mcdermott.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "60-case S-lay screening, including 8″–24″ pipe range, in self-contained HTML — no proprietary toolchain to install for inspection."
- **cannot_claim_yet.** Vessel-specific dynamics under DB101 RAOs; named-McDermott project work.
- **outreach_priority.** **High** — GoM proximity, named-vessel anchor in [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799).
- **private_route.** external.

### Target 5 — Allseas

- **company.** Allseas Group (Switzerland / Netherlands)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Pipelay (S-lay + J-lay), heavy lift (Pioneering Spirit single-lift), decommissioning
- **relevant_fleet.** Pioneering Spirit, Lorelay (PLV — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed), Solitaire, Audacia
- **demo_anchor.** Demo 4 (S-lay screening), Demo 1 (freespan VIV after lay)
- **pain_point_hypothesis.** Allseas operates on the largest single-lift / longest pipelay envelopes in the industry; the differentiator at concept stage is *defensible engineering audit trail* per the citation contract — methodology messaging may resonate more than capacity messaging.
- **corporate_root_evidence.** https://allseas.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Every numeric in the screening report cites the code clause it came from." Methodology proof: `.claude/rules/calc-citation-contract.md` + `digitalmodel/src/digitalmodel/citations/schema.py`.
- **cannot_claim_yet.** Pioneering-Spirit-class single-lift dynamics; vessel-specific motion analysis.
- **outreach_priority.** **High**.
- **private_route.** external.

### Target 6 — Heerema Marine Contractors

- **company.** Heerema Marine Contractors (Netherlands)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Heavy lift (Sleipnir, Thialf), subsea installation, decommissioning
- **relevant_fleet.** Sleipnir, Thialf, Aegir
- **demo_anchor.** Demo 3 (deepwater mudmat installation, HLV envelope analogue), Demo 5 (rigid jumper)
- **pain_point_hypothesis.** Heavy-lift schedule cost is dominated by weather-window risk; screening that resolves go/amber/red across mudmat sizes × Hs envelopes maps directly to operability decisions.
- **corporate_root_evidence.** https://www.heerema.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "180-case mudmat install screening across 5 Hs values per case — overnight HTML report."
- **cannot_claim_yet.** Sleipnir-/Thialf-specific RAOs; HLV-specific DP envelope.
- **outreach_priority.** **High**.
- **private_route.** external.

### Target 7 — Boskalis (Subsea Services)

- **company.** Royal Boskalis Westminster (Netherlands) — Subsea Services / Offshore Energy
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Subsea installation, lay support, dredging-adjacent install
- **relevant_fleet.** Boskalis lay barges (named in [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed), heavy-transport vessels
- **demo_anchor.** Demo 4 (shallow / transitional S-lay), Demo 3 (mudmat install)
- **pain_point_hypothesis.** Cross-segment fleet (subsea + dredging + heavy-transport) → buyer often evaluates marginal-economics fields where small-barge feasibility is the decision driver.
- **corporate_root_evidence.** https://boskalis.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Shallow-water S-lay screening with overbend / sagbend / tension / stinger-departure outputs in a single HTML."
- **cannot_claim_yet.** Boskalis-specific vessel motion data.
- **outreach_priority.** **High**.
- **private_route.** external.

### Target 8 — Van Oord

- **company.** Van Oord (Netherlands)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Offshore wind installation (cable + foundation + turbine), dredging-adjacent
- **relevant_fleet.** Aeolus (wind installation), Bokalift class, Stork (shallow-water lay — [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed)
- **demo_anchor.** Demo 4 (S-lay shallow envelope, Stork analogue); FOWT segment is currently scope-note-only (`docs/gtm/fowt-engineering-scope.md`) — no shipped FOWT demo.
- **pain_point_hypothesis.** Wind installation differs from oil-and-gas; ACE messaging needs explicit "what transfers and what doesn't" to be credible (covered by the FOWT scope note).
- **corporate_root_evidence.** https://www.vanoord.com/ (corporate root)
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Shallow-water lay screening for the Stork-class envelope" (Demo 4); "explicit boundary on what oil-and-gas mooring expertise transfers to floating wind" (FOWT scope note).
- **cannot_claim_yet.** Full IEC 61400-3 DLC execution; coupled aero-hydro-servo-elastic time-domain; certification-grade output.
- **outreach_priority.** **Medium** — wind segment best contacted *after* the FOWT worked example (OC4-DeepCwind 1-pager, `outreach-candidate-briefs-2026-04-28.md` §4.3) ships. Pipelay segment can lead today.
- **private_route.** external.

### Target 9 — DEME Offshore

- **company.** DEME Group, Offshore arm (Belgium)
- **tier_seed.** T1
- **tier_revised.** T1
- **segment.** Offshore wind installation, heavy lift, cable lay
- **relevant_fleet.** Orion (HLV, wind-tuned), Living Stone (cable lay)
- **demo_anchor.** scope-note-only — FOWT lane not shipped; Demo 3 deepwater mudmat envelope partially analogous for foundation install
- **pain_point_hypothesis.** Wind-foundation install is operability-window-bound; Hs / period sensitivity screening at concept stage is the core decision aid.
- **corporate_root_evidence.** https://www.deme-group.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Hs sensitivity sweep across mudmat sizes and water depths" (Demo 3 transferable framing).
- **cannot_claim_yet.** Wind-foundation-specific dynamics; named-DEME project work.
- **outreach_priority.** **Medium** (defer until FOWT worked example ships).
- **private_route.** external.

---

## Tier-2 — Specialist / Mid-Tier Installation & Subsea Operators

### Target 10 — DOF Group (DOF Subsea + Solstad merger)

- **company.** DOF Group (Norway / global) — combined post-merger entity (DOF + Solstad)
- **tier_seed.** T2 (DOF Subsea, Solstad listed separately in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669))
- **tier_revised.** T2 (consolidated row; Solstad collapsed into this entry)
- **segment.** Subsea CSV / IMR / IRM
- **relevant_fleet.** Skandi-class subsea CSVs (multiple)
- **demo_anchor.** Demo 5 (rigid-jumper installation), Demo 3 (mudmat install)
- **pain_point_hypothesis.** IMR-cycle vessel utilization is the operating lever; screening that compresses concept analysis time on a tie-in candidate increases the count of bid-able opportunities per quarter.
- **corporate_root_evidence.** https://dofgroup.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "300-case rigid-jumper install screening — including the 50 mm tie-in alignment phase."
- **cannot_claim_yet.** Skandi-class-specific RAOs; named-DOF project work.
- **outreach_priority.** **High** — Tier-2 fit, named-segment match.
- **private_route.** external.

### Target 11 — Bourbon Offshore

- **company.** Bourbon Maritime (France)
- **tier_seed.** T2
- **tier_revised.** T2
- **segment.** Subsea support, IMR, OSV
- **relevant_fleet.** Bourbon Evolution series (CSV / IMR)
- **demo_anchor.** Demo 5 (rigid jumper), Demo 3 (mudmat install)
- **pain_point_hypothesis.** Mid-tier fleet operators bid against majors on cost; anything that strengthens engineering rigor without buying tooling is a margin lever.
- **corporate_root_evidence.** https://www.bourbon-online.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Self-contained HTML reports — your engineers spot-check the calc surface without installing proprietary toolchains" (Demo 4 framing applies broadly).
- **cannot_claim_yet.** Vessel-specific RAOs; named-Bourbon project work.
- **outreach_priority.** **Medium**.
- **private_route.** external.

### Target 12 — Sapura Energy

- **company.** Sapura Energy Berhad (Malaysia)
- **tier_seed.** T2
- **tier_revised.** T2
- **segment.** SE Asia subsea EPIC, pipelay, drilling
- **relevant_fleet.** Sapura Constructor ([#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) seed), Sapura Onix
- **demo_anchor.** Demo 4 (shallow-water S-lay), Demo 1 (freespan VIV)
- **pain_point_hypothesis.** SE Asia marginal-economics fields favor barge classes where Demo 4's "Can a smaller barge do this without departure-angle pain?" question is the decision driver.
- **corporate_root_evidence.** https://www.sapuraenergy.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Shallow-water S-lay screening — barge selection across pipe size and water depth."
- **cannot_claim_yet.** Sapura-Constructor-specific dynamics; named-Sapura project work.
- **outreach_priority.** **High** (named-vessel anchor in [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799)).
- **private_route.** external.

### Target 13 — Seaway7 (Subsea7 Renewables)

- **company.** Seaway7 (subsidiary of Subsea7)
- **tier_seed.** T2
- **tier_revised.** T2 (deduplicated against Subsea7 row; renewables-segment-specific)
- **segment.** Offshore wind installation (foundation + cable)
- **relevant_fleet.** Seaway Strashnov, Seaway Yudin
- **demo_anchor.** scope-note-only (FOWT lane not shipped)
- **pain_point_hypothesis.** Same FOWT-credibility problem as Target 8 — explicit transfer-and-gap framing is the lead, not capacity claims.
- **corporate_root_evidence.** https://www.seaway7.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Mooring concept screening at pre-FEED level using the same OrcaFlex workflow as deepwater oil-and-gas mooring — with explicit gaps vs. IEC DLCs flagged" (FOWT scope note).
- **cannot_claim_yet.** Coupled aero-hydro-servo-elastic verification; certification-grade output.
- **outreach_priority.** **Medium** (defer until FOWT worked example ships).
- **private_route.** external.

### Target 14 — Cadeler

- **company.** Cadeler A/S (Denmark)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added here as 2026-current wind-segment leader)
- **tier_revised.** T2 (new entry)
- **segment.** Offshore wind installation (turbine install)
- **relevant_fleet.** Wind Orca, Wind Osprey, NextGenerator class (under build)
- **demo_anchor.** scope-note-only
- **pain_point_hypothesis.** Pure-play wind installation operator; messaging must be 100% wind-credibility-anchored.
- **corporate_root_evidence.** https://www.cadeler.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** Defer outreach until FOWT worked example ships; today's claim is "we have a published scope note explicit about what does/doesn't transfer".
- **cannot_claim_yet.** Any oil-and-gas demo as the lead; turbine-specific dynamics.
- **outreach_priority.** **Defer** (logged here so subsequent runs do not re-add).
- **private_route.** none yet.

### Target 15 — Helix Energy Solutions

- **company.** Helix Energy Solutions (Houston)
- **tier_seed.** T3 ("Cal Dive (now Helix)")
- **tier_revised.** T2 (well-intervention-major; retiered up given GoM relevance)
- **segment.** Well intervention, IRM, decommissioning
- **relevant_fleet.** Q4000, Q5000, Q7000, Siem Helix 1
- **demo_anchor.** Demo 5 (rigid jumper — tie-in to existing infrastructure is intervention-adjacent), Demo 3 (mudmat install for new infrastructure)
- **pain_point_hypothesis.** Intervention scopes hinge on tie-in alignment and re-entry tolerances; Demo 5's 50 mm tie-in alignment phase is a direct conversation hook.
- **corporate_root_evidence.** https://www.helixesg.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "300-case rigid-jumper install screening including the 50 mm tie-in alignment phase, which is where day-rate bleed actually happens."
- **cannot_claim_yet.** Q-class-specific RAOs; named-Helix project work; well-intervention dynamics specifically.
- **outreach_priority.** **High** (GoM proximity + tie-in alignment hook).
- **private_route.** external.

---

## Tier-3 — Niche / Regional / IRM Operators

### Target 16 — DeepOcean Group

- **company.** DeepOcean Group (Norway)
- **tier_seed.** T3
- **tier_revised.** T3
- **segment.** IRM, subsea services, decommissioning
- **relevant_fleet.** Multiple subsea CSVs (Edda Fauna, Edda Flora class — public)
- **demo_anchor.** Demo 5 (rigid jumper), Demo 3 (mudmat install)
- **pain_point_hypothesis.** IRM operators run high-cycle workflows where engineering-screening rigor compounds across many small jobs.
- **corporate_root_evidence.** https://www.deepoceangroup.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Self-contained HTML screening reports — overnight turnaround, code-clause-cited."
- **cannot_claim_yet.** DeepOcean-vessel-specific dynamics; named-DeepOcean project work.
- **outreach_priority.** **Medium**.
- **private_route.** external.

### Target 17 — Jan De Nul

- **company.** Jan De Nul Group (Belgium / Luxembourg)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added for crossover dredging + offshore install)
- **tier_revised.** T3 (new entry)
- **segment.** Heavy installation, dredging crossover, offshore wind
- **relevant_fleet.** Voltaire (jack-up wind installation, public)
- **demo_anchor.** scope-note-only (wind segment) + Demo 4 (shallow-water lay framing)
- **pain_point_hypothesis.** Cross-segment buyer; wind-credibility framing required.
- **corporate_root_evidence.** https://www.jandenul.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Concept-stage screening + explicit transfer-and-gap framing for offshore wind work."
- **cannot_claim_yet.** Voltaire-specific dynamics; named-JDN project work; full IEC DLC.
- **outreach_priority.** **Medium**.
- **private_route.** external.

### Target 18 — Eidesvik Offshore

- **company.** Eidesvik Offshore (Norway)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added as Norwegian subsea / OSV niche)
- **tier_revised.** T3
- **segment.** Subsea support, OSV, IRM
- **relevant_fleet.** Subsea / IMR fleet (public)
- **demo_anchor.** Demo 5 (rigid jumper)
- **pain_point_hypothesis.** Mid-tier Norwegian operator competing on engineering rigor + utilization.
- **corporate_root_evidence.** https://www.eidesvik.no/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** Same as Target 16.
- **cannot_claim_yet.** Eidesvik-vessel-specific dynamics.
- **outreach_priority.** **Low** (audience saturation may be high for this segment).
- **private_route.** none yet.

### Target 19 — Acteon Group

- **company.** Acteon Group (UK; mooring, geosciences, IRM brands)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added for mooring/anchor expertise crossover)
- **tier_revised.** T3
- **segment.** Mooring services, anchor design, IRM
- **relevant_fleet.** N/A — services brand, not a fleet operator (consumed by us as adjacent expertise / partner candidate)
- **demo_anchor.** Mooring messaging via `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` + DNV-OS-E301 citation pilot; FOWT scope note.
- **pain_point_hypothesis.** Mooring-services brand → ACE methodology message (citation contract + multi-AI cross-review) may resonate as differentiation against incumbent toolchains.
- **corporate_root_evidence.** https://acteon.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Every standards-derived numeric carries a citation back to the code clause; multi-AI cross-review is standard pre-merge step."
- **cannot_claim_yet.** Anchor-specific design depth (out-of-scope today).
- **outreach_priority.** **Medium** (methodology-led, partner-shape, not a vessel-fleet target).
- **private_route.** none yet.

### Target 20 — Otto Candies LLC

- **company.** Otto Candies LLC (US Gulf, Louisiana)
- **tier_seed.** (not in [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed — added as GoM-niche per [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) "Gulf of Mexico/offshore adjacent work")
- **tier_revised.** T3
- **segment.** OSV / GoM marine, MPSV, ROV-support
- **relevant_fleet.** Public fleet pages (matrix-fill work to confirm vessel detail)
- **demo_anchor.** Demo 3 (mudmat install, GoM proximity)
- **pain_point_hypothesis.** Gulf-niche operator economics are utilization-driven; methodology messaging may be over-tooled relative to ICP.
- **corporate_root_evidence.** https://www.ottocandies.com/
- **deep_link_evidence.** PENDING — verify official fleet/project/vessel subpage before send; scaffold v1 intentionally stops at the corporate root.
- **pain_point_evidence.** `inferred-from-demo-coverage` for scaffold v1; replace with public fleet/project/source proof before send.
- **can_say_now.** "Concept-stage screening on a Gulf-relevant water-depth envelope."
- **cannot_claim_yet.** GoM-specific weather-window data; named-Candies project work.
- **outreach_priority.** **Low** (ICP fit uncertain; flag for user confirmation).
- **private_route.** none yet.

### Target 21 — Solstad Offshore (legacy, now DOF)

- **company.** Solstad Offshore (now consolidated into DOF Group post-merger; retained here as named-vessel anchor)
- **tier_seed.** T2
- **tier_revised.** **Deprecated — collapse into Target 10 (DOF Group).** Listed here so the next reader does not re-add as a separate row.
- **outreach_priority.** **Defer** (treated under Target 10).

### Target 22 — EMAS / Ezra Holdings (legacy)

- **company.** EMAS Energy / Ezra Holdings (Singapore; restructured 2017+; assets dispersed across PaxOcean and other operators)
- **tier_seed.** T2
- **tier_revised.** **Deprecated — restructured entity.** Listed here per [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) seed; no longer a coherent outreach target. The named lay-vessel asset family flagged in [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) ("EMAS/Ezra type barges") routes to whichever current operator now holds the hull.
- **outreach_priority.** **Defer**. Follow-up: open a research issue to map ex-EMAS hulls to current operators if the GoM/SE Asia barge segment becomes a focus lane.

---

## Summary Counts

- **Total target rows:** 22 (≥ 20 required by [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) acceptance criterion #1).
- **Live targets (priority High / Medium / Low):** 19. Deprecated/deferred: 3 (Solstad, EMAS, Cadeler-deferred).
- **Targets with at least one shipped-demo anchor:** 17 of 19 live (Demo 3 / 4 / 5 mapping).
- **Targets in `outreach_priority: High`:** 10 (Subsea7, TechnipFMC, Saipem, McDermott, Allseas, Heerema, Boskalis, DOF Group, Sapura Energy, Helix). Each carries a named-vessel anchor and a demo-mapping.
- **High-priority evidence state:** 10 of 10 currently have `corporate_root_evidence`, `deep_link_evidence`, and `pain_point_evidence` fields present; all 10 still require replacement of scaffold placeholders with verified public deep links / pain-point proof before send.
- **Targets in `outreach_priority: Medium`:** 7 (Van Oord, DEME, Bourbon, Seaway7, DeepOcean, Jan De Nul, Acteon).
- **Targets in `outreach_priority: Low`:** 2 (Eidesvik, Otto Candies).
- **Targets in `outreach_priority: Defer`:** 3.

---

## Matrix-Fill Execution Backlog (follow-up issues to open)

Per [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) acceptance criterion #4, follow-up issues should be opened for high-value targets with insufficient evidence depth before the brochure-send lane ([#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556)) consumes this matrix. **The lane that produced this scaffold has issue-mutation permissions but is electing not to open issues until the user reviews the matrix structure**, to avoid creating issues against a draft that may pivot during review.

Recommended issues to file after user review:

1. **Per-target deep-link verification.** For each High-priority target: confirm fleet/project deep-link URLs, vessel datasheet pages, and any current public project announcements. Output: keep `corporate_root_evidence` as the official-domain anchor, fill `deep_link_evidence` with verified public subpages, and add fetch-date footnotes.
2. **FOWT worked example unblock.** Targets 8 (Van Oord), 9 (DEME), 13 (Seaway7), 14 (Cadeler), 17 (JDN-wind) are blocked on the OC4-DeepCwind FOWT mooring screening 1-pager (`outreach-candidate-briefs-2026-04-28.md` §4.3). Open issue: "feat(gtm): FOWT mooring screening worked example — OC4-DeepCwind reference geometry, 1-pager output".
3. **Ex-EMAS hull mapping.** If the SE Asia / Gulf small-barge segment becomes a focus lane, file a research issue: "DATA: map ex-EMAS / Ezra hulls to current operators (2017+ restructuring)".
4. **GoM-niche ICP confirmation.** Targets 15 (Helix), 20 (Otto Candies) sit in the GoM niche segment. If the user confirms GoM is in scope at High priority, file a research issue to expand GoM-niche coverage (Hornbeck, Edison Chouest, Tidewater) before the next iteration of this matrix.

---

## Cross-References

- **Email templates:** `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` — three-step Day 0/3/7 sequence with placeholder slots that this matrix's `pain_point_hypothesis` field is designed to fill.
- **Capability framing:** `docs/gtm/capability-summary.md`, `docs/gtm/capability-map.md`.
- **Buyer-segment briefs (deeper proof paths):** `docs/gtm/outreach-candidate-briefs-2026-04-28.md` Candidates 3 / 4 / 5 (vessel-installation segment) and Candidate 8 (methodology lane).
- **Adjacent segment scope notes (out-of-scope-for-this-matrix but referenced):** `docs/gtm/marine-terminal-engineering-scope.md` (LNG terminals), `docs/gtm/fowt-engineering-scope.md` (floating wind).
- **Demo proof anchors:** `digitalmodel/examples/demos/gtm/output/demo_03_mudmat_installation_report.html`, `demo_04_shallow_pipelay_report.html`, `demo_05_jumper_installation_report.html`.
- **Vessel-spec data dependency:** [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) (pipelay barge specs collection) — provides spec depth for Targets 1, 3, 4, 5, 7, 12.

---

## Authoring Honesty Footnote

Built from public-corpus sources only:

- [#1669](https://github.com/vamseeachanta/workspace-hub/issues/1669) tier seed list (publicly known company names).
- [#1799](https://github.com/vamseeachanta/workspace-hub/issues/1799) public vessel inventory.
- `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (already-public proof framing).
- Each `corporate_root_evidence` value is an official-domain root the reader can verify; `deep_link_evidence` and `pain_point_evidence` are separated so missing proof is visible instead of implied.

No private contact data, client-derived information, or unverified deep-links were inserted into this scaffold. Live deep-link confirmation, contact-route discovery, and pain-point hardening are matrix-fill execution work tracked in the backlog above.

```
