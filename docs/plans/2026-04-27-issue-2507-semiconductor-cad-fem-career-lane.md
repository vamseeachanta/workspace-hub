# Plan for #2507: Feature: semiconductor chip-design CAD/FEM career lane

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2507
> **Review artifacts:** scripts/review/results/2026-04-27-plan-2507-claude.md | scripts/review/results/2026-04-27-plan-2507-codex.md | scripts/review/results/2026-04-27-plan-2507-gemini.md (to be produced by adversarial wave)
> **Plan filename (final):** docs/plans/2026-04-27-issue-2507-2026-04-27-issue-2507-semiconductor-cad-fem-career-lane.md

---

## Resource Intelligence Summary

### Scope clarification (must read before reviewing rest of plan)

#2507 is the **umbrella/lane-tracking** issue. Its body explicitly states: "This umbrella tracks the lane; child issues should carry implementation details." The five sub-deliverables enumerated in the issue body (research/taxonomy, OpenLane RTL-to-GDS demo, KLayout/GDSFactory layout demo, package thermal/mechanical FEM benchmark, job-application packet) are already filed as children #2508/#2509/#2510/#2511/#2512 with their own plans, reviews, approvals, and TDD artifacts. **This plan therefore does NOT propose new implementation work that duplicates the children.** It proposes the lane-level orchestration deliverable: a single living lane-status document that aggregates child progress, gates lane closure on the children's acceptance criteria, and surfaces lane-wide guardrails. Wave-1 lesson: do not claim work is needed when sibling issues already cover it (#2479 wave-1 anti-pattern). Wave-2 lesson: verify state shifts (two of five children are already CLOSED).

### Existing repo code

- Roadmap anchor exists: `docs/roadmaps/chip-design-cad-fem-career-roadmap.md` (committed 268dbf8a2).
- Knowledge base + taxonomy already shipped under #2508: `docs/reports/semiconductor-cad-fem-knowledge-base.md` and `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml` (committed 942efe2e6, child issue CLOSED 2026-04-27).
- Existing test for the KB taxonomy: `tests/docs/test_semiconductor_kb.py` (git-tracked). The lane-status document proposed here adds a sibling test, not a replacement.
- No `docs/lanes/`, no `docs/tracks/`, and no semiconductor-specific lane status document exists. `git ls-files | grep -iE 'semiconductor|chip-design'` returns only the four artifacts above plus the four children's plan files.
- No `scripts/semiconductor/` directory yet (verified via `git ls-files scripts/semiconductor/` → empty). #2509/#2510/#2511 plans each propose to create that directory; this plan does **not** create it.

### Standards and source limits

| Source / standard family | Status | Finding |
|---|---|---|
| `data/document-index/standards-transfer-ledger.yaml` | not consulted at lane level | Standards-driven numeric work happens in #2511 (closed) and any future child; the umbrella does not introduce standards-derived constants and is therefore out of scope for the calc-citation contract (`.claude/rules/calc-citation-contract.md`). |
| JEDEC / IPC | restricted; not locally ingested | #2508 KB §"JEDEC/IPC access limitations" already encodes the lane-wide guardrail. The lane-status doc must reference (not restate) that section. |
| Open PDK design-rule decks (Sky130, GF180MCU) | external, consumed by #2509 only | Not in lane-level scope. |

### LLM wiki / knowledge pages consulted

- Per #2508 KB §"JEDEC/IPC access limitations" plus a `git ls-files knowledge/wikis/ | grep -iE 'semiconductor|asic|chip-design|openroad|openlane|sky130|gf180'` check returning zero matches, no semiconductor wiki pages exist in the repo. The lane currently has no wiki surface; the lane-status doc records this as the canonical answer to the recurring "where is the semiconductor wiki?" question rather than creating one speculatively.

### Documents consulted

