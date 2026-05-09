# Tier-1 GitHub Issue Kanban Board

Generated: 2026-05-09

## Lane counts

| Lane | Count |
| --- | ---: |
| Blocked / Waiting | 5 |
| In Progress / Status Working | 15 |
| State Conflict / Hygiene | 0 |
| Plan Review / Needs Approval | 20 |
| Approved Label Drift / Repair Before Execution | 83 |
| Ready / Plan Approved | 133 |
| Other Status / Triage | 23 |
| Planning Needed / Future Backlog | 984 |

## Scope

Scoped tier-1 repositories: `workspace-hub`, `digitalmodel`, `assetutilities`, `worldenergydata`, `llm-wiki`, `assethold`, `aceengineer-website`, `aceengineer-strategy`. `llm-wiki` is included as a tier-1 knowledge/retrieval repo in this refresh.

## Executive totals

- Open issues mapped: **1263**
- Recent closed issues sampled: **729**
- Ready / Plan Approved open issues: **133**
- Approved-label drift repair items: **83**
- Plan review / approval decision items: **20**
- Planning-needed / future backlog items: **984**
- In-progress / status-working items: **15**
- Label conflicts: **0**

## Methodology

1. Pull live open issues and a recent closed sample per repo with `gh issue list`.
2. Treat GitHub labels as source-of-truth state, then cross-check local plan artifacts and `.planning/plan-approved/<issue>.md` markers before calling anything execution-ready.
3. Build per-repo, per-domain/category, and special-lane review boards. These are views over the machine JSON, not a separate queue.
4. Route work into ~5-hour Hermes swarm windows by lane: execution-ready, governance repair, approval review, planning factory, status audit, or blocker triage.

## Lane definitions for Hermes execution mapping

| Lane | Meaning | Execution rule |
| --- | --- | --- |
| Ready / Plan Approved | Approved issues with plan and approval-marker evidence | Eligible for execution shortlist after repo/worktree hygiene check |
| Approved Label Drift / Repair Before Execution | Has approval label but missing plan/approval evidence | Governance repair before worker launch |
| Plan Review / Needs Approval | Plan exists or is under review but not approved | User approval/review synthesis before execution |
| Planning Needed / Future Backlog | No status gate label | Intake, clustering, planning, or close/merge/rescope decision |
| In Progress / Status Working | Already assigned/active | Implementation-state audit before duplicate launch |
| Blocked / Waiting | Explicitly blocked/hold | Resolve blocker or park |
| Done / Recently Closed | Recent closed sample | Use for done-review and lessons learned |

## Repo × lane matrix (open issues)

| Route | Blocked / Waiting | In Progress / Status Working | State Conflict / Hygiene | Plan Review / Needs Approval | Approved Label Drift / Repair Before Execution | Ready / Plan Approved | Other Status / Triage | Planning Needed / Future Backlog |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| workspace-hub | 1 | 14 | 0 | 7 | 5 | 4 | 3 | 783 |
| digitalmodel | 0 | 1 | 0 | 1 | 7 | 78 | 6 | 179 |
| assetutilities | 0 | 0 | 0 | 0 | 0 | 21 | 0 | 0 |
| worldenergydata | 0 | 0 | 0 | 2 | 54 | 2 | 0 | 0 |
| llm-wiki | 4 | 0 | 0 | 9 | 12 | 0 | 0 | 17 |
| assethold | 0 | 0 | 0 | 0 | 0 | 28 | 0 | 0 |
| aceengineer-website | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 5 |
| aceengineer-strategy | 0 | 0 | 0 | 1 | 4 | 0 | 14 | 0 |

## Agent route matrix (open issues)

| Route | Blocked / Waiting | In Progress / Status Working | State Conflict / Hygiene | Plan Review / Needs Approval | Approved Label Drift / Repair Before Execution | Ready / Plan Approved | Other Status / Triage | Planning Needed / Future Backlog |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agent:unassigned | 2 | 1 | 0 | 20 | 82 | 133 | 23 | 855 |
| agent:codex | 3 | 14 | 0 | 0 | 0 | 0 | 0 | 67 |
| agent:claude | 0 | 6 | 0 | 0 | 1 | 0 | 0 | 59 |
| agent:gemini | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 3 |

