# Workspace Hub Skills Index

> Complete catalog of Claude Code skills in the workspace-hub skill tree
>
> **Total Skills:** 2,734 (568 active, 2,166 archived)
> **Last Updated:** 2026-04-02
> **Location:** `.claude/skills/`

---

## Overview

All skills are centralized in `/mnt/local-analysis/workspace-hub/.claude/skills/`.
Skills are organized into category directories, each containing subcategories
with one or more `SKILL.md` files. Subcategories can be deeply nested — for
example, `_core/bash/` alone contains 40+ skill files across frameworks like
`bash-cli-framework`, `complexity-scorer`, `git-sync-manager`, and more.

Skills are loaded automatically by Claude Code when task patterns match skill
triggers defined in each `SKILL.md`.

---

## Category Summary

| Category | Active Skills | Subcategories | Description |
|----------|:---:|:---:|-------------|
| `_core` | 53 | 3 | Foundational skills — bash scripting frameworks, agent coordination, context-window management |
| `_internal` | 128 | 4 | Skill system internals — builders, documentation generators, metadata/governance, workflow orchestration |
| `ai` | 9 | 3 | AI agent usage optimization, model/prompt optimization, prompt engineering patterns |
| `business` | 70 | 12 | Admin, client demos, communications, content design, customer support, enterprise search, finance, legal, marketing, product, productivity, sales |
| `data` | 77 | 15 | Data analysis, analytics, calculation reports, document intelligence, document processing (docx/pdf/pptx/xlsx), energy data, research & literature, scientific data, visualization (Plotly) |
| `development` | 52 | 27 | Code review, dev tools, GitHub workflows, git worktrees, MCP server building, parallel processing, planning, TDD, testing, TypeScript, web apps, YAML workflows |
| `digitalmodel` | 2 | 2 | DigitalModel module lookup, naval architecture domain expertise |
| `engineering` | 87 | 13 | Asset integrity, CAD (FreeCAD), CFD (OpenFOAM), doc extraction, drilling, financial analysis, GIS, marine/offshore, maritime legal, oil & gas, standards (DNV/API/ISO), units, engineering workflows |
| `gsd-*` | 57 | — | GSD (Get Shit Done) workflow commands — each a standalone skill directory |
| `operations` | 15 | 3 | DevOps, infrastructure automation, operational tooling |
| `science` | 6 | 1 | Biological research data processing |
| `workspace-hub` | 12 | 12 | Agent teams, reflection, clean code, learning, ecosystem terminology, Playwright, remote desktop, portfolio steering, repo structure, repo sync |
| `_archive` | 2,166 | — | Retired and superseded skills |

> **Note:** "Active Skills" counts every `SKILL.md` file in the category tree
> (excluding `_archive/`). Subcategories often contain multiple nested skills,
> which is why the skill count exceeds the subcategory count.

---

## Category Details

### `_core/` — 53 skills

Foundational capabilities that other skills build on.

| Subcategory | Description |
|-------------|-------------|
| `agents` | Agent coordination and delegation patterns |
| `bash` | Bash scripting frameworks (CLI framework, script framework, complexity scorer, cross-platform compat, git-sync-manager, interactive menu builder, and more) |
| `context-management` | Context window optimization, token budgeting, and session management |

### `_internal/` — 128 skills

The skill system's own machinery — how skills are created, documented, governed, and orchestrated.

| Subcategory | Description |
|-------------|-------------|
| `builders` | Skill and artifact creation frameworks |
| `documentation` | Documentation generation patterns and templates |
| `meta` | Skill system metadata, governance, and lifecycle rules |
| `workflows` | Internal workflow orchestration and chaining |

### `ai/` — 9 skills

| Subcategory | Description |
|-------------|-------------|
| `agent-usage-optimizer` | Optimize AI agent subscription usage across providers |
| `optimization` | AI model tuning and prompt optimization techniques |
| `prompting` | Prompt engineering patterns and templates |

### `business/` — 70 skills

| Subcategory | Description |
|-------------|-------------|
| `admin` | Business administration workflows |
| `client-demo` | Client demonstration preparation |
| `communication` | Professional communications (memos, newsletters) |
| `content-design` | Content creation and design systems |
| `customer-support` | Customer support workflows |
| `enterprise-search` | Enterprise knowledge search |
| `finance` | Financial analysis and reporting |
| `legal` | Legal document handling |
| `marketing` | Marketing content and strategy |
| `product` | Product management workflows |
| `productivity` | Productivity tools and automation |
| `sales` | Sales process and pipeline management |

### `data/` — 77 skills