- Issue #2507 body (this plan's primary source) — defines five-track lane, names the roadmap, states "this umbrella tracks the lane; child issues should carry implementation details."
- Children #2508 (CLOSED), #2509 (OPEN), #2510 (OPEN, status:plan-review), #2511 (CLOSED, status:done), #2512 (OPEN). KB-recommended execution order is #2508→#2511→#2510→#2509→#2512 (per `docs/reports/semiconductor-cad-fem-knowledge-base.md` §Executive Summary lines 12-19).
- `docs/roadmaps/chip-design-cad-fem-career-roadmap.md` — Wave 1 already produced (#2508 done); Wave 4 already produced (#2511 done); Waves 2/3/5 in progress (#2509/#2510/#2512). The roadmap is the authoritative narrative; the lane-status doc proposed here is the operational checklist that complements it.
- `docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md` — sibling plan; verified the lane-wide convention `scripts/semiconductor/`, `tests/semiconductor/`, `data/semiconductor/<feature>/`. The lane-status doc in this plan must NOT contradict that convention.
- `docs/plans/2026-04-26-issue-2508-semiconductor-cad-fem-knowledge-base.md` and `2026-04-27-issue-2511-semiconductor-package-fem-benchmark.md` — closed-child plans; their acceptance criteria become inputs to the umbrella's exit checklist.

### Gaps identified

- No single lane-status document tracks the five children's state, exit criteria, and lane-wide guardrails (JEDEC/IPC posture, "no tapeout / no foundry signoff" disclaimer, KB-recommended execution order, scope-creep boundary). Today this information is split across the roadmap, the KB report, and individual child plans, so reviewers and future hires must reassemble it.
- No test asserts lane-wide guardrail invariants (e.g., the lane-status document references each of the five children, references the KB report, references the roadmap, and does not contain banned compliance-claim phrases like "JEDEC compliant" or "tapeout-ready").
- No automated check verifies the umbrella issue's lane-wide acceptance (e.g., "all five children are at least at status:plan-approved" or "the four required portfolio artifact paths exist when applicable").

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-27T09:19:07Z via `gh issue view` / `gh issue list --label "domain:semiconductor"`):
- `#2507` — OPEN — Feature: semiconductor chip-design CAD/FEM career lane (no `status:*` label).
- `#2508` — CLOSED — research(semiconductor): build chip-design CAD/FEM knowledge base and job taxonomy (status:plan-approved on close).
- `#2509` — OPEN — feat(eda): create reproducible OpenLane/OpenROAD RTL-to-GDS demo report (no `status:*` label visible).
- `#2510` — OPEN — feat(cad): build Python layout/CAD automation demo for chip/package geometries (status:plan-review).
- `#2511` — CLOSED — feat(fem): create semiconductor package thermal/thermo-mechanical benchmark (status:done).
- `#2512` — OPEN — feat(career): build semiconductor CAD/FEM portfolio and job-application packet (no `status:*` label).

**File existence** (`ls` / `git ls-files` 2026-04-27T09:19:07Z):
- EXISTS, git-tracked: `docs/reports/semiconductor-cad-fem-knowledge-base.md`
- EXISTS, git-tracked: `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml`
- EXISTS, git-tracked: `docs/roadmaps/chip-design-cad-fem-career-roadmap.md`
- EXISTS, git-tracked: `docs/plans/_template-issue-plan.md`, `docs/plans/README.md`
- EXISTS, git-tracked: `tests/docs/test_semiconductor_kb.py`
- EXISTS: `.planning/plan-approved/2508.md`, `.planning/plan-approved/2511.md` (no markers for 2507/2509/2510/2512)
- MISSING (this plan creates): `docs/reports/semiconductor-cad-fem-lane-status.md`
- MISSING (this plan creates): `tests/docs/test_semiconductor_lane_status.py`

**Line excerpts**:

From `docs/reports/semiconductor-cad-fem-knowledge-base.md` lines 12-19 (KB-recommended execution order):
```
The recommended order remains:
1. #2508 — build this knowledge base and taxonomy.
2. #2511 — create a semiconductor package thermal/thermo-mechanical FEM benchmark.
3. #2510 — build Python layout/CAD automation for chip/package geometries.
4. #2509 — create a reproducible OpenLane/OpenROAD RTL-to-GDS demo report.
5. #2512 — convert the artifacts into a portfolio and job-application packet.
```