## Top domain/category routes

| Domain route | Open | Ready | Plan review | Approval drift | Planning needed |
| --- | ---: | ---: | ---: | ---: | ---: |
| unlabeled-domain | 373 | 69 | 3 | 24 | 262 |
| category:engineering | 367 | 50 | 4 | 39 | 263 |
| category:harness | 226 | 2 | 0 | 2 | 216 |
| category:documentation | 76 | 2 | 5 | 1 | 66 |
| category:operations | 67 | 1 | 1 | 1 | 62 |
| category:ai-orchestration | 58 | 2 | 0 | 0 | 52 |
| domain:knowledge-management | 48 | 0 | 10 | 0 | 32 |
| category:data | 46 | 6 | 0 | 26 | 14 |
| category:data-pipeline | 43 | 0 | 6 | 0 | 29 |
| domain:marine | 32 | 0 | 1 | 0 | 28 |
| category:engineering-calculations | 27 | 1 | 1 | 0 | 24 |
| domain:document-intelligence | 27 | 0 | 4 | 0 | 20 |
| domain:gtm | 23 | 0 | 0 | 0 | 23 |
| category:skills | 19 | 0 | 0 | 0 | 19 |
| category:business | 15 | 0 | 0 | 0 | 15 |
| category:infrastructure | 15 | 0 | 1 | 0 | 14 |
| domain:skills | 12 | 0 | 0 | 0 | 12 |
| domain:workflow | 12 | 0 | 0 | 0 | 12 |
| domain:frontend-design | 11 | 0 | 0 | 0 | 11 |
| domain:workstations | 11 | 1 | 0 | 0 | 10 |
| category:tooling | 10 | 0 | 1 | 0 | 9 |
| domain:code-promotion | 10 | 0 | 0 | 0 | 10 |
| category:research | 9 | 0 | 0 | 0 | 7 |
| domain:ai-orchestration | 9 | 1 | 0 | 0 | 8 |
| category:automation | 8 | 1 | 0 | 3 | 4 |
| category:maintenance | 8 | 1 | 0 | 0 | 7 |
| category:personal-finance | 8 | 0 | 0 | 0 | 8 |
| domain:naval-architecture | 8 | 4 | 1 | 0 | 3 |
| category:career | 7 | 0 | 0 | 0 | 7 |
| category:document-intelligence | 7 | 0 | 0 | 0 | 7 |
| domain:agent-cost-tracking | 6 | 1 | 0 | 0 | 5 |
| domain:ai-config | 6 | 0 | 0 | 0 | 6 |
| domain:cv-strategy | 6 | 0 | 0 | 0 | 6 |
| domain:pipeline | 6 | 0 | 0 | 0 | 6 |
| domain:release-management | 6 | 0 | 0 | 0 | 6 |
| domain:tax-preparation | 6 | 0 | 0 | 0 | 6 |
| domain:testing | 6 | 0 | 0 | 1 | 4 |
| domain:work-queue | 6 | 0 | 0 | 0 | 6 |
| category:platform | 5 | 0 | 0 | 0 | 5 |
| category:strategy | 5 | 0 | 0 | 0 | 5 |

## Gap signals and future-work heuristics

- Planning-needed heavy domains are the best candidates for a planning-factory swarm, not immediate implementation.
- Approval-label drift is a governance repair lane; do not launch implementation agents from those issues until plan/marker evidence is repaired.
- Unlabeled-domain issues should be triaged into domain/category labels before planning batches so portfolio gaps remain measurable.
- In-progress items need branch/PR/worker-state audits before new work is assigned, preventing duplicate agent launches.
- Recently closed samples should feed lessons learned and duplicate detection before creating new issue trees.

## Generated artifacts

- Machine data: `docs/reports/2026-05-09-tier1-gh-issue-kanban-data.json`
- HTML dashboard: `docs/dashboards/2026-05-09-tier1-gh-issue-kanban.html`
- Board index: `docs/reports/kanban/2026-05-09-board-index.md`

## Review lanes

Detailed lane review tables are split into the per-repo, special-lane, and domain/category boards linked from `docs/reports/kanban/2026-05-09-board-index.md`; the machine JSON and HTML dashboard are the uncapped source of truth.
