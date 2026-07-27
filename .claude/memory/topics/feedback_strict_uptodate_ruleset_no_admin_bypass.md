> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-26
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_strict_uptodate_ruleset_no_admin_bypass.md

---
name: feedback_strict_uptodate_ruleset_no_admin_bypass
description: Merging a green PR blocked by strict-up-to-date ruleset on a churning main — --admin does NOT bypass rulesets; use a merge-when-CLEAN loop or add ruleset bypass
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d8161c1f-2dbe-4020-9d3d-496ca0461f92
---

When a green PR won't merge with "N of N required status checks are expected" and mergeStateStatus flips between BEHIND/BLOCKED even though all required checks pass, the blocker is the branch-ruleset's `strict_required_status_checks_policy: true` ("require branches up to date"), NOT a failing check.

**Why:** GitHub repository *rulesets* are separate from classic branch protection. `gh pr merge --admin` bypasses classic protection but does NOT bypass a ruleset unless the actor is in that ruleset's explicit **bypass-actor list**. So an org/repo admin still gets "Repository rule violations found" from `--admin`. Confirmed live 2026-07-04 on wed #771.

**How to apply:**
1. Diagnose: `gh api repos/<owner>/<repo>/rules/branches/main --jq '.[]|select(.type=="required_status_checks").parameters.strict_required_status_checks_policy'` → if `true`, and the required contexts all pass, the wall is up-to-date, not checks.
2. If main churns (feature merges / crons commit every few min–30 min), a single `update-branch` loses the race (new SHA → ~5 min CI → main moves → BEHIND again). Do NOT hand-chase (anti-pattern per [[feedback_dev_primary_equality_green_is_self_healing]]).
3. **Fastest reliable landing:** a background merge-when-CLEAN loop — poll `mergeStateStatus`; on `BEHIND` with checks done, re-`update-branch`; on `CLEAN|UNSTABLE`, `gh pr merge --squash` immediately. It seizes the first CLEAN window. This is how #771 landed (13:50Z).
4. **Durable fix (owner/admin, out-of-band — do NOT change rulesets autonomously; security-gate change routes to human per [[feedback_agent_cannot_enable_security_gate_bypass]]):** add the admin role to the ruleset's Bypass list (then `--admin` works), OR flip `strict_required_status_checks_policy` to false (the required checks re-run on main post-merge anyway, so strict adds little on a fast-moving main).
5. wed main cadence 2026-07-04 was ~28-32 min between commits → the loop wins in 1-2 cycles. On a truly fast main, prefer the ruleset bypass.

Related: [[project_ecosystem_review_2026_07_04]], [[feedback_agent_can_verify_but_not_self_merge_pr]], [[feedback_dev_primary_equality_green_is_self_healing]]
