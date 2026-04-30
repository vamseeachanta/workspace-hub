# Plan for #2554: feat(gtm): weekly vessel contractor outreach matrix for April target

> **Status:** blocker-remediation patch applied; pending fresh r2 adversarial re-review (not approval-ready)
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2554
> **Review artifacts:** r1 post-fill review at `scripts/review/results/2026-04-30-plan-2554-{claude,codex,gemini,disagreement}.md` returned MAJOR; r2 required at `scripts/review/results/2026-04-30-plan-2554-r2-{claude,codex,gemini,synthesis}.md` before `status:plan-review`.
> **Self-reference slug:** `2026-04-29-issue-2554-vessel-contractor-outreach-matrix`

---

## Resource Intelligence Summary

### Existing repo code / artifacts

- **Found:** `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` (138 lines, 2026-04-02) — three-step cold/follow-up/meeting outreach sequence with placeholder slots (`{{COMPANY}}`, `{{JOB_TITLE}}`, `{{PAIN_POINT_*}}`), Day 0/3/7 timing, A/B subject variants, and disqualification criteria. **Implication for #2554:** the matrix needs a per-target slot for `{{PAIN_POINT_1..3}}` derived from public fleet/project evidence, otherwise the templates render with stale generic copy.
- **Found:** `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (1014 lines, lane C2 output) — 10 buyer-segment briefs with `can-say-now` / `cannot-claim-yet` / `missing-proof` fields. Candidates 3, 4, and 5 are vessel-installation-segment (deepwater mudmat, shallow-water S-lay, rigid-jumper installation). **Implication:** the contractor matrix can adopt the eight-field brief template and use Demo 3/4/5 as conceptual proof anchors, but the plan no longer treats missing demo-output files as existing local artifacts.
- **Found:** `docs/gtm/capability-summary.md`, `docs/gtm/capability-map.md`, `docs/gtm/marine-terminal-engineering-scope.md`, `docs/gtm/fowt-engineering-scope.md` — capability framing already split by service line and adjacent segments. The contractor matrix should reference these via path, not re-author scope text.
- **Found:** Issue #1669 body (Apr 2) — pre-existing tier seed list (Tier-1 majors: Subsea7, TechnipFMC, Saipem, McDermott, Allseas, Heerema, Boskalis, Van Oord, DEME; Tier-2 specialists: DOF Subsea, Solstad, Bourbon, Sapura, EMAS/Ezra, Seaway7; Tier-3 niche: Helix, Superior Energy, DeepOcean, Gulf Offshore). **Implication:** the matrix takes #1669's tier list as the starting set and must reconcile (drop, retier, add) using the criteria below; #1669 has no evidence URLs attached to most names.
- **Found:** Issue #1799 body — pipelay barge spec collection target (Allseas Lorelay, Subsea 7 Seven Navica, Saipem Castorone, McDermott DB101, Sapura Constructor, Van Oord Stork, Boskalis lay barges). **Implication:** vessel-spec data anchors the "relevant fleet angle" column for ~7 contractors and is also a public-source seed for the matrix. #1799 itself is a separate data-collection issue — the matrix references its outputs without duplicating spec rows.
- **Not found at this workspace-hub HEAD:** `digitalmodel/examples/demos/gtm/data/csv_hlv_vessels.json` and `digitalmodel/examples/demos/gtm/demo_03|04|05_*` output files. **Implication:** the #2554 matrix may use Demo 3/4/5 only as internal/conceptual GTM anchors inherited from the briefs; #2556 or any send-ready artifact must not claim local demo-file proof unless those artifacts are restored or replaced by a committed proof path.
- **Found:** `docs/gtm/intake/prospect-schema.json` (Draft-07 validated per #2346) — defines the YAML intake shape used to produce 48-hour custom demo reruns. **Implication:** the matrix `outreach priority` column should flag which contractors would be worth pre-staging an intake YAML for once their interest is confirmed.
- **Gap:** No existing single artifact merges (a) #1669 tier list, (b) public fleet evidence, (c) #1799 vessel-spec coverage, (d) per-target pain-point hypotheses, and (e) demo-anchor mapping into one outreach-ready matrix. `ls docs/reports/gtm/ 2>&1` returned "No such file or directory" — the target directory has to be created.
- **Gap:** No automated public/private boundary check exists for GTM matrices. `scripts/legal/legal-sanity-scan.sh --diff-only` exists per `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates", but `--diff-only` can false-pass after files are committed. This plan therefore requires a targeted committed-artifact scan recorded at `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md`.

