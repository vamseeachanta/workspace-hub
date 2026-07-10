> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_completeness_score_before_closure.md

---
name: feedback-completeness-score-before-closure
description: User requirement 2026-05-25 — all completed work must carry a test-based completeness score (0-100%) the user can review/rank BEFORE issue closure; all progress documented in HTML artifacts per the repo ecosystem.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e9bcfa5b-c1dc-4596-834b-bda6539efc25
---

User requirement, 2026-05-25: **"For all work completed, the user should be able to
rank or evaluate the completeness (0% to 100%) based on tests prior to issue closure.
All the progress should be documented in HTML artifacts per the repo ecosystem."**

**Why:** the user is operationalizing autonomous work (Hermes kanban dispatch — see
[[project_kanban_ecosystem_runaway_state]]). Closure needs an objective, test-grounded
completeness signal the user reviews, not agent self-report, and the evidence must be
durable + scannable (HTML).

**How to apply:**
1. **Every completed work item gets a completeness % (0–100), derived from TEST/verification
   evidence** — for code: test pass-rate + coverage delta + acceptance-criteria checklist;
   for ops/infra: live-probe evidence. Score adversarially, not charitably (per
   [[feedback_adversarial_review_stance]]).
2. **The score gates closure.** Insert a review point between Cross-review and Close in the
   existing flow ([[project_gsd_migration]] gates). Owner confirms ≥ threshold (default 90%)
   before `gh issue close`. Owner may override the % DOWN, never silently up.
3. **Document in HTML** under `docs/reports/<date>-<issue>-completeness.html` per
   [[feedback_html_default_artifact]]. Storage hook: `hermes kanban complete --metadata
   '{"completeness_pct":N,"evidence":...}'` and/or the issue body.
4. **Building the enforcement gate itself goes through the mandatory planning flow** (Issue →
   Plan → Approve → Implement) — do NOT bolt it on. Enforcement-gradient target:
   prose rule → `scripts/enforcement/check-completeness-before-close.*` → pre-close hook.

**Prototype delivered 2026-05-25:** `docs/reports/2026-05-25-session-completeness-scorecard.html`
(committed `f262d38b0`) — scores this session's 6 work items against probe/test evidence
(aggregate 99%), and carries the reusable rubric + owner-override column.

**SHIPPED 2026-05-26:** implemented + merged via PR #2800 (`scripts/workflow/completeness_score.py`,
`completeness_gate_check.py`, `completeness_gate_runner.py`, `.github/workflows/completeness-gate.yml`,
`scripts/enforcement/check-completeness-before-close.sh`, `render_completeness_html.py`, rule
`.claude/rules/completeness-before-close.md`). Both gates passed adversarial review (plan + code,
Claude+Codex MAJOR each → fixed inline).

**ROLLOUT LESSON (generalizable — applies to ANY fail-closed enforcement gate):** PR #2800 merged a
gate that fired on its OWN issue — `COMPLETENESS_OWNERS` was unset and the owners-config check ran
*before* the scope filter, so it fail-closed and reopened #2798 (and would have bounced every
`state_reason==completed` close repo-wide). **Always ship an enforcement gate (a) OPT-IN** (an explicit
label like `gate:completeness`, not retroactively over the whole backlog) **and (b) INERT WHEN
UNCONFIGURED** (scope/opt-in check BEFORE any required-config check, so a missing config variable
doesn't block unrelated work). Fixed in PR #2803.

**SOLO-OPERATION LESSON (PR #2807, found by dogfooding #2798 through its own gate):** the
code-review hardening added a `verifier != closer` rule (stop a closing bot self-verifying). But
that makes the gate **unsatisfiable for a solo operator** — the same person verifies + closes →
DENY. The authorized-appliers check already guarantees an OWNER applied the verified label (the
real human gate), so **separation-of-duties must be OPT-IN, not default** (`COMPLETENESS_REQUIRE_SEPARATE_CLOSER=1`
for teams; default solo-friendly). Generalizable: don't bake team-shaped separation-of-duties into
controls a solo operator must pass. The required repo variable (`COMPLETENESS_OWNERS`)
is now set to `vamseeachanta`; the `status:completeness-verified` label still needs a repo ruleset
restricting who can apply it before graduating beyond opt-in.

Related: [[feedback_html_default_artifact]], [[feedback_adversarial_review_stance]],
[[project_kanban_ecosystem_runaway_state]], [[feedback_pre_completion_cleanup_audit_gate]].
