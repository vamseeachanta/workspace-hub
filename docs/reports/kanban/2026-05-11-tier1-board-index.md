# Tier-1 Repository Kanban Board Index

Generated: 2026-05-11

Source: live `gh issue list --state open --limit 1000` for the eight tier-1 repos. Machine data: `../2026-05-11-tier1-kanban-board-data.json`.

## Operating contract

- Every open issue is mapped to a lifecycle lane, domain board, AI provider/reviewer route, and machine route.
- User decisions stay visible in **Decision / User Input** and **Plan Review / Cross-Review** lanes; implementation must not start until actioned.
- Repo file structure, tests, and CI/CD hygiene are standing acceptance gates for every implementation issue.
- Plans and artifacts require cross-review before closeout; default owner is Claude orchestration with Codex/Gemini adversarial support.
- `ace-linux-1` remains the control surface; `ace-linux-2` is overflow only after fresh readiness/auth/worktree checks.

## Portfolio lane matrix

| Repo | Decision / User Input | In Progress / Active | Plan Review / Cross-Review | Ready / Plan Approved | Triage / Intake | Planning Needed | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| workspace-hub | 3 | 11 | 7 | 8 | 23 | 765 | 817 |
| digitalmodel | 0 | 1 | 0 | 85 | 1 | 184 | 271 |
| assetutilities | 0 | 0 | 0 | 19 | 0 | 0 | 19 |
| worldenergydata | 0 | 0 | 2 | 54 | 0 | 0 | 56 |
| llm-wiki | 4 | 0 | 3 | 12 | 0 | 17 | 36 |
| assethold | 0 | 0 | 0 | 27 | 0 | 0 | 27 |
| aceengineer-website | 0 | 0 | 0 | 0 | 0 | 5 | 5 |
| aceengineer-strategy | 0 | 0 | 0 | 4 | 0 | 16 | 20 |

## Portfolio provider/machine defaults

| Lifecycle segment | Primary provider | Review/cross-review | Machine |
| --- | --- | --- | --- |
| Intake / planning | Claude planner + Gemini research | Claude synthesis | ace-linux-1 |
| Plan review / decisions | Claude | Gemini/Codex adversarial review as scaled | ace-linux-1 control surface |
| Approved implementation | Codex primary for bounded code/tests; Claude for orchestration | Claude/Codex/Gemini based on risk | ace-linux-1, with ace-linux-2 overflow after readiness |
| Hygiene / tests / CI | Codex primary | Claude reviewer | owning repo worktree on ace-linux-1 |
| GTM/content | Claude primary; Codex for site/build edits | Gemini research/copy-risk review | ace-linux-1 |

## Repo boards

- [workspace-hub](2026-05-11-repo-workspace-hub-kanban.md) — 817 open issues
- [digitalmodel](2026-05-11-repo-digitalmodel-kanban.md) — 271 open issues
- [assetutilities](2026-05-11-repo-assetutilities-kanban.md) — 19 open issues
- [worldenergydata](2026-05-11-repo-worldenergydata-kanban.md) — 56 open issues
- [llm-wiki](2026-05-11-repo-llm-wiki-kanban.md) — 36 open issues
- [assethold](2026-05-11-repo-assethold-kanban.md) — 27 open issues
- [aceengineer-website](2026-05-11-repo-aceengineer-website-kanban.md) — 5 open issues
- [aceengineer-strategy](2026-05-11-repo-aceengineer-strategy-kanban.md) — 20 open issues

## Domain boards generated per repo

### workspace-hub

