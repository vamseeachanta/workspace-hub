# Plan for aceengineer-strategy #2: Wedge Confirmation — Approach C + Mooring as First Vertical

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/aceengineer-strategy/issues/2
> **Parent epic:** https://github.com/vamseeachanta/aceengineer-strategy/issues/1
> **Review artifacts:** scripts/review/results/2026-04-25-plan-aces-2-claude.md (pending)

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/` repo contains mature mooring analysis modules (OrcaFlex, OrcaWave, mooring system tools). Confirmed via repo listing 2026-04-25.
- Found: `knowledge/seeds/mooring-failures-lng-terminals.yaml` — at minimum one corpus file of mooring failures exists. Memory `project_mooring_failures_knowledge.md` references "40 entries at knowledge/seeds/" but actual file inventory is one YAML; broader corpus may be dispersed. Verify before declaring "40-case corpus" in implementation phase.
- Found: solver queue + overnight batch infrastructure (workspace-hub project memory `project_solver_queue_architecture.md`, `project_overnight_batch_runs.md`) supports parametric runs.
- Gap: no existing "flywheel wedge" decision artifact in workspace-hub `docs/governance/`.

### Standards

Not directly applicable to this decision plan; downstream issue #4 will industrialize DNV-OS-E301 + API RP 2SK.

### LLM Wiki pages consulted

- `knowledge/wikis/marine-engineering/` exists per `find` 2026-04-25; CSA Z276 routing decision in workspace-hub #2471 is adjacent but not authoritative for general standards.

### Documents consulted

- aceengineer-strategy issue #1 (epic body, decision log) — captures the public-by-default policy and Approach C recommendation.
- aceengineer-strategy issue #2 (this issue's body) — scope, dependencies.
- Workspace-hub project memory `project_field_dev_economics.md` (DONE), `project_field_dev_arch_patterns.md` (DONE) — alternative wedge candidates considered.
- SemiAnalysis website (https://semianalysis.com/) — comparable model fetched 2026-04-25 for analogy framing.

### Gaps identified

- No prior workspace-hub `docs/governance/` artifact captures wedge selection logic — must be created.
- No formal "graduation criteria" exists for moving from one vertical to the next.
- Rollback triggers (when do we abandon mooring as the wedge) are not yet specified.

### Evidence (embedded verification)

**Issue states** (verified 2026-04-25 via `gh issue view`):
- aceengineer-strategy `#1` — OPEN — "[Epic] Cradle-to-Grave Engineering Flywheel — Strategic Initiative"
- aceengineer-strategy `#2` — OPEN — "[P0] Wedge confirmation: Approach C + mooring as first vertical"

**File existence** (`ls` 2026-04-25):
- EXISTS: `knowledge/seeds/mooring-failures-lng-terminals.yaml`
- EXISTS: `digitalmodel/` (separate git repo)
- MISSING (this plan creates): `docs/governance/flywheel-wedge-decision.md`

**Source count:** 5 distinct sources above.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-25-aces-2-flywheel-wedge-mooring.md` |
| Decision artifact (created by this issue) | `docs/governance/flywheel-wedge-decision.md` |
| Plan review — Claude | `scripts/review/results/2026-04-25-plan-aces-2-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-25-plan-aces-2-codex.md` (deferred — codex-cli 0.124.0 broken upstream per `feedback_codex_cli_0_124_upstream_regression.md`) |
| Plan review — Gemini | `scripts/review/results/2026-04-25-plan-aces-2-gemini.md` (deferred — strategy doc, defer to user judgment) |

---

## Deliverable

A workspace-hub-tracked decision artifact at `docs/governance/flywheel-wedge-decision.md` that locks Approach C with mooring as the first vertical, defines graduation criteria for moving to vertical 2, defines rollback triggers, and is cited by all dependent flywheel issues (#3–#14).

---

## Pseudocode

T1 — trivial; see Files to Change.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/flywheel-wedge-decision.md` | Captures Approach C + mooring decision, graduation criteria, rollback triggers, time horizon |
| Update | `docs/plans/README.md` | Add row for this plan |

---

## Decision Content (to be written into `flywheel-wedge-decision.md`)

