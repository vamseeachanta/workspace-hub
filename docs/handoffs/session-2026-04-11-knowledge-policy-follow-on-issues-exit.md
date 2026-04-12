# Exit Handoff — knowledge policy follow-on issues and session wrap-up

Date: 2026-04-11
Repo: `/mnt/local-analysis/workspace-hub`

## Summary
This exit pass converted the main follow-on implementation surfaces from the durable/transient knowledge policy (#2209) into concrete GitHub issues and recorded the resulting next-step queue.

## GitHub issues created

1. #2233 — feat(knowledge): add `promoted_from` frontmatter field to wiki schema and validation guidance
   - https://github.com/vamseeachanta/workspace-hub/issues/2233
   - Purpose: make promotion provenance explicit in durable wiki artifacts.

2. #2234 — chore(workflow): update session-start-routine to treat handoffs as unverified context
   - https://github.com/vamseeachanta/workspace-hub/issues/2234
   - Purpose: stop handoff artifacts from being treated as authoritative durable knowledge.

3. #2235 — chore(plans): add retention metadata section to issue plan template
   - https://github.com/vamseeachanta/workspace-hub/issues/2235
   - Purpose: give plans explicit retention/expiry metadata aligned with #2209.

4. #2236 — chore(workflow): add post-closure promotion step to issue-planning-mode
   - https://github.com/vamseeachanta/workspace-hub/issues/2236
   - Purpose: route validated findings out of issues into durable knowledge after closeout.

5. #2237 — feat(automation): build transient-artifact cleanup and archival workflow for handoffs and planning state
   - https://github.com/vamseeachanta/workspace-hub/issues/2237
   - Purpose: turn #2209 retention rules into cleanup/archive automation.

6. #2238 — feat(conformance): add closed-issue citation guardrail so durable docs reference promoted knowledge instead
   - https://github.com/vamseeachanta/workspace-hub/issues/2238
   - Purpose: prevent closed issues from becoming de facto durable knowledge sources.

## Existing related issues already in place
- #2205 parent operating model
- #2206 conformance checks against the intelligence pyramid
- #2207 provenance + reuse contract
- #2209 durable/transient boundary policy
- #2139 weekly review artifact schema and canonical output layout

## Suggested execution order
1. #2233 — wiki schema support for `promoted_from`
2. #2234 — session-start handoff verification guidance
3. #2235 — plan-template retention metadata
4. #2236 — post-closure promotion step in issue workflow
5. #2237 — transient artifact cleanup/archive automation
6. #2238 — closed-issue citation guardrail

## Notes from validation runs
- #2205, #2207, and #2209 deliverables were already present/validated and had GitHub summary comments posted.
- All three still lack local plan approval marker files under `.planning/plan-approved/`:
  - `.planning/plan-approved/2205.md`
  - `.planning/plan-approved/2207.md`
  - `.planning/plan-approved/2209.md`
- This was not blocking validation because relevant deliverables were already committed via auto-sync, but it remains a workflow hygiene gap.

## Temporary execution artifacts created during this session
- `tmp/file-based-claude-bash-agent-teams-prompt-2207.md`
- `tmp/run_claude_agent_team_2207.sh`
- `tmp/file-based-claude-bash-agent-teams-prompt-2209.md`
- `tmp/run_claude_agent_team_2209.sh`
- `tmp/claude-agent-team-2205-implement.prompt.md`
- `tmp/run_claude_agent_team_2205.sh`
- `tmp/future-2209-issues/*.md` body files used for `gh issue create`

## Recommended next actions after exit
A. Create the missing `.planning/plan-approved/{2205,2207,2209}.md` markers.
B. Decide whether to clean or keep the temporary `tmp/` prompt/runner artifacts.
C. Start planning on the newly created issues beginning with #2233.

## Exit state
- Future follow-on issues created successfully.
- Exit handoff documented.
- No additional implementation performed in this pass.
