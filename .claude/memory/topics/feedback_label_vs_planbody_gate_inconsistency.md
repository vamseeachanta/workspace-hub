> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-21
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_label_vs_planbody_gate_inconsistency.md

---
name: label-vs-planbody-gate-inconsistency
description: "When GitHub `status:plan-approved` label disagrees with the plan body's status field (label=approved + body=plan-review/MAJOR-blocked), halt dispatch and surface the gate inconsistency — do not rationalize the label alone as authorization"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d4fe73ec-6517-4e58-a943-20b6e6bd30f0
---

When triaging or dispatching against a `status:plan-approved`-labeled issue, **also verify the plan body's "Status:" line**. If the body still says `plan-review` / "fresh reviews MAJOR" / "not approval-ready" while the label says approved, the gate is INCONSISTENT — halt dispatch, surface to user with the unblock criteria. The label is not sufficient on its own when the plan author has explicitly warned against the current state.

**Why:** Tonight's triage (2026-05-15) re-encountered this exact pattern on three issues:
- [[issue-2626]] — label=`plan-approved`, body=`plan-review (fresh Codex/Gemini MAJOR; not approval-ready)`
- [[issue-2550]] — label=`plan-approved`, body=`plan-review` + "NEEDS FRESH RE-REVIEW after 2026-05-02 hardening"
- (Also [[issue-2510]] earlier — label=`plan-approved`, body=`plan-review` after 14 review rounds in sustained-MAJOR loop)

A prior 2026-05-11 session set the correct precedent for #2550 (commit [[commit-106e8d476]] / `docs/reports/2026-05-11-issue-2550-approval-blocker.md`): documented "Implementation was not started ... because the approval gate is inconsistent" and listed unblock criteria. Tonight's session honored that precedent across all three issues by halting + commenting + listing the same unblock criteria.

Without this rule the dispatcher (kanban-worker, /goal handlers, batch agents) would proceed on a label that the plan author themselves disagrees with — that's dispatch-as-rationalization-of-approval, the exact failure mode [[feedback_dispatch_local_marker_rationalization]] warns about.

**How to apply:**

1. **Before any dispatch action** on a `status:plan-approved` issue, read the plan body's `> **Status:** ...` line at the top.
2. **If the body says `plan-approved`** (matching the label): proceed.
3. **If the body says `plan-review` / "MAJOR" / "not approval-ready"**: HALT. Surface to user with the two-path unblock criteria:
   - (a) Rerun cross-review until verdicts are MINOR/PASS, then re-approve.
   - (b) User-in-loop explicit override: add truthful `.planning/plan-approved/<n>.md` marker with SHA + review-artifact paths + override reason; then the marker-label-parity gate (#2701/#2706) will accept.
4. **Recommend label cleanup**: if the user knows the label is stale, removing `status:plan-approved` until the body catches up keeps future dispatch attempts from re-discovering the same problem.
5. **Surface in the issue thread**: post a comment referencing the prior halt precedent + the specific unblock criteria. This makes the inconsistency discoverable at the GH-issue layer rather than requiring git-archaeology.

Cross-references:
- [[feedback_never_offer_to_self_label_plan_approved]] — never self-label, never pre-authorize via handoff
- [[feedback_dispatch_local_marker_rationalization]] — dispatch is NOT approval; agents must not write marker files
- [[feedback_codex_sustained_major_loop]] — when Codex sustains MAJOR for 3+ rounds, surface decision instead of auto-cycling (the upstream cause for many label-vs-body drifts)
- [[issue-2701]] — marker-label parity gate (forward direction: marker requires label)
- [[issue-2706]] — marker-label parity gate (reverse direction: label requires marker)
- 2026-05-11 [[commit-106e8d476]] — peer-precedent halt that set the bar
