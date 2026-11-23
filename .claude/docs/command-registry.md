# Command Registry

> Comprehensive mapping of slash commands to agents and skills for workspace-hub.

## Purpose

This registry provides a quick reference for discovering and loading skills by command. Use this to:
- Find the right agent for a task
- Understand command prerequisites
- Load skills on-demand with `/skill-name`

## Loading Commands

```bash
# Load any skill on-demand
/skill-name

# Example: Load TDD skill
/tdd

# Example: Load code review swarm
/code-review
```

---

## Core Development Agents

Essential agents for the development lifecycle.

| Command | Agent | Category | Prerequisites | Description |
|---------|-------|----------|---------------|-------------|
| `/coder` | core-coder | core | Test framework | Implementation specialist for clean, efficient code |
| `/tester` | core-tester | core | Jest/Vitest/pytest | QA specialist for comprehensive testing |
| `/reviewer` | core-reviewer | core | Git diff available | Code review and security audit |
| `/planner` | core-planner | core | None | Strategic task decomposition and planning |
| `/researcher` | core-researcher | core | None | Deep research and pattern analysis |

### Usage Pattern

```javascript
// Spawn via Task tool
Task("Coder agent", "Implement [feature] following TDD", "coder")
Task("Tester agent", "Create tests for [feature]", "tester")
Task("Reviewer agent", "Review PR #123", "reviewer")
```

---

## GitHub Integration

Commands for GitHub workflow automation.

| Command | Agent | Category | Prerequisites | Description |
|---------|-------|----------|---------------|-------------|
| `/pr-manager` | github-pr-manager | github | `gh auth status` | PR lifecycle management and multi-reviewer coordination |
| `/code-review` | github-code-review | github | Git diff | Multi-agent code review with security analysis |
| `/issue-tracker` | github-issue-tracker | github | `gh` CLI | Issue management and triage |
| `/release-manager` | github-release-manager | github | Git tags | Coordinate releases and changelogs |
| `/release-swarm` | github-release-swarm | github | Git tags | Automated release with swarm agents |
| `/github-sync` | github-sync | github | SSH keys | Sync coordinator for multi-repo |
| `/repo-architect` | github-repo-architect | github | None | Repository structure design |
| `/github-workflow` | github-workflow | github | `.github/workflows/` | GitHub Actions automation |
| `/multi-repo` | github-multi-repo | github | SSH keys | Cross-repository operations |
| `/swarm-pr` | github-swarm-pr | github | `gh` CLI | Swarm-based PR management |
| `/swarm-issue` | github-swarm-issue | github | `gh` CLI | Issue-based swarm coordination |

### GitHub CLI Examples

```bash
# PR management
gh pr create --title "Feature" --body "Description"
gh pr review 123 --approve --body "LGTM!"
gh pr merge 123 --squash --delete-branch

# Code review
gh pr diff 123
gh pr view 123 --json files,additions,deletions
```

---

## Testing Skills

Commands for test-driven development and validation.

| Command | Agent | Category | Prerequisites | Description |
|---------|-------|----------|---------------|-------------|
| `/tdd` | testing-tdd-london | testing | Jest/Vitest | London School (mockist) TDD |
| `/tdd-production` | testing-production | testing | Test framework | Production validation testing |
| `/webapp-testing` | webapp-testing | testing | Playwright/Cypress | Web application E2E testing |

### TDD Workflow

```typescript
// London School - Outside-In
describe('Feature', () => {
  it('should verify interactions', () => {
    const mockRepo = { save: jest.fn() };
    const service = new Service(mockRepo);
    service.execute();
    expect(mockRepo.save).toHaveBeenCalled();
  });
});
```

---

## SPARC Methodology

Commands for the Specification-Pseudocode-Architecture-Refinement-Completion workflow.

| Command | Agent | Category | Prerequisites | Description |
|---------|-------|----------|---------------|-------------|
| `/sparc-spec` | sparc-specification | sparc | Requirements | Define specifications and requirements |
| `/sparc-pseudo` | sparc-pseudocode | sparc | Specifications | Algorithm design with pseudocode |
| `/sparc-arch` | sparc-architecture | sparc | Pseudocode | System architecture design |
| `/sparc-refine` | sparc-refinement | sparc | Architecture | TDD implementation and refinement |
| `/sparc-workflow` | sparc-workflow | workspace-hub | None | Complete SPARC orchestration |

