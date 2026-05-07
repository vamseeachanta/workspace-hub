# Tier-1 GitHub Issue Kanban Board

Generated: 2026-05-06

## Scope

Scoped tier-1 repositories: `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `assethold`, `aceengineer-website`. Open issues are mapped into execution lanes; recent closed issues provide the Done lane sample.

## Executive totals

- Open issues mapped: **1189**
- Recent closed issues sampled: **349**
- Ready / Plan Approved open issues: **129**
- Approved-label drift repair items: **66**
- Plan review / approval decision items: **8**
- Planning-needed / future backlog items: **967**
- In-progress / status-working items: **15**
- Label conflicts: **0**

## Lane definitions for Hermes execution mapping

| Lane | Meaning | Execution rule |
|---|---|---|
| Ready / Plan Approved | Approved issues with plan and approval-marker evidence | Eligible for execution shortlist after repo worktree hygiene check |
| Approved Label Drift / Repair Before Execution | Has approval label but missing plan/approval evidence | Governance repair before worker launch |
| Plan Review / Needs Approval | Plan exists or is under review but not approved | User approval/review synthesis before execution |
| Planning Needed / Future Backlog | No status gate label | Intake, clustering, planning, or close/merge/rescope decision |
| In Progress / Status Working | Already assigned/active | Implementation-state audit before duplicate launch |
| Blocked / Waiting | Explicitly blocked/hold | Resolve blocker or park |
| Done / Recently Closed | Recent closed sample | Use for done-review and lessons learned |

## Repo × lane matrix (open issues)

| Repo | Blocked / Waiting | In Progress / Status Working | State Conflict / Hygiene | Plan Review / Needs Approval | Approved Label Drift / Repair Before Execution | Ready / Plan Approved | Other Status / Triage | Planning Needed / Future Backlog |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| workspace-hub | 1 | 14 | 0 | 7 | 4 | 3 | 3 | 783 |
| digitalmodel | 0 | 1 | 0 | 0 | 7 | 77 | 0 | 179 |
| assetutilities | 0 | 0 | 0 | 0 | 0 | 21 | 0 | 0 |
| worldenergydata | 0 | 0 | 0 | 1 | 55 | 1 | 0 | 0 |
| assethold | 0 | 0 | 0 | 0 | 0 | 27 | 0 | 0 |
| aceengineer-website | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |

## Agent route matrix (open issues)

| Agent route | Blocked / Waiting | In Progress / Status Working | State Conflict / Hygiene | Plan Review / Needs Approval | Approved Label Drift / Repair Before Execution | Ready / Plan Approved | Other Status / Triage | Planning Needed / Future Backlog |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agent:claude | 0 | 6 | 0 | 5 | 58 | 109 | 0 | 324 |
| agent:codex | 1 | 8 | 0 | 1 | 4 | 15 | 2 | 214 |
| agent:gemini | 0 | 1 | 0 | 2 | 4 | 5 | 1 | 93 |
| agent:any | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 336 |

## Repo × agent route (open issues)

| Repo | agent:claude | agent:codex | agent:gemini | agent:any |
| --- | --- | --- | --- | --- |
| workspace-hub | 234 | 204 | 79 | 298 |
| digitalmodel | 178 | 35 | 18 | 33 |
| assetutilities | 20 | 0 | 1 | 0 |
| worldenergydata | 48 | 5 | 4 | 0 |
| assethold | 22 | 1 | 4 | 0 |
| aceengineer-website | 0 | 0 | 0 | 5 |

## Recommended Hermes orchestration lanes

1. **Execution shortlist lane:** pull from `Ready / Plan Approved`, excluding `status:working`, and launch one issue per isolated worktree. Start with a small batch of 3–4 only.
2. **Governance repair lane:** repair `Approved Label Drift` before execution. In this snapshot, this is primarily approval-marker/plan evidence drift.
3. **Approval lane:** move `Plan Review / Needs Approval` through adversarial review synthesis and explicit user approval.
4. **Planning factory lane:** cluster `Planning Needed / Future Backlog` by repo/domain, close duplicates/stale items, and draft canonical plans for high-leverage clusters.
5. **Implementation-state audit lane:** audit `In Progress / Status Working` before assigning any duplicate workers.

## Dashboard artifact

Interactive board: `docs/dashboards/2026-05-06-tier1-gh-issue-kanban.html`

Data artifact: `docs/reports/2026-05-06-tier1-gh-issue-kanban-data.json`

## Notes

- This is a GitHub-label-derived board, not a separate manual queue. Labels remain the source of truth.
- Do not launch workers from label-only approved issues without approval evidence and local worktree hygiene checks.