### Standards

Not applicable. `cat:business`, `cat:strategy`, `domain:gtm`, `priority:high` — no engineering standards exercised, no calc constants emitted; `.claude/rules/calc-citation-contract.md` does not apply. `.claude/rules/coding-style.md` (relative paths, no hardcoded absolute paths in artifacts) and `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates for Public Artifacts" do apply.

### LLM Wiki pages consulted

- No wiki pages are direct inputs to this matrix. The matrix consumes public corporate fleet/project disclosures and demo-concept anchors from existing GTM briefs; missing local demo-output files are not treated as proof paths for promotion. Wiki promotion of any contractor-specific synthesis is out of scope until a public-source-only methodology layer is approved separately (out-of-scope: legal sanity gate not yet run for vessel-contractor synthesis).

### Documents consulted

- Issue #2554 body — defines the deliverable shape (≥20 ranked targets, public evidence per target, public/private separation, follow-up issues for missing data) and ties scope back to #1669/#2016 and Demo 3/4/5 as proof anchors.
- Issue #1669 body — defines the seed tier list, the per-target prospect-list structure (`company / contact / title / email`), email-sequence cadence, value-prop angles, and Phase 1 / Phase 2 / Phase 3 decomposition. **The matrix in this plan is the Phase 1 "prospect list with company, segment/tier" deliverable, not the email send.**
- Issue #2016 body — parent GTM conversion umbrella; lists Tier-3 outreach sub-issues (#191, #117, #1669, #197) as blocked on demo readiness. The GTM brief treats Demo 1–5 as the conceptual unblocker for #1669; because local demo-output files are not present at this workspace-hub HEAD, #2554 uses those only as internal matrix anchors and does not authorize send-ready demo-proof claims.
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
- NOT FOUND at this workspace-hub HEAD: `digitalmodel/examples/demos/gtm/demo_03_deepwater_mudmat_installation.py` and Demo 3/4/5 HTML outputs; treat demo anchors as conceptual until a committed proof path is restored
- MISSING (this plan creates): `docs/reports/gtm/` (parent dir), `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- MISSING (this plan creates): `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` (this file)

**Gap proofs**:
- Historical creation proof: `docs/reports/gtm/` did not exist before the scaffold lane; it now exists and contains the #2554 matrix plus this blocker-removal validation artifact.
- `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` is the reusable template source; there is still no public prospect-list artifact with individual contacts to extend, and this matrix intentionally keeps contact data out of repo.