- [domain:orchestration](2026-05-11-repo-workspace-hub-domain-domain-orchestration-kanban.md) — 216
- [cat:engineering](2026-05-11-repo-workspace-hub-domain-cat-engineering-kanban.md) — 79
- [cat:operations](2026-05-11-repo-workspace-hub-domain-cat-operations-kanban.md) — 60
- [cat:documentation](2026-05-11-repo-workspace-hub-domain-cat-documentation-kanban.md) — 43
- [cat:harness](2026-05-11-repo-workspace-hub-domain-cat-harness-kanban.md) — 41
- [cat:ai-orchestration](2026-05-11-repo-workspace-hub-domain-cat-ai-orchestration-kanban.md) — 33
- [domain:marine](2026-05-11-repo-workspace-hub-domain-domain-marine-kanban.md) — 28
- [domain:document-intelligence](2026-05-11-repo-workspace-hub-domain-domain-document-intelligence-kanban.md) — 23
- [domain:gtm](2026-05-11-repo-workspace-hub-domain-domain-gtm-kanban.md) — 23
- [cat:engineering-calculations](2026-05-11-repo-workspace-hub-domain-cat-engineering-calculations-kanban.md) — 21
- [domain:knowledge-management](2026-05-11-repo-workspace-hub-domain-domain-knowledge-management-kanban.md) — 20
- [cat:data-pipeline](2026-05-11-repo-workspace-hub-domain-cat-data-pipeline-kanban.md) — 13
- [domain:skills](2026-05-11-repo-workspace-hub-domain-domain-skills-kanban.md) — 12
- [domain:workflow](2026-05-11-repo-workspace-hub-domain-domain-workflow-kanban.md) — 12
- [domain:frontend-design](2026-05-11-repo-workspace-hub-domain-domain-frontend-design-kanban.md) — 11
- [domain:code-promotion](2026-05-11-repo-workspace-hub-domain-domain-code-promotion-kanban.md) — 10
- [cat:infrastructure](2026-05-11-repo-workspace-hub-domain-cat-infrastructure-kanban.md) — 9
- [domain:ai-orchestration](2026-05-11-repo-workspace-hub-domain-domain-ai-orchestration-kanban.md) — 8
- [cat:document-intelligence](2026-05-11-repo-workspace-hub-domain-cat-document-intelligence-kanban.md) — 7
- [cat:skills](2026-05-11-repo-workspace-hub-domain-cat-skills-kanban.md) — 7
- [domain:ai-config](2026-05-11-repo-workspace-hub-domain-domain-ai-config-kanban.md) — 6
- [domain:cv-strategy](2026-05-11-repo-workspace-hub-domain-domain-cv-strategy-kanban.md) — 6
- [domain:pipeline](2026-05-11-repo-workspace-hub-domain-domain-pipeline-kanban.md) — 6
- [domain:release-management](2026-05-11-repo-workspace-hub-domain-domain-release-management-kanban.md) — 6
- [domain:tax-preparation](2026-05-11-repo-workspace-hub-domain-domain-tax-preparation-kanban.md) — 6
- [domain:testing](2026-05-11-repo-workspace-hub-domain-domain-testing-kanban.md) — 6
- [domain:work-queue](2026-05-11-repo-workspace-hub-domain-domain-work-queue-kanban.md) — 6
- [domain:workstations](2026-05-11-repo-workspace-hub-domain-domain-workstations-kanban.md) — 6
- [domain:repo-organization](2026-05-11-repo-workspace-hub-domain-domain-repo-organization-kanban.md) — 5
- [domain:session](2026-05-11-repo-workspace-hub-domain-domain-session-kanban.md) — 5
- [domain:uncategorised](2026-05-11-repo-workspace-hub-domain-domain-uncategorised-kanban.md) — 5
- [domain:ai-tools](2026-05-11-repo-workspace-hub-domain-domain-ai-tools-kanban.md) — 4
- [domain:semiconductor](2026-05-11-repo-workspace-hub-domain-domain-semiconductor-kanban.md) — 4
- [domain:cleanup](2026-05-11-repo-workspace-hub-domain-domain-cleanup-kanban.md) — 3
- [domain:cross-platform](2026-05-11-repo-workspace-hub-domain-domain-cross-platform-kanban.md) — 3
- [domain:data-pipeline](2026-05-11-repo-workspace-hub-domain-domain-data-pipeline-kanban.md) — 3
- [domain:naval-architecture](2026-05-11-repo-workspace-hub-domain-domain-naval-architecture-kanban.md) — 3
- [domain:security](2026-05-11-repo-workspace-hub-domain-domain-security-kanban.md) — 3
- [domain:structural](2026-05-11-repo-workspace-hub-domain-domain-structural-kanban.md) — 3
- [cat:harness/ops](2026-05-11-repo-workspace-hub-domain-cat-harness-ops-kanban.md) — 2
- [cat:harness/skills](2026-05-11-repo-workspace-hub-domain-cat-harness-skills-kanban.md) — 2
- [domain:calculation-examples](2026-05-11-repo-workspace-hub-domain-domain-calculation-examples-kanban.md) — 2
- [domain:hydrodynamics](2026-05-11-repo-workspace-hub-domain-domain-hydrodynamics-kanban.md) — 2
- [domain:integrations](2026-05-11-repo-workspace-hub-domain-domain-integrations-kanban.md) — 2
- [domain:ops](2026-05-11-repo-workspace-hub-domain-domain-ops-kanban.md) — 2
- [domain:terminal](2026-05-11-repo-workspace-hub-domain-domain-terminal-kanban.md) — 2
- [cat:analysis](2026-05-11-repo-workspace-hub-domain-cat-analysis-kanban.md) — 1
- [cat:ci](2026-05-11-repo-workspace-hub-domain-cat-ci-kanban.md) — 1
- [cat:data](2026-05-11-repo-workspace-hub-domain-cat-data-kanban.md) — 1
- [cat:harness/session](2026-05-11-repo-workspace-hub-domain-cat-harness-session-kanban.md) — 1
- [cat:maintenance](2026-05-11-repo-workspace-hub-domain-cat-maintenance-kanban.md) — 1
- [cat:tooling](2026-05-11-repo-workspace-hub-domain-cat-tooling-kanban.md) — 1
- [cat:uncategorised](2026-05-11-repo-workspace-hub-domain-cat-uncategorised-kanban.md) — 1
- [cat:work-queue-infrastructure](2026-05-11-repo-workspace-hub-domain-cat-work-queue-infrastructure-kanban.md) — 1
- [domain:agent-adapters](2026-05-11-repo-workspace-hub-domain-domain-agent-adapters-kanban.md) — 1
- [domain:agent-cost-tracking](2026-05-11-repo-workspace-hub-domain-domain-agent-cost-tracking-kanban.md) — 1
- [domain:agent-patterns](2026-05-11-repo-workspace-hub-domain-domain-agent-patterns-kanban.md) — 1
- [domain:agent-ux](2026-05-11-repo-workspace-hub-domain-domain-agent-ux-kanban.md) — 1
- [domain:automation](2026-05-11-repo-workspace-hub-domain-domain-automation-kanban.md) — 1
- [domain:branding](2026-05-11-repo-workspace-hub-domain-domain-branding-kanban.md) — 1
- [domain:cathodic-protection](2026-05-11-repo-workspace-hub-domain-domain-cathodic-protection-kanban.md) — 1
- [domain:cre-finance](2026-05-11-repo-workspace-hub-domain-domain-cre-finance-kanban.md) — 1
- [domain:document-index](2026-05-11-repo-workspace-hub-domain-domain-document-index-kanban.md) — 1
- [domain:drilling](2026-05-11-repo-workspace-hub-domain-domain-drilling-kanban.md) — 1
- [domain:electrical-engineering](2026-05-11-repo-workspace-hub-domain-domain-electrical-engineering-kanban.md) — 1
- [domain:extraction-pipeline](2026-05-11-repo-workspace-hub-domain-domain-extraction-pipeline-kanban.md) — 1
- [domain:gis](2026-05-11-repo-workspace-hub-domain-domain-gis-kanban.md) — 1
- [domain:git-hygiene](2026-05-11-repo-workspace-hub-domain-domain-git-hygiene-kanban.md) — 1
- [domain:home](2026-05-11-repo-workspace-hub-domain-domain-home-kanban.md) — 1
- [domain:hooks](2026-05-11-repo-workspace-hub-domain-domain-hooks-kanban.md) — 1
- [domain:infrastructure](2026-05-11-repo-workspace-hub-domain-domain-infrastructure-kanban.md) — 1
- [domain:labor-market](2026-05-11-repo-workspace-hub-domain-domain-labor-market-kanban.md) — 1
- [domain:onboarding](2026-05-11-repo-workspace-hub-domain-domain-onboarding-kanban.md) — 1
- [domain:refactor](2026-05-11-repo-workspace-hub-domain-domain-refactor-kanban.md) — 1
- [domain:reporting](2026-05-11-repo-workspace-hub-domain-domain-reporting-kanban.md) — 1
- [domain:scripts](2026-05-11-repo-workspace-hub-domain-domain-scripts-kanban.md) — 1
- [domain:session-health](2026-05-11-repo-workspace-hub-domain-domain-session-health-kanban.md) — 1
- [domain:skill-curation](2026-05-11-repo-workspace-hub-domain-domain-skill-curation-kanban.md) — 1
- [domain:standards](2026-05-11-repo-workspace-hub-domain-domain-standards-kanban.md) — 1
- [domain:standards-tooling](2026-05-11-repo-workspace-hub-domain-domain-standards-tooling-kanban.md) — 1
- [domain:structural-dynamics](2026-05-11-repo-workspace-hub-domain-domain-structural-dynamics-kanban.md) — 1
- [domain:training](2026-05-11-repo-workspace-hub-domain-domain-training-kanban.md) — 1
- [domain:website](2026-05-11-repo-workspace-hub-domain-domain-website-kanban.md) — 1
- [domain:work-queue-workflow](2026-05-11-repo-workspace-hub-domain-domain-work-queue-workflow-kanban.md) — 1
### digitalmodel