| Subcategory | Description |
|-------------|-------------|
| `analysis` | General data analysis patterns |
| `analytics` | Analytics dashboards and reporting |
| `calculation-report` | Calculation report generation |
| `dark-intelligence-workflow` | Intelligence gathering workflows |
| `doc-intelligence-promotion` | Document intelligence promotion |
| `doc-research-download` | Document research and download |
| `document-index-pipeline` | Document indexing pipeline |
| `documents` | Document processing (docx, pdf, pptx, xlsx) |
| `energy` | Energy sector data processing |
| `engineering` | Engineering data analysis |
| `office` | Office document manipulation |
| `research-and-literature-gathering` | Research literature collection |
| `research-literature` | Academic research processing |
| `scientific` | Scientific data processing |
| `visualization` | Data visualization (Plotly, charts) |

### `development/` — 52 skills

| Subcategory | Description |
|-------------|-------------|
| `automation` | Build and deployment automation |
| `code-reviewer` | Code review checklists and patterns |
| `data-pipeline-processor` | Data transformation pipeline execution |
| `devtools` | Developer tooling and utilities |
| `documentation` | Developer documentation generation |
| `elite-frontend-ux` | High-quality frontend/UX patterns |
| `engineering-report-generator` | Engineering report with Plotly visualizations |
| `git-worktree-workflow` | Git worktree parallel development |
| `github` | GitHub CLI and API patterns |
| `gitignore-scaffold` | .gitignore scaffolding for projects |
| `html-report-verify` | HTML report verification |
| `mcp-builder` | MCP server development guide |
| `parallel-file-processor` | Parallel file processing (2-3x perf) |
| `planning` | Implementation planning patterns |
| `plugin-management` | Plugin lifecycle management |
| `shell-tdd` | Shell-based test-driven development |
| `skill-eval` | Skill evaluation and scoring |
| `sparc` | _(legacy — retained for reference only)_ |
| `subagent-driven` | Subagent-driven task decomposition |
| `systematic-debugging` | Systematic debugging methodology |
| `tdd-obra` | Test-driven development (OBRA pattern) |
| `testing` | Testing patterns (pytest, unit, integration) |
| `tools` | Development tool integrations |
| `verification-loop` | Automated verification loops |
| `webapp-testing` | Web app testing with Playwright |
| `workflows` | Development workflow orchestration |
| `yaml-workflow-executor` | YAML-driven workflow execution |

### `digitalmodel/` — 2 skills

| Subcategory | Description |
|-------------|-------------|
| `module-lookup` | DigitalModel module discovery and lookup |
| `naval-architect-expert` | Naval architecture domain expertise |

### `engineering/` — 87 skills

| Subcategory | Description |
|-------------|-------------|
| `asset-integrity` | Asset integrity management |
| `cad` | CAD automation (FreeCAD, parametric design) |
| `cfd` | Computational fluid dynamics (OpenFOAM) |
| `doc-extraction` | Engineering document data extraction |
| `drilling` | Drilling engineering operations |
| `financial-analysis` | Engineering project economics |
| `gis` | Geographic information systems |
| `marine-offshore` | Marine/offshore engineering (mooring, risers, VIV) |
| `maritime-legal` | Maritime regulations and legal |
| `oil-and-gas` | Oil & gas production operations |
| `standards` | Engineering standards (DNV, API, ISO) |
| `units` | Unit conversion and validation |
| `workflows` | Engineering workflow orchestration |

### `operations/` — 15 skills

| Subcategory | Description |
|-------------|-------------|
| `automation` | Operational automation patterns |
| `devops` | DevOps and infrastructure |
| `devtools` | Operational developer tools |

### `science/` — 6 skills

| Subcategory | Description |
|-------------|-------------|
| `bio-research` | Biological research data processing |

### `workspace-hub/` — 12 skills

| Subcategory | Description |
|-------------|-------------|
| `agent-teams` | AI agent team coordination |
| `claude-reflect` | Claude self-reflection patterns |
| `clean-code` | Code cleanliness standards |
| `comprehensive-learning` | Learning and knowledge capture |
| `ecosystem-terminology` | Workspace-hub terminology guide |
| `improve` | Self-improvement workflows |
| `playwright` | Browser automation with Playwright |
| `remote-desktop` | Remote desktop management |
| `repo-portfolio-steering` | Repository portfolio management |
| `repo-structure` | Repository structure conventions |
| `repo-sync` | Multi-repo synchronization |
| `sync` | Configuration sync utilities |

---

## GSD Workflow Commands — 57 skills

The GSD (Get Shit Done) framework provides workflow commands as individual
skill directories. Each `gsd-*` directory contains a single `SKILL.md`.
Invoke them with `/gsd:<command>` syntax.

### Task Execution

| Command | Description |
|---------|-------------|
| `gsd-do` | Route freeform text to the right GSD command |
| `gsd-fast` | Quick task execution mode |
| `gsd-quick` | Rapid task dispatch |
| `gsd-next` | Pick and execute next task |
| `gsd-autonomous` | Autonomous task execution |

### Project Management

| Command | Description |
|---------|-------------|
| `gsd-new-project` | Initialize a new GSD project |
| `gsd-new-milestone` | Create a new milestone |
| `gsd-new-workspace` | Create a new workspace |
| `gsd-complete-milestone` | Mark milestone complete |
| `gsd-milestone-summary` | Summarize milestone status |
| `gsd-remove-workspace` | Remove a workspace |