### SPARC Flow

```
Specification -> Pseudocode -> Architecture -> Refinement -> Completion
     |              |              |              |             |
   What?         How?          Where?        Build it!      Ship it!
```

---

## Workspace Management

Commands for workspace-hub operations.

| Command | Agent | Category | Prerequisites | Description |
|---------|-------|----------|---------------|-------------|
| `/repo-sync` | repo-sync | workspace-hub | SSH keys | Bulk Git operations across repos |
| `/workspace-cli` | workspace-cli | workspace-hub | None | Interactive workspace menu |
| `/compliance-check` | compliance-check | workspace-hub | None | Standards verification |
| `/agent-orchestration` | agent-orchestration | workspace-hub | None | Agent coordination framework |
| `/repo-capability-map` | repo-capability-map | workspace-hub | None | Capability discovery, domain classification, gap analysis |
| `/reflect` | claude-reflect | workspace-hub | Git history | Periodic reflection on git history across repos |
| `/work` | work-queue | workspace-hub | None | Work item capture and processing pipeline |
| `/knowledge` | knowledge-manager | workspace-hub | `jq` | Capture, organize, and surface institutional knowledge |
| `/knowledge capture` | knowledge-manager | workspace-hub | `jq` | Extract and store knowledge entries |
| `/knowledge advise` | knowledge-manager | workspace-hub | `jq` | Surface relevant knowledge for a task |
| `/knowledge search` | knowledge-manager | workspace-hub | `jq` | Search by keyword/tag/type/category |
| `/knowledge review` | knowledge-manager | workspace-hub | `jq` | Review stale entries, decay confidence |
| `/knowledge stats` | knowledge-manager | workspace-hub | `jq` | Knowledge base health dashboard |

### Repository Sync

```bash
# Status check
./scripts/repository_sync status all

# Pull all repos
./scripts/repository_sync pull all

# Sync (commit + push) all
./scripts/repository_sync sync all -m "End of day sync"
```

---

## Document Handling

Commands for document processing and knowledge management.

| Command | Agent | Category | Prerequisites | Description |
|---------|-------|----------|---------------|-------------|
| `/pdf` | pdf | document-handling | pypdf | PDF reading and extraction |
| `/docx` | docx | document-handling | python-docx | Word document processing |
| `/xlsx` | xlsx | document-handling | openpyxl | Excel spreadsheet processing |
| `/pptx` | pptx | document-handling | python-pptx | PowerPoint creation |
| `/rag-builder` | rag-system-builder | document-handling | Vector DB | RAG system construction |
| `/knowledge-base` | knowledge-base-builder | document-handling | None | Knowledge base creation |
| `/semantic-search` | semantic-search-setup | document-handling | Embeddings | Semantic search configuration |

---

## Builders & Tools

Commands for creating and extending capabilities.

| Command | Agent | Category | Prerequisites | Description |
|---------|-------|----------|---------------|-------------|
| `/skill-creator` | skill-creator | builders | None | Create new Claude Code skills |
| `/mcp-builder` | mcp-builder | development | Node.js | Build MCP servers |
| `/web-artifacts` | web-artifacts-builder | builders | None | Create web artifacts |

### Skill Creation

```bash
# Create skill directory
mkdir -p .claude/skills/my-skill

# Create SKILL.md
cat > .claude/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Action-oriented description. Use for X, Y, Z.
version: 1.0.0
category: builders
---
# My Skill
## Overview
[Purpose explanation]
EOF
```

---

## DevOps & Infrastructure

Commands for development operations and infrastructure.

| Command | Agent | Category | Prerequisites | Description |
|---------|-------|----------|---------------|-------------|
| `/docker` | docker | devtools | Docker installed | Container management |
| `/git-advanced` | git-advanced | devtools | Git | Advanced Git operations |
| `/uv` | uv-package-manager | devtools | uv installed | Python package management |
| `/github-actions` | github-actions | automation | `.github/` dir | CI/CD workflow automation |

