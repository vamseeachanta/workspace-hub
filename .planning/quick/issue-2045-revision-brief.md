Revision brief for #2045 plan

The plan is not approval-ready and needs a targeted rewrite before user review.

Required revisions
1. Correct governance state in the header:
- change Status from plan-approved to draft or plan-review
- replace waived-review language with actual review artifacts
- do not imply approval already happened

2. Expand retrieval to meet the template baseline:
- docs/document-intelligence/README.md
- docs/standards/AI_REVIEW_ROUTING_POLICY.md
- docs/standards/SUBAGENT_CONTEXT_ISOLATION.md
- prior related plans in docs/plans/
- .claude/hooks/plan-approval-gate.sh
- agent-facing onboarding surfaces for Claude/Gemini/Hermes/Codex

3. Remove false blocker assumptions:
- delete claims that .claude/skills/ is blocked by the plan-approval gate
- remove acceptance criteria/risk language based on that false assumption
- the gate already whitelists */.claude/*

4. Make scope concrete:
- explicitly enumerate what “all agents” means operationally
- list every onboarding surface to be updated, or narrow the claim
- rewrite pseudocode around real discovery/review/label workflow rather than abstract doc updates

5. Replace TDD Test List: N/A with real validations:
- verify referenced onboarding docs/skills exist and align
- verify review-routing policy matches required Claude/Codex/Gemini review path
- verify gate safe-path assumptions against live hook behavior
- verify example plans use template + review artifacts correctly

6. Rewrite acceptance criteria:
- remove pre-checked boxes
- require real adversarial review evidence
- require corrected governance state before approval
- require baseline retrieval compliance
- require every claimed onboarding surface updated or scope narrowed