### Phase Management

| Command | Description |
|---------|-------------|
| `gsd-add-phase` | Add a phase to a milestone |
| `gsd-plan-phase` | Plan phase details |
| `gsd-execute-phase` | Execute a phase |
| `gsd-discuss-phase` | Discuss phase approach |
| `gsd-validate-phase` | Validate phase completion |
| `gsd-remove-phase` | Remove a phase |
| `gsd-insert-phase` | Insert a phase at position |
| `gsd-research-phase` | Research phase requirements |
| `gsd-ui-phase` | Phase UI rendering |

### Task Tracking

| Command | Description |
|---------|-------------|
| `gsd-add-todo` | Add a todo item |
| `gsd-add-backlog` | Add to backlog |
| `gsd-check-todos` | Check pending todos |
| `gsd-review-backlog` | Review backlog items |
| `gsd-progress` | Show progress report |
| `gsd-stats` | Project statistics |

### Quality & Review

| Command | Description |
|---------|-------------|
| `gsd-review` | Review work quality |
| `gsd-verify-work` | Verify completed work |
| `gsd-audit-milestone` | Audit milestone quality |
| `gsd-audit-uat` | User acceptance testing |
| `gsd-add-tests` | Add tests to codebase |
| `gsd-ui-review` | UI review process |

### Operations

| Command | Description |
|---------|-------------|
| `gsd-help` | GSD help and command reference |
| `gsd-health` | System health check |
| `gsd-debug` | Debug GSD issues |
| `gsd-forensics` | Deep investigation of issues |
| `gsd-cleanup` | Clean up artifacts |
| `gsd-update` | Update GSD framework |
| `gsd-ship` | Ship/deploy changes |
| `gsd-map-codebase` | Map codebase structure |

### Workflow Control

| Command | Description |
|---------|-------------|
| `gsd-pause-work` | Pause current work |
| `gsd-resume-work` | Resume paused work |
| `gsd-thread` | Thread management |
| `gsd-workstreams` | Manage parallel workstreams |
| `gsd-pr-branch` | PR and branch workflow |
| `gsd-reapply-patches` | Reapply patches after conflict |
| `gsd-manager` | GSD manager mode |

### Other

| Command | Description |
|---------|-------------|
| `gsd-note` | Add a note |
| `gsd-plant-seed` | Plant a seed idea for later |
| `gsd-session-report` | Generate session report |
| `gsd-settings` | GSD settings management |
| `gsd-set-profile` | Set user profile |
| `gsd-profile-user` | View user profile |
| `gsd-join-discord` | Join Discord community |
| `gsd-list-workspaces` | List available workspaces |
| `gsd-list-phase-assumptions` | List phase assumptions |
| `gsd-plan-milestone-gaps` | Identify gaps in milestones |

---

## Skill File Structure

Each skill is a directory containing at minimum a `SKILL.md` file:

```
.claude/skills/<category>/<subcategory>/SKILL.md
.claude/skills/<category>/<subcategory>/<sub-skill>/SKILL.md
```

A `SKILL.md` typically includes:

- **Triggers** — patterns that cause the skill to be loaded automatically
- **Description** — what the skill does
- **Instructions** — step-by-step guidance for Claude Code
- **Examples** — usage examples
- **Best Practices** — domain-specific conventions

Deeply nested skills (e.g., `_core/bash/bash-cli-framework/1-always-use-set-e/SKILL.md`)
provide granular, composable instructions that roll up into their parent skill.

---

## Usage

```bash
# Count active skills
find .claude/skills -name SKILL.md -not -path '*/_archive/*' | wc -l

# View a specific skill
cat .claude/skills/engineering/marine-offshore/SKILL.md

# List all categories
ls -d .claude/skills/*/

# Run a GSD command
/gsd:help
/gsd:next
/gsd:do fix the broken tests
```

Skills are loaded automatically when Claude Code detects a task that matches
a skill's trigger patterns. You do not need to manually load skills — the
system selects the relevant ones based on your request context.

---

## Empty / Reserved Directories

The following directories exist in `.claude/skills/` but currently contain
no active skills:

- `session-logs/` — reserved for session log skills
- `_runtime/` — reserved for runtime-generated skills
- `eng/` — reserved (engineering overflow or short alias)

---

## Archive

The `_archive/` directory contains **2,166** retired or superseded skills.
Skills are archived (not deleted) when they are replaced by improved versions
or when their domain is reorganized. Archived skills are excluded from
automatic loading.

---

## Related Documentation

- [Workspace Hub Capabilities Summary](WORKSPACE_HUB_CAPABILITIES_SUMMARY.md)
- [Control Plane Contract](standards/CONTROL_PLANE_CONTRACT.md)
- [AI Agent Guidelines](modules/ai/AI_AGENT_GUIDELINES.md)

---

*Generated from `.claude/skills/` tree on 2026-04-02.*
