# Tier-1 GitHub Issue Kanban Board

Generated: 2026-05-06

## Scope

Scoped tier-1 repositories: `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `assethold`, `aceengineer-website`, `aceengineer-strategy`. `aceengineer-strategy` is included as the GTM strategy tier-1 repo in this refresh.

## Executive totals

- Open issues mapped: **1205**
- Recent closed issues sampled: **199**
- Ready / Plan Approved open issues: **128**
- Approved-label drift repair items: **69**
- Plan review / approval decision items: **10**
- Planning-needed / future backlog items: **968**
- In-progress / status-working items: **15**
- Label conflicts: **0**

## Lane definitions for Hermes execution mapping

| Lane | Meaning | Execution rule |
| --- | --- | --- |
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
| digitalmodel | 0 | 1 | 0 | 1 | 7 | 76 | 0 | 179 |
| assetutilities | 0 | 0 | 0 | 0 | 0 | 21 | 0 | 0 |
| worldenergydata | 0 | 0 | 0 | 1 | 55 | 1 | 0 | 1 |
| assethold | 0 | 0 | 0 | 0 | 0 | 27 | 0 | 0 |
| aceengineer-website | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| aceengineer-strategy | 0 | 0 | 0 | 1 | 3 | 0 | 11 | 0 |

## Agent route matrix (open issues)

| Agent route | Blocked / Waiting | In Progress / Status Working | State Conflict / Hygiene | Plan Review / Needs Approval | Approved Label Drift / Repair Before Execution | Ready / Plan Approved | Other Status / Triage | Planning Needed / Future Backlog |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agent:claude | 0 | 6 | 0 | 7 | 7 | 14 | 11 | 553 |
| agent:codex | 1 | 8 | 0 | 2 | 17 | 37 | 3 | 268 |
| agent:any | 0 | 1 | 0 | 0 | 44 | 76 | 0 | 141 |
| agent:gemini | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 6 |

## Top domain/category routes

| Domain route | Open | Ready | Plan review | Approval drift | Planning needed |
| --- | --- | --- | --- | --- | --- |
| category:engineering | 284 | 46 | 2 | 27 | 204 |
| unlabeled-domain | 204 | 29 | 0 | 10 | 165 |
| category:harness | 142 | 0 | 0 | 0 | 136 |
| domain:marine | 73 | 19 | 1 | 4 | 46 |
| category:operations | 62 | 0 | 0 | 0 | 60 |
| category:documentation | 46 | 0 | 0 | 0 | 45 |
| domain:document-intelligence | 42 | 3 | 1 | 0 | 36 |
| category:ai-orchestration | 34 | 0 | 0 | 0 | 30 |
| category:data | 32 | 6 | 0 | 24 | 2 |
| domain:ai-orchestration | 32 | 5 | 0 | 0 | 27 |
| domain:repo-governance | 29 | 6 | 0 | 3 | 20 |
| domain:testing | 29 | 4 | 0 | 4 | 20 |
| domain:gtm | 28 | 1 | 0 | 0 | 27 |
| domain:knowledge-management | 24 | 0 | 2 | 0 | 20 |
| category:engineering-calculations | 23 | 1 | 0 | 0 | 21 |
| category:data-pipeline | 17 | 0 | 0 | 0 | 16 |
| domain:gtm-strategy | 15 | 0 | 1 | 3 | 0 |
| domain:workflow | 12 | 0 | 0 | 0 | 12 |
| domain:skills | 12 | 0 | 0 | 0 | 12 |
| domain:workstations | 11 | 1 | 0 | 0 | 10 |
| domain:frontend-design | 11 | 0 | 0 | 0 | 11 |
| category:infrastructure | 10 | 0 | 0 | 0 | 10 |
| domain:code-promotion | 10 | 0 | 0 | 0 | 10 |
| category:document-intelligence | 7 | 0 | 0 | 0 | 7 |
| domain:naval-architecture | 7 | 4 | 0 | 0 | 3 |

## Board views created for review

- General dashboard: `docs/dashboards/2026-05-06-tier1-gh-issue-kanban.html`
- Board index: `docs/reports/2026-05-06-tier1-board-index.md`
- Per-repo boards: `docs/reports/kanban/2026-05-06-repo-*-kanban.md` (**7 files**) 
- Domain boards: `docs/reports/kanban/2026-05-06-domain-*-kanban.md` (**16 files currently written for top/explicit review domains**)
- Planning board: `docs/reports/kanban/2026-05-06-planning-needed-kanban.md`
- Execution board: `docs/reports/kanban/2026-05-06-execution-ready-kanban.md`
- Drift repair board: `docs/reports/kanban/2026-05-06-approval-drift-kanban.md`

## Notes

- This is a GitHub-label-derived board set, not a separate manual queue. Labels remain the source of truth.
- Markdown board files are review surfaces and may cap long lane item lists; full issue rows are in the machine-readable JSON and HTML dashboard.
- Do not launch workers from label-only approved issues without approval evidence and local worktree hygiene checks.
