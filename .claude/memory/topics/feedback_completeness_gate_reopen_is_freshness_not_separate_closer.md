> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-29
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_completeness_gate_reopen_is_freshness_not_separate_closer.md

---
name: feedback_completeness_gate_reopen_is_freshness_not_separate_closer
description: "completeness gate (#2798) reopens on label-freshness/authorized-owner, NOT separate-closer (opt-in, default off); verify check.py before asking user to flip a CI var"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 125ef504-cd50-421e-a7c5-e585a8805650
---

The #2798 completeness gate's reopen is almost never the separate-closer rule. Verified by reading `scripts/workflow/completeness_gate_check.py:evaluate_close` + `completeness_gate_runner.py:100` on origin/main (2026-05-28).

**Why:** `require_separate_closer` defaults `False` and is read as `os.environ.get("COMPLETENESS_REQUIRE_SEPARATE_CLOSER","").lower() in ("1","true","yes")` — unset → `False`, so it never blocks a solo operator. The real blockers, in order: record missing/unbound `issue_number`; unknown `cls` (only `code`=90, `evidence`=80 in DEFAULT_THRESHOLDS); `status:completeness-verified` absent OR applied by an actor not in `COMPLETENESS_OWNERS` var; **`body_verified_fresh`** — the verified label must be applied AT/AFTER the body's `lastEditedAt` (anchors on `lastEditedAt`, not `updatedAt`, per fix #5, so the close itself won't false-fail). #2845/#2846 reopened because the label predated the last body edit; re-applying the label after the edit (then re-closing) fixed it with zero config change.

**How to apply:** before asking the user to change any `COMPLETENESS_*` CI var, read the gate source and pull the actual label-event time vs `lastEditedAt` (`gh api .../timeline` + `gh api graphql {issue{lastEditedAt}}`). The 2026-05-28 orchestrator-consistency handoff misdiagnosed this as separate-closer; don't trust a handoff's gate diagnosis over the live check logic. Corrects [[project_orchestrator_consistency_decisions]].
