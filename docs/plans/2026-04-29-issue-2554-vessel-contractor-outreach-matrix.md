# Plan for #2554: feat(gtm): weekly vessel contractor outreach matrix for April target

> **Status:** status:blocked — blocker-remediation patch applied; pending clean adversarial re-review (not approval-ready)
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2554
> **Review artifacts:** r1 post-fill review at `scripts/review/results/2026-04-30-plan-2554-{claude,codex,gemini,disagreement}.md` returned MAJOR; clean rerun required at `scripts/review/results/2026-04-30-plan-2554-r2-{claude,codex,gemini,synthesis}.md` before `status:plan-review`.
> **Self-reference slug:** `2026-04-29-issue-2554-vessel-contractor-outreach-matrix`

---

## Resource Intelligence Summary

### Existing repo code / artifacts

- **Found:** `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` (138 lines, 2026-04-02) — three-step cold/follow-up/meeting outreach sequence with placeholder slots (`{{COMPANY}}`, `{{JOB_TITLE}}`, `{{PAIN_POINT_*}}`), Day 0/3/7 timing, A/B subject variants, and disqualification criteria. **Implication for #2554:** the matrix needs a per-target slot for `{{PAIN_POINT_1..3}}` derived from public fleet/project evidence, otherwise the templates render with stale generic copy.
- **Found:** `docs/gtm/outreach-candidate-briefs-2026-04-28.md` (1014 lines, lane C2 output) — 10 buyer-segment briefs with `can-say-now` / `cannot-claim-yet` / `missing-proof` fields. Candidates 3, 4, and 5 are vessel-installation-segment (deepwater mudmat, shallow-water S-lay, rigid-jumper installation). **Implication:** the contractor matrix can adopt the eight-field brief template and use Demo 3/4/5 as conceptual proof anchors, but the plan no longer treats missing demo-output files as existing local artifacts.
- **Found:** `docs/gtm/capability-summary.md`, `docs/gtm/capability-map.md`, `docs/gtm/marine-terminal-engineering-scope.md`, `docs/gtm/fowt-engineering-scope.md` — capability framing already split by service line and adjacent segments. The contractor matrix should reference these via path, not re-author scope text.
- **Found:** Issue #1669 body (Apr 2) — pre-existing tier seed list (Tier-1 majors: Subsea7, TechnipFMC, Saipem, McDermott, Allseas, Heerema, Boskalis, Van Oord, DEME; Tier-2 specialists: DOF Subsea, Solstad, Bourbon, Sapura, EMAS/Ezra, Seaway7; Tier-3 niche: Helix, Superior Energy, DeepOcean, Gulf Offshore). **Implication:** the matrix takes #1669's tier list as the starting set and must reconcile (drop, retier, add) using the criteria below; #1669 has no evidence URLs attached to most names.
- **Found:** Issue #1799 body — pipelay barge spec collection target (Allseas Lorelay, Subsea 7 Seven Navica, Saipem Castorone, McDermott DB101, Sapura Constructor, Van Oord Stork, Boskalis lay barges). **Implication:** vessel-spec data anchors the "relevant fleet angle" column for ~7 contractors and is also a public-source seed for the matrix. #1799 itself is a separate data-collection issue — the matrix references its outputs without duplicating spec rows.
- **Demo artifact boundary:** `docs/gtm/outreach-candidate-briefs-2026-04-28.md` provides the Demo 3/4/5 positioning language used by this matrix. Exact `digitalmodel/examples/demos/gtm/output/demo_03|04|05_*.html` proof paths are not present on GitHub `main` for this repo, so the public matrix must not cite those local output paths as proof. If another checkout has generated demo outputs, treat them as separate implementation evidence that must be committed or linked before send-ready claims.
- **Found:** `docs/gtm/intake/prospect-schema.json` (Draft-07 validated per #2346) — defines the YAML intake shape used to produce 48-hour custom demo reruns. **Implication:** the matrix `outreach priority` column should flag which contractors would be worth pre-staging an intake YAML for once their interest is confirmed.
- **Resolved gap:** Before the #2554 lane there was no single artifact merging (a) #1669 tier list, (b) public fleet evidence, (c) #1799 vessel-spec coverage, (d) per-target pain-point hypotheses, and (e) demo-anchor mapping. The current scaffold now provides that matrix at `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`.
- **Gap:** No automated public/private boundary check exists for GTM matrices. `scripts/legal/legal-sanity-scan.sh --diff-only` exists per `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates", but `--diff-only` can false-pass after files are committed. This plan therefore requires a targeted committed-artifact scan recorded at `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md`.

### Standards

Not applicable. `cat:business`, `cat:strategy`, `domain:gtm`, `priority:high` — no engineering standards exercised, no calc constants emitted; `.claude/rules/calc-citation-contract.md` does not apply. `.claude/rules/coding-style.md` (relative paths, no hardcoded absolute paths in artifacts) and `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates for Public Artifacts" do apply.

### LLM Wiki pages consulted

- No wiki pages are direct inputs to this matrix. The matrix consumes public corporate fleet/project disclosures and demo-concept anchors from existing GTM briefs; missing local demo-output files are not treated as proof paths for promotion. Wiki promotion of any contractor-specific synthesis is out of scope until a public-source-only methodology layer is approved separately (out-of-scope: repo-public legal/privacy scan is current for this matrix; separate public-source-only wiki synthesis remains out of scope).

### Documents consulted

- Issue #2554 body — defines the deliverable shape (≥20 ranked targets, public evidence per target, public/private separation, follow-up issues for missing data) and ties scope back to #1669/#2016 and Demo 3/4/5 as proof anchors.
- Issue #1669 body — defines the seed tier list, the per-target prospect-list structure (`company / contact / title / email`), email-sequence cadence, value-prop angles, and Phase 1 / Phase 2 / Phase 3 decomposition. **The matrix in this plan is the Phase 1 "prospect list with company, segment/tier" deliverable, not the email send.**
- Issue #2016 body — parent GTM conversion umbrella; lists Tier-3 outreach sub-issues (#191, #117, #1669, #197) as blocked on demo readiness. The GTM brief treats Demo 1–5 as the conceptual unblocker for #1669; because local demo-output files are not present at this workspace-hub HEAD, #2554 uses those only as internal matrix anchors and does not authorize send-ready demo-proof claims.
- Issue #1799 body — public pipelay-barge spec inventory; provides 7 vessel→operator mappings the matrix can reuse without re-research.
- `docs/BUSINESS_BRAIN.md` §"Interactive Weekly GTM Targets" (line 106-112) — confirms the April 1 weekly target is "produce vessel capability charts and send a good brochure to all researched vessel contractors". The matrix in this plan supplies the *researched-contractor* substrate that the brochure-send (#2556) consumes.
- `docs/BUSINESS_BRAIN.md` §"GTM-to-Code Readiness Loop" (lines 114-120) — confirms that public-facing GTM artifacts must carry source provenance and may not exceed repo-evidence claims. The matrix template includes evidence-URL and `can-say-now` columns to enforce this.
- `docs/BUSINESS_BRAIN.md` §"Legal Sanity Gates for Public Artifacts" (lines 122-132) — establishes that any client-derived or contact-list content must pass legal sanity before public promotion. **Decision in this plan:** the public matrix at `docs/reports/gtm/...` carries no direct contact mechanisms or named-person outreach details (emails, phone numbers, individual LinkedIn URLs, or name-with-title contact strings). Per-target named contacts, if any, route to a private surface outside this repo.
- `docs/plans/_template-issue-plan.md` — the canonical template; this plan follows its section order and the embedded retrieval contract.
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` (v3.1.0) — the planning workflow skill. Confirms draft → adversarial review → `status:plan-review` → user approval gating; no self-approval.
- `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/2554-contractor-matrix.md` (recovered from `git show HEAD:`) — the overnight task brief that scoped this work; explicitly forbids implementation code, email sends, and self-approval, and enforces public/private boundary preservation.
- Memory: `feedback_inline_gh_issue_url.md` — issue references must render as GitHub Markdown hyperlinks (`#2554` → `[#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554)`). Applied to newly edited GitHub issue references where practical; legacy bare issue tokens may remain in quoted context and are not a promotion gate.
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
- GitHub-main boundary: exact `digitalmodel/examples/demos/gtm/output/demo_03|04|05_*.html` report paths are not present on `main`; treat Demo 3/4/5 row values as positioning anchors from the GTM briefs unless/until a committed proof path is restored.
- EXISTS after #2554/#2560 work: `docs/reports/gtm/` and `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`.
- EXISTS: `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` (this file).

**Gap proofs**:
- Current artifact proof: `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` and `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md` exist on `main` after the blocker-remediation patch.
- `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` is the reusable template source; there is no public prospect-list artifact with individual contacts to extend, and this matrix intentionally keeps contact data out of repo.

<!-- Source count: 4 GitHub issues (#2554/#1669/#2016/#1799) + Business Brain + 6 repo file paths + 2 memory entries + plan template + planning skill = 15 distinct sources. Minimum 3 satisfied. -->

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
| Legal/privacy validation | `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md` generated by `uv run python scripts/validation/validate_gtm_2554_matrix.py --write-artifact` |
| Validation script | `scripts/validation/validate_gtm_2554_matrix.py` | Repo-public structural/legal/count gate used by this plan; not a semantic substitute for reviewer spot-checks |
| Demo proof boundary | Do not cite `digitalmodel/examples/demos/gtm/output/demo_0[345]_*.html` as public proof unless those exact paths exist on GitHub `main` or are restored in a follow-up. |

---

## Deliverable

A draft repo-tracked vessel-contractor outreach scaffold at `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` that ranks the current vessel-installation contractor/operator candidate set by outreach fit, attaches at least one public corporate-root evidence URL per live target, maps each live target to one or more GTM demo concepts as an internal proof anchor where available, and keeps individual contact details out of the public artifact. Owner-approved defaults have been applied: Hornbeck Offshore Services and Edison Chouest Offshore were added as fully populated GoM vessel/operator targets, Acteon remains partner-shape / non-counted for the vessel-contractor minimum, wind-focused targets remain Medium/Defer for send-readiness pending a FOWT worked example; only rows explicitly tagged `wind-only; excluded from live_countable until FOWT worked example` are excluded from the 20-target live count. The scaffold now has 20 semantically live countable vessel/operator targets using the explicit exclusion list in the validation artifact. The scaffold can feed #2556 only after live re-review clears #2554 and the owner explicitly approves any send.

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
            demo_anchor: [],                              # Demo 3 / 4 / 5 positioning anchors only until public proof paths are restored
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
            mark candidate not_send_ready and keep / downgrade below High until evidence is filled
        if candidate is High and private_route is null:
            mark candidate high_priority_but_no_send_route and keep private detail outside repo
        if candidate is explicitly tagged wind-only and FOWT worked example is not shipped:
            exclude candidate from live_countable_targets unless it also has non-wind vessel/operator evidence
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
| Update / done | `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` | Primary deliverable — research scaffold; patched for evidence/legal/demo-boundary drift |
| Update / done | `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` | This canonical plan; patched after r1/r2 blocker findings |
| Update / done | `docs/plans/README.md` | Plan Index row points at the canonical plan and current blocked/r2 status |
| Update / done | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` | Lane summary reconciled after #2560 closure and blocker-remediation patch |
| Create / done | `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md` | Targeted committed-artifact legal/privacy scan and semantic target-count inventory |

### Files required before promotion (not yet completed until review artifacts are archived)

| Required before promotion | Path | Gate |
|---|---|---|
| r2 review artifacts | `scripts/review/results/2026-04-30-plan-2554-r2-{claude,codex,gemini,synthesis}.md` | Fresh independent adversarial review artifacts required before `status:plan-review`; produced by the follow-on remediation owner using `scripts/review/plan-review-fanout.sh` or a documented provider fallback |

No production-code paths are touched. No edits to `digitalmodel/`, `assetutilities/`, or other Tier-1 repos. No edits to `docs/gtm/` (existing GTM corpus stays as-is and is referenced by path).

---

## Test List (research-artifact equivalent of TDD)

Because the deliverable is a research artifact rather than executable code, the test list below is a checklist of falsifiable, automatable assertions against the scaffold. Each row is a binary did/didn't check that must pass before `status:plan-review` can be requested.

| Check | What it verifies | How to execute |
|---|---|---|
| `live_countable_targets ≥ 20` | Acceptance criterion #1 in #2554; excludes legacy/deprecated, `Defer`, explicitly non-counted partner-shape rows, and rows explicitly tagged wind-only pending FOWT | Run `uv run python scripts/validation/validate_gtm_2554_matrix.py --write-artifact`; the script parses target blocks, verifies required row fields, derives live/countable rows, compares scaffold/summary count claims, rewrites the legal-scan inventory with PASS/FAIL status, and fails if live_countable < 20 or contact/deny-list hits exist. |
| `each_live_target has public evidence` | Acceptance criterion #2 at scaffold-review depth | validator confirms each counted row has at least one allowed public URL in `corporate_root_evidence:` and a populated `deep_link_evidence:` field; High-priority rows must additionally have official-source or explicitly bounded `deep_link_evidence:` / `pain_point_evidence:` that does not overclaim. |
| `each live High-priority target has a deep-link backlog slot` | Corporate-root vs deep-link distinction is explicit | per-target field `deep_link_evidence:` present; High-priority rows may not be `PENDING`, while Defer/non-counted rows may remain `PENDING` with explicit exclusion status |
| `each live target has pain-point evidence traceability` | Hypotheses are attributable, not freehand | per-target field `pain_point_evidence:` present |
| `no individual contact details inline` | Acceptance criterion #3 in #2554 + Legal Sanity Gate | Targeted committed-artifact scan recorded at `docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md`; do not rely on `--diff-only` after commit. |
| `each High-priority target has ≥1 demo anchor` | Outreach-readiness check (matrix usable for #2556) | per-target field `demo_anchor:` non-empty for `outreach_priority: High` |
| `tier_seed reconciliation is recorded` | Traceability to #1669 (no silent retiering) | each target's `tier_seed` and `tier_revised` fields both present |
| `cannot_claim_yet field is populated` | Inherits the proof-bounding contract from `outreach-candidate-briefs-2026-04-28.md` | per-target field `cannot_claim_yet:` non-empty |
| `follow-up issues opened for High + low-evidence` | Acceptance criterion #4 in #2554 | issue list at the bottom of the scaffold cross-links each filed issue |
| `high_priority_count_consistency` | Numeric count of High-priority rows agrees with the named list, scaffold Summary Counts, lane-summary file, and legal-scan inventory | Run `uv run python scripts/validation/validate_gtm_2554_matrix.py --write-artifact`; compare its generated live-countable and High counts to the scaffold Summary Counts bullet and the lane-summary counts. Do not rely on markdown-emphasis grep alone. |
| `provider fallback is documented without weakening gate order` | Review-readiness contract is explicit | AC text says `UNAVAILABLE` artifacts document a blocked provider but do not by themselves satisfy promotion |
| `public/private routing decision recorded` | Boundary policy applied per BUSINESS_BRAIN | scaffold header carries the explicit decision text |

These checks replace the standard `pytest` lines that would appear for an engineering plan. The acceptance criteria below restate them in user-facing form.

---

## Acceptance Criteria

- [ ] Scaffold lists at least 20 **live countable** vessel-installation contractor or operator targets, each with `tier_seed`, `tier_revised`, `segment`, `outreach_priority`, `demo_anchor`, `corporate_root_evidence`, and `deep_link_evidence` populated. The count must exclude legacy/deprecated rows, `outreach_priority: Defer`, explicitly non-counted partner-shape rows such as Acteon, and rows explicitly tagged `wind-only; excluded from live_countable until FOWT worked example`. Wind-focused but broader offshore contractor/operator rows may remain live-countable while still not send-ready for #2556.
- [ ] Every live countable target has at least one allowed public evidence URL in `corporate_root_evidence:` and a populated `deep_link_evidence:` field containing official-domain evidence or explicit bounded language such as `no-stable-official-page-verified` / `no-public-proof-found` / access-boundary notes. Reviewer spot-check confirms the evidence is company/corporate-root or explicitly bounded. Every High-priority row has `pain_point_evidence:` populated with either public official evidence or explicit bounded language; corporate roots alone are not sufficient for High-priority outreach-fit claims.
- [ ] No individual contact details (named persons, direct emails, phone numbers, individual LinkedIn URLs) appear inline in the public artifact. The scaffold carries an explicit "private contact data routes outside this repo" note in its header; the committed-artifact legal/privacy scan records zero deny-list/contact-pattern hits, and manual reviewer spot-check is required because regexes cannot prove semantic absence of all names/titles.
- [ ] Each `outreach_priority: High` target maps to at least one GTM demo concept (Demo 3, 4, or 5 as the immediate set; 6, 7 if/when shipped/restored) under `demo_anchor:`. This is an internal positioning anchor, not proof that local Demo 3/4/5 output files are present.
- [ ] Review-routing contract is explicit: `status:plan-review` requires non-empty, independent r2 artifacts at `scripts/review/results/2026-04-30-plan-2554-r2-{claude,codex,gemini}.md` plus a synthesis at `...-r2-synthesis.md`; those artifacts must cite the exact content commit SHA under review. The synthesis should cite the parent/content commit reviewed; if the synthesis artifact itself is committed later, the issue comment must state both the reviewed content SHA and the artifact-archive SHA. During the r2 run these artifacts may not exist yet; promotion is allowed only after they are archived. All substantive verdicts must be `APPROVE` or `MINOR`, and the r2 synthesis must explicitly disposition every MINOR finding as addressed, accepted-with-boundary, or deferred outside #2554 scope with rationale. If a provider CLI fails, the synthesis must document the failure and either rerun via a working route or keep #2554 blocked; no automatic 2-of-3 downgrade is authorized. `UNAVAILABLE`, zero-byte, self-bootstrap, or stale-path artifacts document failure but do not satisfy promotion.
- [ ] Each live target carries a `pain_point_evidence:` slot that either cites a public source path / URL or explicitly says the current statement is an inference from demo coverage pending deeper public verification.
- [ ] Live-countable and High-priority counts are reproducible and consistent across artifacts: `uv run python scripts/validation/validate_gtm_2554_matrix.py --write-artifact` must pass; the generated `Semantic live/countable vessel/operator target count` must match the lane summary live-countable integer, and the generated High count must match the scaffold Summary Counts bullet and lane-summary High count. Any mismatch is a blocker for `status:plan-review` and must be reconciled before promotion. Historical note: the 2026-04-29 next-wave review found a prior body/summary divergence; current patched artifacts record 20 live-countable targets and 12 High-priority targets.
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


### R1/R2 blocker-remediation ledger

| Prior finding theme | Resolution in current draft | Verification |
|---|---|---|
| Stale artifact family / self-bootstrap review | r2 artifact family required; Hermes delegate no longer counts as promotion evidence | AC #5 + Promotion condition |
| Static or false target counts | Added executable validator `scripts/validation/validate_gtm_2554_matrix.py` and generated legal-scan artifact | `uv run python scripts/validation/validate_gtm_2554_matrix.py --write-artifact` |
| Demo proof-path overclaim | Scaffold now treats Demo 3/4/5 as positioning concepts unless proof paths are restored | Scaffold header + Cross-References |
| `--diff-only` false-pass risk | Scaffold/plan require committed-artifact scan pattern | Legal scan artifact + scaffold legal-gate text |
| #2560 stale dependency | Summary states #2560 is CLOSED/status:done; remaining blocker is r2 review | Lane summary + README row |
| Provider CLI/regression risk | r2 synthesis must document provider failure and keep blocked unless rerun via working route | AC #5 |

**Current draft state:** PATCHED AFTER R1; PENDING CLEAN RERUN REVIEW. This draft incorporates the r1 blocker-removal edits: explicit r2 artifact family, no self-bootstrap review credit, semantic live-count validation, High-priority evidence/boundary requirements, targeted committed-artifact legal/privacy scan, corrected local artifact claims, and authoritative blocked status.

**Promotion condition:** #2554 may move from `status:blocked` to `status:plan-review` only after a fresh rerun adversarial review writes non-empty independent artifacts at `scripts/review/results/2026-04-30-plan-2554-r2-{claude,codex,gemini}.md`, writes `scripts/review/results/2026-04-30-plan-2554-r2-synthesis.md`, and the synthesis records no unresolved MAJOR findings. Until then, #2556 remains blocked/no-send unless the owner explicitly waives #2554 and separately approves send.

---

## Risks and Open Questions

- **Risk:** the contractor matrix is only as defensible as its weakest evidence URL. If a shipped row cites a fleet page that goes dark or moves, the matrix decays. **Mitigation:** URLs are captured in a dated snapshot and rows with access challenges or unverifiable deep pages carry explicit boundary language; a future hardening pass may add per-URL fetch-date footnotes.
- **Risk:** the contractor list overlaps with corpus-confidential client-project data (Woodfibre, SESA per `outreach-candidate-briefs-2026-04-28.md` Candidate 6). **Mitigation:** the matrix scaffold scope is *vessel-installation contractors only*. Any LNG-terminal or FOWT crossover is explicitly deferred to the relevant capability scope notes (`docs/gtm/marine-terminal-engineering-scope.md`, `docs/gtm/fowt-engineering-scope.md`) and not duplicated.
- **Risk:** the brochure-send lane (#2556) depends on this matrix; if the matrix slips, #2555 capability charts and #2556 brochure both stall. **Mitigation:** the scaffold is producible from already-public information in this repo + #1669/#1799 seed sets without external research, so the artifact can ship inside a single planning session.
- **Risk:** sending outreach without a confirmed contact route is wasteful. **Mitigation:** #2554 may rank High based on fit/evidence, but #2556 send-readiness is gated on an external private-route pointer; no private-route details are stored in this repo and no send is authorized by #2554.
- **Resolved by owner default approval:** the OCS / Gulf of Mexico segment is in scope at High priority when a target maps to Demo 3/5 and Gulf access. Hornbeck and ECO were added as countable GoM vessel/operator targets; the broader GoM evidence lane is tracked in [#2562](https://github.com/vamseeachanta/workspace-hub/issues/2562).
- **Resolved by owner default approval:** wind-installation-only contractors remain Medium/Defer until the FOWT worked example ships. The FOWT worked-example lane is tracked in [#2561](https://github.com/vamseeachanta/workspace-hub/issues/2561).

---

## Complexity: T2

**T2** — research-artifact deliverable spanning multiple files (plan, scaffold, README index update, lane summary), with falsifiable acceptance criteria and an adversarial review gate. No production code paths touched; no client-facing send executed by this lane. Classification follows the workspace-hub convention that "scope of artifacts touched + need for cross-review" determines complexity rather than line count.