<!-- Source count: issue body (#2554) + 5 sibling/parent issues (#1669/#2016/#1799/#2554/BUSINESS_BRAIN) + 6 repo file paths + 2 memory entries + plan template + planning skill = 16 distinct sources. Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` |
| Research scaffold | `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` |
| r1 post-fill review — Claude | `scripts/review/results/2026-04-30-plan-2554-claude.md` (MAJOR) |
| r1 post-fill review — Codex | `scripts/review/results/2026-04-30-plan-2554-codex.md` (MAJOR) |
| r1 post-fill review — Gemini | `scripts/review/results/2026-04-30-plan-2554-gemini.md` (MAJOR; contains sandbox/path-access false positives to be guarded by r2 inline package) |
| Index update | `docs/plans/README.md` (one row appended) |
| Summary | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` |
| Existing reused | `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` (no edits) |
| Existing reused | `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (cross-linked) |
| Required r2 review | `scripts/review/results/2026-04-30-plan-2554-r2-{claude,codex,gemini,synthesis}.md` |
| Legal/privacy validation | `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md` |
| Not currently present | `digitalmodel/examples/demos/gtm/demo_0[345]_*.html` (do not cite as local proof until restored) |

---

## Deliverable

A draft repo-tracked vessel-contractor outreach scaffold at `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` that ranks the current vessel-installation contractor/operator candidate set by outreach fit, attaches at least one public corporate-root evidence URL per live target, maps each live target to one or more GTM demo concepts as an internal proof anchor where available, and keeps individual contact details out of the public artifact. Owner-approved defaults have been applied: Hornbeck Offshore Services and Edison Chouest Offshore were added as fully populated GoM vessel/operator targets, Acteon remains partner-shape / non-counted for the vessel-contractor minimum, wind-only targets remain Medium/Defer pending a FOWT worked example, and the scaffold now has 20 semantically live countable vessel/operator targets using the explicit exclusion list in the validation artifact. The scaffold can feed #2556 only after live re-review clears #2554 and the owner explicitly approves any send.

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
            demo_anchor: [],                              # Demo 3 / 4 / 5 only until 6/7 ship or are restored
            pain_point_hypothesis: null,                  # public-evidence-bounded
            pain_point_evidence: [],                      # public source or explicit bounded inference
            corporate_root_evidence: [],                  # ≥1 official domain root required for every live/countable row
            deep_link_evidence: [],                       # official fleet/project/vessel page or explicit access boundary
            can_say_now: [],                              # ACE-claim envelope
            cannot_claim_yet: [],                         # adjacent-claim guard
            outreach_priority: null,                      # High / Medium / Low / Defer
            private_route: null                           # never inline; private pointer omitted from public artifact
        }
        if corporate_root_evidence is empty:
            mark candidate outreach_priority = Defer and exclude from live_countable_targets
        if candidate has no public deep_link_evidence and no explicit official-site/access-boundary note:
            mark candidate not_send_ready and keep/ downgrade below High until evidence is filled
        if candidate has individual contact (name, title, email, phone, individual LinkedIn):
            raise legal_sanity_failure before writing public artifact
        targets.append(candidate)

    rank(targets, key = (outreach_priority, demo_anchor_density, evidence_strength))
    exclude legacy/deprecated, Defer, and explicitly non-counted partner-shape rows from live_countable_targets
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
| Create | `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md` | Targeted committed-artifact legal/privacy scan and semantic target-count inventory |
| Pending r2 review | `scripts/review/results/2026-04-30-plan-2554-r2-{claude,codex,gemini,synthesis}.md` | Fresh independent adversarial review artifacts required before `status:plan-review` |

No production-code paths are touched. No edits to `digitalmodel/`, `assetutilities/`, or other Tier-1 repos. No edits to `docs/gtm/` (existing GTM corpus stays as-is and is referenced by path).

---

## Test List (research-artifact equivalent of TDD)

Because the deliverable is a research artifact rather than executable code, the test list below is a checklist of falsifiable, automatable assertions against the scaffold. Each row is a binary did/didn't check that must pass before `status:plan-review` can be requested.

| Check | What it verifies | How to execute |
|---|---|---|
| `live_countable_targets ≥ 20` | Acceptance criterion #1 in #2554; excludes legacy/deprecated, `Defer`, and explicitly non-counted partner-shape rows | Re-run the semantic row inventory recorded in `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md`; the plain heading grep is not sufficient. |
| `each_live_target has public evidence` | Acceptance criterion #2 at scaffold-review depth | per-target `corporate_root_evidence:` non-empty; High-priority rows must additionally have official-domain `deep_link_evidence:` or explicit `no-public-proof-found` / access-boundary text and `pain_point_evidence:` that does not overclaim. |
| `each live High-priority target has a deep-link backlog slot` | Corporate-root vs deep-link distinction is explicit | per-target field `deep_link_evidence:` present, even if marked `PENDING` in scaffold v1 |
| `each live target has pain-point evidence traceability` | Hypotheses are attributable, not freehand | per-target field `pain_point_evidence:` present |
| `no individual contact details inline` | Acceptance criterion #3 in #2554 + Legal Sanity Gate | Targeted committed-artifact scan recorded at `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md`; do not rely on `--diff-only` after commit. |
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

