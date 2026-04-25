# Adversarial Plan Review — aceengineer-strategy #2 (Wedge Confirmation)

**Reviewer:** Claude (single-author r3, fallback per `feedback_permission_gate_blocks_cross_review.md`)
**Plan file:** `docs/plans/2026-04-25-aces-2-flywheel-wedge-mooring.md`
**Date:** 2026-04-25
**Stance:** Adversarial — assume defects until proven otherwise. No praise. No restatement.

---

## What I checked

1. Resource Intelligence Summary — source count, claim accuracy, gap honesty
2. File-existence claims (`docs/governance/` convention exists? `knowledge/seeds/mooring-failures-lng-terminals.yaml` exists?)
3. Decision content sufficiency for downstream issues to actually cite
4. Graduation criteria falsifiability
5. Rollback trigger specificity
6. Cross-reference graph closure (which downstream issues actually need this artifact?)

---

## Verdict: MINOR

The plan is structurally sound for a T1 decision artifact. Findings are non-blocking but should be patched before user approval.

---

## Findings

### F1 — MINOR: "40 entries" claim hedged but not resolved
**Plan §Resource Intelligence — Existing repo code:** plan acknowledges discrepancy ("memory references 40 entries... but actual file inventory is one YAML"). This is honest but leaves the corpus-size assumption hanging. Decision artifact mentions "corpus exists" without committing to a number. Acceptable for a decision plan, but the downstream #6 plan will inherit this ambiguity.

**Recommendation:** plan should explicitly defer corpus-size claim to #6 plan's resource-intel and add a note.

### F2 — MINOR: Graduation criterion #4 ("strategic free-tier client whose use materially advances the loop") is non-falsifiable
**Plan §Decision Content #5:** "1 strategic free-tier client whose use materially advances the loop" is too vague. "Materially advances" cannot be checked.

**Recommendation:** add specific operationalization: at least one of (a) public case study published with client logo, (b) ≥10 measurable telemetry data points fed into atlas calibration, (c) ≥1 standards-interpretation refinement with public attribution. Pick one or use as alternatives.

### F3 — MINOR: Rollback trigger time-window single-point
**Plan §Decision Content #6:** "if no anchor pilot signed within 12 months, OR if no atlas v1 published within 18 months." Two triggers, but no specification of *what to do* when triggered. "Reconsider wedge selection" is not a procedure.

**Recommendation:** specify the rollback procedure: who calls it, what artifact they produce, what the next decision-fork looks like. Otherwise the trigger is performative.

### F4 — MINOR: Cross-reference grep is one-directional
**Plan §TDD/Validation Checks:** "Cross-reference grep: `grep -r ... .` returns links from all P0–P3 plan files." Good, but the *forward* direction is also needed — the decision artifact should list which downstream issues are bound to it, so a reader of the artifact knows what depends on it.

**Recommendation:** add to acceptance criteria: "decision artifact contains an explicit 'binds:' or 'used-by:' list naming dependent issues."

### F5 — INFO: Issue #2 body has open user questions (time horizon, hard/soft rollback gate) that the plan punts to the user
**Plan §Risks/Open Questions:** plan correctly flags these as user-input-dependent. That means status:plan-review surfaces these to the user for decision, which is the right gate behavior. Not a defect.

---

## Empty-review check

Nothing found returning APPROVE without verification — see findings F1–F4 above. F5 is INFO not a defect.

---

## Cross-provider context

- **Codex:** UNAVAILABLE — codex-cli 0.124.0 broken upstream per `feedback_codex_cli_0_124_upstream_regression.md`; #2479 filed; workaround = downgrade to 0.123.0. This single-author Claude review is the documented fallback.
- **Gemini:** DEFERRED for this strategy plan; would add value primarily on the open-question framing, not on plan structure.

---

## Recommended action

1. Patch plan to address F2, F3, F4 inline before applying `status:plan-review` label.
2. F1 acknowledged; defer to #6 plan.
3. Plan is otherwise approval-ready as a decision-input plan; user input on open questions is the actual gate.