- [cat:engineering](2026-05-11-repo-digitalmodel-domain-cat-engineering-kanban.md) — 179
- [domain:engineering-models](2026-05-11-repo-digitalmodel-domain-domain-engineering-models-kanban.md) — 77
- [cat:data](2026-05-11-repo-digitalmodel-domain-cat-data-kanban.md) — 5
- [domain:naval-architecture](2026-05-11-repo-digitalmodel-domain-domain-naval-architecture-kanban.md) — 4
- [cat:engineering-methodology](2026-05-11-repo-digitalmodel-domain-cat-engineering-methodology-kanban.md) — 3
- [cat:engineering-calculations](2026-05-11-repo-digitalmodel-domain-cat-engineering-calculations-kanban.md) — 2
- [cat:engineering-models](2026-05-11-repo-digitalmodel-domain-cat-engineering-models-kanban.md) — 1
### assetutilities

- [domain:shared-utilities](2026-05-11-repo-assetutilities-domain-domain-shared-utilities-kanban.md) — 19
### worldenergydata

- [cat:engineering](2026-05-11-repo-worldenergydata-domain-cat-engineering-kanban.md) — 22
- [domain:energy-data](2026-05-11-repo-worldenergydata-domain-domain-energy-data-kanban.md) — 18
- [cat:data](2026-05-11-repo-worldenergydata-domain-cat-data-kanban.md) — 15
- [cat:automation](2026-05-11-repo-worldenergydata-domain-cat-automation-kanban.md) — 1
### llm-wiki

