# Flywheel Wedge Decision — Approach C + Mooring Vertical

> **Status:** LOCKED
> **Date:** 2026-04-26
> **Authority:** User-approved via aceengineer-strategy [#2](https://github.com/vamseeachanta/aceengineer-strategy/issues/2) `status:plan-approved` (label flipped 2026-04-26) + decision-panel acceptance ("continue with your defaults"). Local approval marker: `.planning/plan-approved/aces-2.md` (revision-bound to plan SHA `7af80b652`).
> **Plan:** [`docs/plans/2026-04-25-aces-2-flywheel-wedge-mooring.md`](../plans/2026-04-25-aces-2-flywheel-wedge-mooring.md)
> **Parent epic:** [aceengineer-strategy #1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1)

---

## 1. Decision

**Approach C** (closed-loop on one vertical, end-to-end through all 7 layers) is selected over Approach A (standards-first) and Approach B (calculators-first). **Mooring** is selected as the first vertical.

## 2. Rationale — Why Approach C over A and B

Approaches A and B both produce *publisher-tier* outcomes (best case: SemiAnalysis-for-marine). They strengthen layers 1–4 but never exercise layers 6 (real-time assistance) or 7 (feedback loop), which is where the structural moat lives. Approach C is the only approach where the loop actually closes; loop velocity is the thing competitors cannot replicate even with full read access to our public data.

## 3. Rationale — Why Mooring as Wedge

- `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` is mature production code.
- `knowledge/seeds/mooring-failures-lng-terminals.yaml` (and adjacent seed corpora) contains existing technical-attribution failure cases.
- DNV-OS-E301 (Position Mooring) + API RP 2SK (Stationkeeping Systems) are well-bounded standards with clear scope — small enough to industrialize as Phase 2 of [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) within the wedge time horizon.
- Operators (locked ICP per [`flywheel-icp-decision.md`](./flywheel-icp-decision.md)) currently lack a credible mooring-integrity intelligence product; market gap is real.
- The solver-queue + nightly-batch infrastructure (per workspace-hub `project_solver_queue_architecture.md`, `project_overnight_batch_runs.md`) supports the parametric-atlas computation needs of [aces-#8](https://github.com/vamseeachanta/aceengineer-strategy/issues/8) without new infra investment.

Alternatives considered and deferred: risers (good fit but `digitalmodel/drilling_riser/` is less mature), field-development economics ([aces-#14](https://github.com/vamseeachanta/aceengineer-strategy/issues/14) replication target — too broad as wedge), naval architecture (mooring is more discrete).

## 4. Time Horizon

**18 months** before considering vertical-2 expansion. Rationale: gives ≥3 quarterly feedback-loop cycles after first anchor pilot signs (typical operator pilot procurement cycle is 3–6 months), without risking momentum loss. Reviewed quarterly through the portfolio cadence ([aces-#10](https://github.com/vamseeachanta/aceengineer-strategy/issues/10)).

## 5. Graduation Criteria — All Required to Declare Wedge Proven

1. Anchor pilot signed under default-publish telemetry agreement ([aces-#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11)).
2. Atlas v1 published publicly with paid integration tier live ([aces-#7](https://github.com/vamseeachanta/aceengineer-strategy/issues/7), [aces-#8](https://github.com/vamseeachanta/aceengineer-strategy/issues/8)).
3. At least one full feedback-loop cycle closed and published to public log ([aces-#13](https://github.com/vamseeachanta/aceengineer-strategy/issues/13)).
4. Either: **(a)** 1 paying integration customer with executed MSA, **OR (b)** 1 strategic free-tier client meeting at least *one* of:
   - **(b1)** public case study published with client logo + technical attribution, OR
   - **(b2)** ≥10 measurable telemetry data points fed into atlas calibration, OR
   - **(b3)** ≥1 standards-interpretation refinement with public attribution to the engagement.

The (b)-path satisfies the public-by-default + flywheel-velocity-first motto: a free-tier client whose engagement materially advances the loop graduates the wedge as effectively as a paying one.

## 6. Rollback Triggers and Procedure

**Triggers** (any one fires the procedure):
- No anchor pilot signed within 12 months of this decision (i.e., by 2027-04-26)
- No atlas v1 published within 18 months of this decision (i.e., by 2027-10-26)

**Gate type:** **soft** — checkpoint with explicit review, not automatic wedge-change. The procedure forces the explicit reconsideration; the gate type lets the user accept context that justifies continuing.

**Procedure:**
1. User (or portfolio cadence [aces-#10](https://github.com/vamseeachanta/aceengineer-strategy/issues/10)) calls a wedge-review checkpoint.
2. Claude session produces a wedge-review artifact at `docs/governance/flywheel-wedge-review-YYYYMM.md` summarizing: what worked, what didn't, candidate alternative wedges (riser / field-dev econ / etc.), evidence for each alternative.
3. User explicitly accepts or revises the wedge in the next decision-log entry on epic [aces-#1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1). Continuing with the current wedge requires an explicit "continue mooring" decision; staying silent does not equal continuing.

## 7. Cross-References

### `cites:` (artifacts this decision relies on)

- aceengineer-strategy [#1](https://github.com/vamseeachanta/aceengineer-strategy/issues/1) (epic decision log, 2026-04-25 entries)
- workspace-hub commit `7af80b652` (plan landing) + `64a9167497` (decision-panel resolution)
- `docs/governance/2026-04-25-cradle-to-grave-engineering-flywheel-design.md` (companion design spec)

### `binds:` (issues bound to this decision — wedge change requires their concurrence)

- [aces-#3](https://github.com/vamseeachanta/aceengineer-strategy/issues/3) — ICP confirmation (operators chosen because of mooring fit)
- [aces-#4](https://github.com/vamseeachanta/aceengineer-strategy/issues/4) — Standards canonical home (DNV-OS-E301 + API RP 2SK chosen because of mooring)
- [aces-#5](https://github.com/vamseeachanta/aceengineer-strategy/issues/5) — Public mooring quick-screen calculator
- [aces-#6](https://github.com/vamseeachanta/aceengineer-strategy/issues/6) — Public failure-case browser (mooring corpus first)
- [aces-#7](https://github.com/vamseeachanta/aceengineer-strategy/issues/7) — Mooring failure intelligence integration product
- [aces-#8](https://github.com/vamseeachanta/aceengineer-strategy/issues/8) — Mooring parametric atlas API
- [aces-#11](https://github.com/vamseeachanta/aceengineer-strategy/issues/11) — Anchor pilot client (operator with mooring assets)
- [aces-#12](https://github.com/vamseeachanta/aceengineer-strategy/issues/12) — Real-time mooring monitoring copilot
- [aces-#13](https://github.com/vamseeachanta/aceengineer-strategy/issues/13) — Feedback-loop pipeline (mooring telemetry → atlas/standards)
- [aces-#14](https://github.com/vamseeachanta/aceengineer-strategy/issues/14) — Replication harness (post-mooring; hard-blocked on this wedge proving)

A wedge change (e.g., switching to risers) requires explicit reconcile of all 10 issues above — mooring-specific scope, plans, and references would all need amendment.