- [ ] Scaffold lists at least 20 **live countable** vessel-installation contractor or operator targets, each with `tier_seed`, `tier_revised`, `segment`, `outreach_priority`, and `demo_anchor` fields populated. The count must exclude legacy/deprecated rows, `outreach_priority: Defer`, and explicitly non-counted partner-shape rows such as Acteon.
- [ ] Every live countable target has at least one official corporate-root evidence URL (`corporate_root_evidence:` non-empty). Every High-priority row has official-domain `deep_link_evidence:` and `pain_point_evidence:` populated with either public official evidence or explicit bounded language such as `no-public-proof-found` / access-boundary notes; corporate roots alone are not sufficient for High-priority outreach-fit claims.
- [ ] No individual contact details (named persons, direct emails, phone numbers, individual LinkedIn URLs) appear inline in the public artifact. The scaffold carries an explicit "private contact data routes outside this repo" note in its header, and the committed-artifact legal/privacy scan records zero deny-list/contact-pattern hits.
- [ ] Each `outreach_priority: High` target maps to at least one GTM demo concept (Demo 3, 4, or 5 as the immediate set; 6, 7 if/when shipped/restored) under `demo_anchor:`. This is an internal positioning anchor, not proof that local Demo 3/4/5 output files are present.
- [ ] Review-routing contract is explicit: `status:plan-review` requires non-empty, independent r2 artifacts at `scripts/review/results/2026-04-30-plan-2554-r2-{claude,codex,gemini}.md` plus a synthesis at `...-r2-synthesis.md`; all substantive verdicts must be `APPROVE` or `MINOR`, and the r2 synthesis must explicitly disposition every MINOR finding as addressed, accepted-with-boundary, or deferred outside #2554 scope with rationale. `UNAVAILABLE`, zero-byte, self-bootstrap, or stale-path artifacts document failure but do not satisfy promotion.
- [ ] Each live target carries a `pain_point_evidence:` slot that either cites a public source path / URL or explicitly says the current statement is an inference from demo coverage pending deeper public verification.
- [ ] Live-countable and High-priority counts are consistent across artifacts: `Semantic live/countable vessel/operator target count` in the legal-scan artifact must match the lane summary live-countable integer, and the integer printed in the scaffold's "Targets in `outreach_priority: High`" Summary Counts bullet equals the row-grep count (`grep -cE '\*\*outreach_priority\.\*\* \*\*High\*\*'` over the scaffold) AND equals the count printed in `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md`. Any mismatch is a blocker for `status:plan-review` and must be reconciled before promotion. Historical note: the 2026-04-29 next-wave review found a prior body/summary divergence; current patched artifacts record 20 live-countable targets and 12 High-priority targets.
- [ ] Plan Index row exists in `docs/plans/README.md` reflecting the current plan status (`draft` until adversarial review lands, `plan-review` once it does).
- [ ] Lane summary at `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` records what shipped, what is blocked, and the exact next action for the user.
- [ ] No commits to production code paths (`digitalmodel/`, `assetutilities/`, etc.) and no email sends or external contacts initiated by this lane.

---

## Adversarial Review Summary

Historical review results are retained for traceability; they are not approval evidence for the current patched draft.

