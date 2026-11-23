Revision brief for #2018 plan

The current plan needs a substantive rewrite before it can return to approval-ready status.

Required revisions
1. Rewrite front matter and review summary:
- remove approval-ready language
- replace old subagent-only review summary with current blocking reviews:
  - scripts/review/results/2026-04-14-plan-2018-codex.md
  - scripts/review/results/2026-04-14-plan-2018-gemini.md
- mark the plan as MAJOR / not approval-ready

2. Expand retrieval to full live enforcement surface:
- .github/workflows/enforcement-gate.yml
- .claude/hooks/cross-review-gate.sh
- scripts/enforcement/compliance-dashboard.sh
- .claude/hooks/plan-approval-gate.sh
- scripts/enforcement/require-plan-approval.sh
- scripts/enforcement/require-review-on-push.sh
- current issue comments/history
- provider-specific bootstrap/prefill/config surfaces for Hermes, Claude, Codex, and Gemini

3. Replace parent-inventory framing with real bypass-closure framing:
- add a bypass matrix covering runtime hook, pre-commit, pre-push, CI, approval marker spoofing, env-var bypasses, safe-path abuse, manual git path, and agent bootstrap paths
- for each row: current control, known bypass, required fix/proof, and test evidence

4. Replace document-centric TDD with functional enforcement tests:
- blocked write without marker
- blocked commit under strict mode
- blocked push/PR without review evidence
- CI failure without plan/review evidence
- env-var bypass attempts
- safe-path/control-plane exemption abuse
- self-approved marker spoofing
- per-agent validation across Hermes/Claude/Codex/Gemini
- rollback behavior or mandatory rollback child-issue split

5. Resolve, do not defer, rollback:
- either include a concrete rollback design and tests
- or explicitly re-scope #2018 and create a mandatory child issue before approval

6. Add a boundary table against sibling issues so #2018 cannot be closed by documentation alone.