---

## Consensus Protocols

Commands for distributed consensus in swarm operations.

| Command | Agent | Category | Prerequisites | Description |
|---------|-------|----------|---------------|-------------|
| `/consensus-raft` | consensus-raft | consensus | Swarm active | Raft consensus protocol |
| `/consensus-gossip` | consensus-gossip | consensus | Swarm active | Gossip protocol coordination |
| `/consensus-crdt` | consensus-crdt | consensus | Swarm active | CRDT-based state sync |
| `/consensus-byzantine` | consensus-byzantine | consensus | Swarm active | Byzantine fault tolerance |
| `/consensus-quorum` | consensus-quorum | consensus | Swarm active | Quorum-based decisions |

---

## Command Aliases

Common alternative names for commands.

| Alias | Maps To | Notes |
|-------|---------|-------|
| `/test` | `/tester` | Core testing agent |
| `/review` | `/reviewer` | Code review agent |
| `/plan` | `/planner` | Planning agent |
| `/research` | `/researcher` | Research agent |
| `/code` | `/coder` | Implementation agent |
| `/pr` | `/pr-manager` | PR management |
| `/sync` | `/repo-sync` | Repository sync |
| `/capmap` | `/repo-capability-map` | Capability map |
| `/capability-map` | `/repo-capability-map` | Capability map |
| `/k` | `/knowledge` | Knowledge base status |
| `/kc` | `/knowledge capture` | Knowledge capture |
| `/ka` | `/knowledge advise` | Knowledge advise |
| `/ks` | `/knowledge search` | Knowledge search |
| `/kr` | `/knowledge review` | Knowledge review |

---

## Quick Reference by Task

### "I need to..."

| Task | Command | Agent |
|------|---------|-------|
| Write new code | `/coder` | core-coder |
| Write tests | `/tester` | core-tester |
| Review a PR | `/code-review` | github-code-review |
| Plan a feature | `/planner` | core-planner |
| Research patterns | `/researcher` | core-researcher |
| Create a PR | `/pr-manager` | github-pr-manager |
| Sync all repos | `/repo-sync` | repo-sync |
| Monitor performance | `/perf-monitor` | optimization-monitor |
| Design architecture | `/sparc-arch` | sparc-architecture |
| Coordinate swarm | `/swarm-queen` | swarm-queen |
| Process PDFs | `/pdf` | pdf |
| Create a skill | `/skill-creator` | skill-creator |
| TDD development | `/tdd` | testing-tdd-london |
| Map repo capabilities | `/repo-capability-map` | repo-capability-map |
| Find capability gaps | `/repo-capability-map gaps` | repo-capability-map |
| Capture knowledge | `/knowledge capture` | knowledge-manager |
| Get task advice | `/knowledge advise` | knowledge-manager |
| Search knowledge | `/knowledge search` | knowledge-manager |

---

## Skill Categories Overview

| Category | Focus | Example Skills |
|----------|-------|----------------|
| `core` | Development lifecycle | coder, tester, reviewer, planner |
| `github` | GitHub integration | pr-manager, code-review, release-manager |
| `testing` | Test strategies | tdd-london, production, webapp |
| `sparc` | SPARC methodology | specification, architecture, refinement |
| `swarm` | Multi-agent coordination | queen, collective, worker, scout |
| `optimization` | Performance | monitor, benchmark, load-balancer |
| `workspace-hub` | Repo management | repo-sync, compliance, orchestration, capability-map, reflect, work |
| `document-handling` | Documents | pdf, docx, xlsx, rag-builder |
| `builders` | Tool creation | skill-creator, mcp-builder |
| `devtools` | Dev operations | docker, git-advanced, uv |
| `consensus` | Distributed consensus | raft, gossip, crdt, byzantine |

---

## Related Documentation

- [Orchestrator Pattern](./orchestrator-pattern.md) - Delegation patterns

- [Context Limits](./CONTEXT_LIMITS.md) - Memory management
- [Execution Patterns](./execution-patterns.md) - Best practices

---

*Last updated: 2026-01-30*