1. **Decision:** Approach C (closed-loop on one vertical end-to-end) chosen over Approach A (standards-first) and Approach B (calculators-first). Mooring vertical chosen as first wedge over riser, field-dev economics, naval architecture, integrity-management, and decommissioning.
2. **Rationale (why C over A, B):** A and B both produce publisher-tier outcomes. C is the only approach that exercises layers 6 (real-time assistance) and 7 (feedback loop), which is where the structural moat lives.
3. **Rationale (why mooring):** strongest existing asset base — `digitalmodel` mooring code mature, `knowledge/seeds/` mooring corpus exists, DNV-OS-E301 + API RP 2SK are well-bounded, operators currently lack credible mooring-integrity intelligence product.
4. **Time horizon:** 12–18 months on the mooring wedge before considering vertical 2.
5. **Graduation criteria** (all required to declare wedge proven):
   - Anchor pilot signed under default-publish telemetry agreement (#11)
   - Atlas v1 published publicly with paid integration tier live (#7, #8)
   - At least one full feedback-loop cycle closed and published to public log (#13)
   - Either: (a) 1 paying integration customer with executed MSA, OR (b) 1 strategic free-tier client meeting at least *one* of: (b1) public case study published with client logo + technical attribution, (b2) ≥10 measurable telemetry data points fed into atlas calibration, (b3) ≥1 standards-interpretation refinement with public attribution to the engagement.
6. **Rollback triggers and procedure:** if no anchor pilot signed within 12 months OR no atlas v1 published within 18 months, the rollback procedure is: (i) the user calls a wedge-review checkpoint via portfolio cadence #10; (ii) Claude session produces a wedge-review artifact at `docs/governance/flywheel-wedge-review-YYYYMM.md` summarizing what worked / what didn't / candidate alternative wedges; (iii) the user explicitly accepts or revises the wedge in the next decision-log entry on epic #1.
7. **Cross-references:** the artifact contains both directions:
   - `cites:` list — what other artifacts this decision cites (e.g., epic #1 decision log)
   - `binds:` list — which downstream issues are bound to this decision (specifically #3, #4, #5, #6, #7, #8, #11, #12, #13, #14)
   The `binds:` list lets a reader of the artifact know what depends on it without grepping the tree.

---

## TDD / Validation Checks

| Check | What it verifies |
|---|---|
| `flywheel-wedge-decision.md` exists at agreed path | File presence |
| Decision artifact contains all 7 sections (decision, rationale C-vs-AB, rationale mooring, time horizon, graduation, rollback, cross-refs) | Content completeness |
| Cross-reference grep: `grep -r "flywheel-wedge-decision.md" .` returns links from all P0–P3 plan files | Bidirectional linkage |
| Issue #2 body explicitly cites this artifact path in resolution comment | Closure traceability |

---

## Acceptance Criteria

- [ ] `docs/governance/flywheel-wedge-decision.md` created and committed
- [ ] All 7 decision sections populated with content from this plan
- [ ] `docs/plans/README.md` updated with this plan's row
- [ ] aceengineer-strategy issue #2 closure comment cites the artifact path
- [ ] Cross-references from at least #1 (epic), #3 (ICP — depends on wedge), and #4 (standards — depends on wedge) updated to cite the artifact

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self-r3) | MINOR | F1 (corpus-size hedge — deferred to #6 plan), F2 (graduation criterion (b) operationalized — fixed inline), F3 (rollback procedure specified — fixed inline), F4 (`binds:` list added to artifact — fixed inline), F5 (open user questions are correct gate behavior — INFO). See `scripts/review/results/2026-04-25-plan-aces-2-claude.md`. |
| Codex | UNAVAILABLE | codex-cli 0.124.0 broken upstream per `feedback_codex_cli_0_124_upstream_regression.md`; #2479 filed; workaround = downgrade to 0.123.0; deferred. Single-author Claude r3 is the documented fallback per `feedback_permission_gate_blocks_cross_review.md`. |
| Gemini | DEFERRED | strategy decision doc; cross-provider review adds limited value pre-user-input; recommend re-review after user fills decisions. |

**Overall result:** PASS (Claude MINOR, all findings patched inline; F1 acknowledged and deferred to downstream plan).

Revisions made based on review:
- §Decision Content #5: graduation criterion (b) replaced with falsifiable sub-criteria (b1/b2/b3).
- §Decision Content #6: rollback procedure (i)/(ii)/(iii) added; named the wedge-review artifact path.
- §Decision Content #7: artifact must contain both `cites:` and `binds:` lists; named the bound-issue set.

---

## Risks and Open Questions

- **Risk:** committing to mooring as the wedge for 12–18 months may foreclose faster wins in field-dev economics or naval architecture. Mitigation: rollback triggers are explicit; checkpoint at 12 months.
- **Risk:** "graduation criteria" is too strict and locks us out of expanding even when the loop is partially proven. Mitigation: criteria reviewed quarterly with portfolio management cadence (#10).
- **Open:** hard rollback gate or soft checkpoint? (Issue #2 lists this as an open user question.)

---

## Complexity: T1

T1 — single-file decision artifact, no code changes, no tests beyond presence/link validation. The work is in writing the decision content cleanly, not in implementation.
