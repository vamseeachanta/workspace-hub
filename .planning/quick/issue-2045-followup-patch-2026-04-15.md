Follow-up #2045 patch wave landed locally after the latest Codex MAJOR:

Key repairs applied:
- added the new Claude artifact into the plan header and review history:
  - `scripts/review/results/2026-04-15-plan-2045-claude.md`
- removed the old "Claude missing" blocker from the plan text
- moved `.codex/CODEX.md` contradiction cleanup more clearly into implementation scope
- added an explicit `test_issue_2045_skill_alignment.sh` to cover the `issue-planning-mode` skill vs `AGENTS.md`
- tightened `test_issue_2045_operational_workflow.sh` to use issue #2045 as the concrete sample and `gh issue view 2045 --json comments,labels` as the evidence path
- clarified validation-only scope for `.codex/config.toml` vs `.codex/CODEX.md`
- strengthened policy-alignment and onboarding-doc checks to handle deprecated workflow references and canonical-contract references more explicitly

The plan is still not approval-ready yet, but this closes a meaningful portion of the latest Codex blocker set before the next re-review.