- [domain:knowledge-management](2026-05-11-repo-llm-wiki-domain-domain-knowledge-management-kanban.md) — 19
- [cat:engineering](2026-05-11-repo-llm-wiki-domain-cat-engineering-kanban.md) — 10
- [cat:data](2026-05-11-repo-llm-wiki-domain-cat-data-kanban.md) — 2
- [cat:documentation](2026-05-11-repo-llm-wiki-domain-cat-documentation-kanban.md) — 2
- [domain:knowledge](2026-05-11-repo-llm-wiki-domain-domain-knowledge-kanban.md) — 2
- [domain:maritime-law](2026-05-11-repo-llm-wiki-domain-domain-maritime-law-kanban.md) — 1
### assethold

- [domain:finance-portfolio](2026-05-11-repo-assethold-domain-domain-finance-portfolio-kanban.md) — 16
- [cat:engineering](2026-05-11-repo-assethold-domain-cat-engineering-kanban.md) — 10
- [cat:maintenance](2026-05-11-repo-assethold-domain-cat-maintenance-kanban.md) — 1
### aceengineer-website

- [domain:website-gtm](2026-05-11-repo-aceengineer-website-domain-domain-website-gtm-kanban.md) — 5
### aceengineer-strategy

- [domain:business-strategy](2026-05-11-repo-aceengineer-strategy-domain-domain-business-strategy-kanban.md) — 20