From issue #2507 body (Policy section):
```
Follow repository gates: issue -> plan -> adversarial review -> user approval -> TDD implementation. This umbrella tracks the lane; child issues should carry implementation details.
```

**Gap proofs**:
- `git ls-files | grep -i "semiconductor-cad-fem-lane-status"` → empty (confirms lane-status doc does not yet exist).
- `ls docs/lanes 2>&1` → "No such file or directory" (confirms no `docs/lanes/` convention exists; lane-status placement under `docs/reports/` matches sibling pattern of #2508's report).
- `git ls-files scripts/semiconductor/` → empty (confirms umbrella has not pre-empted child scripts).

Distinct sources consulted: 5 (issue #2507 body + four sibling issues #2508/#2509/#2510/#2511/#2512 + roadmap doc + KB report + #2509 plan + #2511 plan = 9 distinct sources).

---

## Verification Log

| # | Claim in plan | Verification command / source | Result |
|---|---|---|---|
| 1 | Issue #2507 is OPEN, umbrella, no status label | `gh issue view 2507 --json labels,state` | Confirmed OPEN, labels include enhancement/priority:high/cat:engineering/cat:research/cat:career/domain:semiconductor/domain:chip-design; no `status:*` label. |
| 2 | #2508 is CLOSED with knowledge-base artifacts produced | `gh issue view 2508`; `ls docs/reports/semiconductor-cad-fem-knowledge-base.md` | CLOSED with status:plan-approved; KB report and YAML matrix both exist and are git-tracked. |
| 3 | #2509 OPEN, plan exists | `gh issue view 2509`; `ls docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md` | OPEN; plan file exists, status `draft` per its header. |
| 4 | #2510 OPEN, status:plan-review | `gh issue view 2510` | OPEN with `status:plan-review`. |
| 5 | #2511 CLOSED, status:done | `gh issue view 2511` | CLOSED with `status:done`. |
| 6 | #2512 OPEN, no status label | `gh issue view 2512` | OPEN; no `status:*` label. |
| 7 | KB report recommends order #2508→#2511→#2510→#2509→#2512 | Read `docs/reports/semiconductor-cad-fem-knowledge-base.md` lines 12-19 | Confirmed. |
| 8 | Roadmap document exists at `docs/roadmaps/chip-design-cad-fem-career-roadmap.md` | `ls`; `git ls-files docs/roadmaps/chip-design-cad-fem-career-roadmap.md` | EXISTS, tracked, last commit 268dbf8a2. |
| 9 | YAML matrix exists at `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml` | `ls`; read first 100 lines | EXISTS, schema_version 1, 6 role families, 6 job_evidence rows. |
| 10 | No existing `docs/reports/semiconductor-cad-fem-lane-status.md` | `git ls-files | grep semiconductor-cad-fem-lane-status` | Empty — file does not exist. |
| 11 | No existing `docs/lanes/` directory | `ls docs/lanes 2>&1` | "No such file or directory". |
| 12 | No semiconductor wiki pages | `git ls-files knowledge/wikis/ | grep -iE 'semiconductor|asic|chip-design|openroad|openlane|sky130|gf180'` | Empty. |
| 13 | Existing semiconductor test pattern | `ls tests/docs/test_semiconductor_kb.py` | EXISTS, git-tracked. The new lane-status test follows the same `tests/docs/` placement. |
| 14 | Approval markers — only #2508 and #2511 have local markers | `ls .planning/plan-approved/` filtered to `25(07|08|09|10|11|12).md` | Only `2508.md` and `2511.md` present. |
| 15 | KB-stated guardrail "no JEDEC/IPC compliance claim" | `docs/reports/semiconductor-cad-fem-knowledge-base.md` §"JEDEC/IPC access limitations" lines 91-95 | Confirmed: "may be used only as vocabulary and source-acquisition targets... This report does not claim detailed standard requirements, compliance, or source extraction from those documents." |

All claims load-bearing for plan correctness are verified. No `[UNVERIFIED]` claims remain.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-27-issue-2507-`2026-04-27-issue-2507-semiconductor-cad-fem-career-lane`.md |
| Lane status document (NEW) | docs/reports/semiconductor-cad-fem-lane-status.md |
| Lane-status test (NEW) | tests/docs/test_semiconductor_lane_status.py |
| Plan review — Claude | scripts/review/results/2026-04-27-plan-2507-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-27-plan-2507-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-27-plan-2507-gemini.md |
| Index update | docs/plans/README.md (add row for this plan) |
| Existing roadmap (referenced, not modified) | docs/roadmaps/chip-design-cad-fem-career-roadmap.md |
| Existing KB report (referenced, not modified) | docs/reports/semiconductor-cad-fem-knowledge-base.md |
| Existing taxonomy (referenced, not modified) | data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml |
| Existing test (sibling pattern; not modified) | tests/docs/test_semiconductor_kb.py |
| Children plans (referenced, not modified) | docs/plans/2026-04-26-issue-2508-*.md, 2509-*, 2510-*, 2026-04-27-issue-2511-*.md |

---

## Deliverable

A living lane-status document at `docs/reports/semiconductor-cad-fem-lane-status.md`, plus a TDD-covered guardrail test, that operationally tracks the five children of the semiconductor CAD/FEM career lane and defines the lane-wide acceptance gates needed to close the umbrella issue #2507.

---

## Pseudocode

The lane-status document will be authored as Markdown with these sections:

```
## Lane Charter
- Restate (in 2-3 sentences) the umbrella scope from #2507 body and the technical thesis from the roadmap.
- Quote the KB-recommended execution order (#2508 → #2511 → #2510 → #2509 → #2512).

## Children Status Table
- Row per child issue: number, title, GitHub state, status:* label, plan path, approval marker, key artifact paths, KB-position-in-order.
- Source-of-truth note: GitHub label > approval marker > README row (per issue-planning-mode SKILL §"Status authority").

## Lane-wide Guardrails
- Cite #2508 KB §"JEDEC/IPC access limitations" — no compliance claims.
- Cite #2508 KB §"Risks and Guardrails" — no tapeout/foundry-signoff claims; demo-only geometries.
- Convention: scripts/semiconductor/, tests/semiconductor/, data/semiconductor/<feature>/ (per #2509/#2511 plan precedent).
- Wiki posture: no semiconductor wiki pages today; create only when a downstream child needs one.

## Lane Acceptance Gate (mirrors umbrella's checklist)
- KB report exists and remains accurate (currently TRUE — landed via #2508).
- Package thermal/thermo-mechanical FEM benchmark exists (currently TRUE — landed via #2511).
- Python layout/CAD demo exists (currently FALSE — pending #2510 implementation).
- Reproducible OpenLane/OpenROAD demo report exists (currently FALSE — pending #2509 implementation).
- Job-application packet exists and references the four artifacts above (currently FALSE — pending #2512).
- All five child issues are CLOSED, and #2507 has no remaining open children (currently FALSE).

## Maintenance Protocol
- This document is refreshed in the same PR that lands or closes any of the five children.
- A test in tests/docs/test_semiconductor_lane_status.py asserts cross-link integrity at every CI run.

## Out-of-Scope Notes
- Production tapeout, foundry signoff, JEDEC/IPC compliance — not in lane scope.
- Wiki creation — deferred to per-child decision (currently zero pages).
```

The companion test will:

```
test_lane_status_references_all_five_children:
  read docs/reports/semiconductor-cad-fem-lane-status.md
  assert each of "#2508", "#2509", "#2510", "#2511", "#2512" appears at least once

test_lane_status_links_anchor_artifacts:
  read the lane-status doc
  assert it references docs/reports/semiconductor-cad-fem-knowledge-base.md
  assert it references data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml
  assert it references docs/roadmaps/chip-design-cad-fem-career-roadmap.md

test_lane_status_has_no_banned_compliance_claims:
  read the lane-status doc, lowercased
  for phrase in ["jedec compliant", "ipc compliant", "tapeout-ready", "tapeout ready",
                 "foundry signoff", "foundry-signoff", "production-certified semiconductor"]:
      assert phrase not in text  # guardrail against scope-creep claims

test_lane_status_quotes_kb_recommended_order:
  read the lane-status doc
  assert "#2508" appears before "#2511" appears before "#2510" appears
  before "#2509" appears before "#2512" (KB-recommended order #2508→#2511→#2510→#2509→#2512)
```

No production code paths change; the test is documentation-guardrail only.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/reports/semiconductor-cad-fem-lane-status.md | Lane-level operational status document — single source of truth for #2507 progress and lane-wide guardrails. |
| Create | tests/docs/test_semiconductor_lane_status.py | Guardrail tests asserting cross-link integrity, banned-claim absence, and KB-recommended order. |
| Modify | docs/plans/README.md | Add an index row for this plan (per `issue-planning-mode` SKILL Step 2 requirement). |
| Create | scripts/review/results/2026-04-27-plan-2507-claude.md | Adversarial review artifact (Claude). |
| Create | scripts/review/results/2026-04-27-plan-2507-codex.md | Adversarial review artifact (Codex). |
| Create | scripts/review/results/2026-04-27-plan-2507-gemini.md | Adversarial review artifact (Gemini). |
| Create (final) | docs/plans/2026-04-27-issue-2507-`2026-04-27-issue-2507-semiconductor-cad-fem-career-lane`.md | Canonical plan in repo (this draft is at `/tmp/overnight-plans/wave-3/issue-2507-plan.md`; user-approved final slug to be chosen at adoption time). |
| (NOT modify) | docs/roadmaps/chip-design-cad-fem-career-roadmap.md | Already covers narrative; lane-status doc complements rather than rewrites. |
| (NOT modify) | docs/reports/semiconductor-cad-fem-knowledge-base.md | Closed-child output; do not double-cite. |
| (NOT modify) | data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml | Closed-child output; do not double-cite. |
| (NOT modify) | tests/docs/test_semiconductor_kb.py | Sibling test; only the new test file is added. |
| (NOT create) | scripts/semiconductor/, tests/semiconductor/, data/semiconductor/ | Owned by #2509/#2510/#2511 plans; the umbrella does not pre-empt them. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_lane_status_file_exists | The lane-status document is present and non-empty | `docs/reports/semiconductor-cad-fem-lane-status.md` | File exists, size > 1 KB |
| test_lane_status_references_all_five_children | Lane status references each of #2508/#2509/#2510/#2511/#2512 at least once | Lane status file content | Each `#NNNN` substring present |
| test_lane_status_links_kb_report | Lane status links to the KB report | Lane status content | String `docs/reports/semiconductor-cad-fem-knowledge-base.md` present |
| test_lane_status_links_taxonomy_yaml | Lane status links to the taxonomy YAML | Lane status content | String `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml` present |
| test_lane_status_links_roadmap | Lane status links to the career roadmap | Lane status content | String `docs/roadmaps/chip-design-cad-fem-career-roadmap.md` present |
| test_lane_status_has_no_banned_compliance_claims | Lane status does not assert JEDEC/IPC compliance, tapeout readiness, or foundry signoff | Lowercased file content | None of {"jedec compliant", "ipc compliant", "tapeout-ready", "tapeout ready", "foundry signoff", "foundry-signoff", "production-certified semiconductor"} appears |
| test_lane_status_preserves_kb_recommended_order | First mention of children appears in KB-recommended order | Lane status content | `find("#2508") < find("#2511") < find("#2510") < find("#2509") < find("#2512")` for first occurrences |
| test_lane_status_acceptance_table_lists_five_gates | Acceptance section lists exactly the five lane-level gates from the umbrella issue body | Lane status content | Five distinct gate bullets present (research/taxonomy, EDA demo, CAD demo, FEM benchmark, application packet) |

---

## Acceptance Criteria

- [ ] `docs/reports/semiconductor-cad-fem-lane-status.md` exists and is git-tracked.
- [ ] `tests/docs/test_semiconductor_lane_status.py` exists, is git-tracked, and all its tests pass: `uv run pytest tests/docs/test_semiconductor_lane_status.py -v`.
- [ ] Existing semiconductor tests still pass: `uv run pytest tests/docs/test_semiconductor_kb.py -v`.
- [ ] Full suite passes: `uv run pytest tests/` (no regressions introduced).
- [ ] `docs/plans/README.md` has a new row for this plan with status reflecting the live label state.
- [ ] Three review artifacts under `scripts/review/results/2026-04-27-plan-2507-*.md` exist and are non-empty.
- [ ] `.planning/plan-approved/2507.md` marker exists (created by user at approval time, not by the implementing agent).
- [ ] (Lane-closure gate, separate from this plan's acceptance) The umbrella issue #2507 will only be CLOSED when all five children #2508/#2509/#2510/#2511/#2512 are CLOSED **and** the lane-status document marks every gate row TRUE. This plan delivers the gate document; it does not itself close the lane.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | To be filled after `scripts/review/results/2026-04-27-plan-2507-claude.md` is produced. |
| Codex | PENDING | To be filled after `scripts/review/results/2026-04-27-plan-2507-codex.md` is produced. |
| Gemini | PENDING | To be filled after `scripts/review/results/2026-04-27-plan-2507-gemini.md` is produced. |

**Overall result:** PENDING (re-draft expected if any provider returns MAJOR).

Revisions made based on review:
- (none yet — plan is in initial draft state)

---

## Risks and Open Questions

- **Risk: umbrella scope creep.** Future commits may try to attach implementation work to #2507 instead of opening a sixth child. **Mitigation:** lane-status doc states explicitly that all new lane work opens a new child issue; the test asserts the five-child structure.
- **Risk: lane-status drift.** The doc will lie if it is not updated when child state changes. **Mitigation:** the test guardrail catches absence of any child reference; reviewers must update lane-status in the same PR that lands a child closure. **Open question:** should a pre-commit hook block commits that close one of #2508-#2512 without touching lane-status? Defer to user during approval.
- **Risk: KB-recommended order test brittleness.** The KB recommends order #2508→#2511→#2510→#2509→#2512, but actual landing order has been #2508 (closed) → #2511 (closed) → others pending — i.e., consistent so far. If a child closes out-of-order in the future, the lane-status doc may want to record the deviation. **Mitigation:** the test asserts mention-order in the doc, not landing-order in reality. The doc author can add a "Deviations" subsection without breaking the test.
- **Risk: double-cite of #2508 KB content.** If lane-status restates the role taxonomy, future drift becomes likely. **Mitigation:** lane-status links to KB sections rather than restating them.
- **Risk: wiki-creation expectation.** Some reviewers may expect a semiconductor wiki to be created here. **Mitigation:** the lane-status doc explicitly records "no semiconductor wiki pages today, deferred to per-child decision" so the absence is intentional, not an oversight. **Open:** when (if ever) does the lane warrant a dedicated wiki domain? Defer to user.
- **Risk: redundant umbrella plan.** Reviewer may argue an umbrella issue does not need its own plan because all children already have plans. **Mitigation:** issue-planning-mode SKILL applies to ALL GitHub issues without exception; the deliverable here (lane-status doc + test) is a real artifact that does not exist anywhere else, not a procedural placeholder.
- **Open question:** should `docs/plans/README.md` carry a separate "Lane plans" section, or is a normal row sufficient? Defer to user during approval.
- **Open question:** does the user want `cat:documentation` added to #2507's labels (currently absent) given that the deliverable is a doc + a doc-test? Defer to user during approval.

---

## Complexity: T2

Justification: T2 — one new doc file plus one new test file, no production code changes, no new directory conventions, modifies one index file (`docs/plans/README.md`). The orchestration scope is narrow but the cross-reference / guardrail logic warrants TDD coverage, which is why this is T2 rather than T1.