| Wave | Provider | Verdict | Current interpretation |
|---|---|---|---|
| 2026-04-29 next-wave | Claude / Codex / Gemini | mixed MINOR / MAJOR / UNAVAILABLE | Superseded by #2560 evidence-fill (now CLOSED/status:done) and the 2026-04-30 post-fill review. |
| 2026-04-30 r1 post-fill | Claude | MAJOR | Valid governance blockers: stale artifact path family, self-bootstrap review dependency, insufficient live-count validation, missing committed-artifact legal scan, stale status text. |
| 2026-04-30 r1 post-fill | Codex | MAJOR | Valid blockers: canonical review gate unmet, three-agent policy mismatch, target-count false pass, evidence gate too weak, `--diff-only` false-pass risk. |
| 2026-04-30 r1 post-fill | Gemini | MAJOR | Mixed validity: path-access false positives on files that exist locally, but useful signal that reviewer packages must inline exact artifact facts and avoid ungrounded demo-file claims. |

**Current draft state:** PATCHED AFTER R1; PENDING R2 RE-REVIEW. This draft incorporates the r1 blocker-removal edits: explicit r2 artifact family, no self-bootstrap review credit, semantic live-count validation, High-priority evidence/boundary requirements, targeted committed-artifact legal/privacy scan, corrected local artifact claims, and authoritative blocked status.

**Promotion condition:** #2554 may move from `status:blocked` to `status:plan-review` only after a fresh r2 adversarial review writes non-empty independent artifacts at `scripts/review/results/2026-04-30-plan-2554-r2-{claude,codex,gemini}.md`, writes `scripts/review/results/2026-04-30-plan-2554-r2-synthesis.md`, and the synthesis records no unresolved MAJOR findings. Until then, #2556 remains blocked/no-send unless the owner explicitly waives #2554 and separately approves send.

---

## Risks and Open Questions

- **Risk:** the contractor matrix is only as defensible as its weakest evidence URL. If a shipped row cites a fleet page that goes dark or moves, the matrix decays. **Mitigation:** every URL is cited at extraction time with a fetch-date footnote in the scaffold; the matrix is designated a *snapshot* (dated filename) rather than a living index.
- **Risk:** the contractor list overlaps with corpus-confidential client-project data (Woodfibre, SESA per `outreach-candidate-briefs-2026-04-28.md` Candidate 6). **Mitigation:** the matrix scaffold scope is *vessel-installation contractors only*. Any LNG-terminal or FOWT crossover is explicitly deferred to the relevant capability scope notes (`docs/gtm/marine-terminal-engineering-scope.md`, `docs/gtm/fowt-engineering-scope.md`) and not duplicated.
- **Risk:** the brochure-send lane (#2556) depends on this matrix; if the matrix slips, #2555 capability charts and #2556 brochure both stall. **Mitigation:** the scaffold is producible from already-public information in this repo + #1669/#1799 seed sets without external research, so the artifact can ship inside a single planning session.
- **Risk:** sending outreach without a confirmed contact route is wasteful. **Mitigation:** `outreach_priority: High` is gated on having a private-route pointer recorded (e.g., LinkedIn search query, BD-ops handoff lane) even if the literal contact lives outside this repo.
- **Resolved by owner default approval:** the OCS / Gulf of Mexico segment is in scope at High priority when a target maps to Demo 3/5 and Gulf access. Hornbeck and ECO were added as countable GoM vessel/operator targets; the broader GoM evidence lane is tracked in [#2562](https://github.com/vamseeachanta/workspace-hub/issues/2562).
- **Resolved by owner default approval:** wind-installation-only contractors remain Medium/Defer until the FOWT worked example ships. The FOWT worked-example lane is tracked in [#2561](https://github.com/vamseeachanta/workspace-hub/issues/2561).

---

## Complexity: T2

**T2** — research-artifact deliverable spanning multiple files (plan, scaffold, README index update, lane summary), with falsifiable acceptance criteria and an adversarial review gate. No production code paths touched; no client-facing send executed by this lane. Classification follows the workspace-hub convention that "scope of artifacts touched + need for cross-review" determines complexity rather than line count.
