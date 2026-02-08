# Workspace Hub

> **Context Budget**: 4KB max | Submodules inherit and extend

## Golden Rule: Orchestrator Pattern

**Claude Code CLI is the orchestrator, NOT the executor.**

```
┌─────────────────────────────────────────────────────┐
│  Main Claude Code Instance = ORCHESTRATOR ONLY     │
│  • Plans and coordinates                           │
│  • Spawns subagents for ALL execution              │
│  • Stays lean (<20% context for planning)          │
│  • NEVER executes complex tasks directly           │
└─────────────────────────────────────────────────────┘
```

**Why?** Subagents isolate context pollution, prevent drift, and can be discarded without losing orchestrator state.

## Core Rules

1. **Orchestrate, don't execute** - Always delegate via Task tool
2. **TDD mandatory** - Tests before implementation
3. **Batch operations** - Single messages
4. **YAGNI** - Only what's needed
5. **No sycophancy** - Ask questions when unclear
6. **Use repo uv environment** - All tasks execute in project's uv environment

## Delegation Pattern

Keep main context free. Use Task tool for:
- **Explore**: codebase search, file discovery, understanding code
- **Plan**: architecture decisions, implementation strategy
- **Bash**: git operations, builds, tests
- **general-purpose**: multi-step implementations

Agents on-demand: `.claude/agent-library/<category>/<agent>.md`

### Agent Categories
- `core/` - coder, tester, reviewer, planner
- `devops/` - database, infrastructure, security-audit, observability
- `github/` - pr-manager, code-review-swarm, release-manager
- `sparc/` - specification, pseudocode, architecture

## Git Operations

- Submodules: handle individually, expect force-pushed refs and merge conflicts
- Never rebase diverged branches — use merge or `reset --hard origin/<branch>` after user confirmation
- Windows: report path limitations (trailing spaces, long paths, symlinks) immediately, don't retry
- Shell scripts: use `#!/usr/bin/env bash`, ensure LF line endings

## Work Items & Approval Gates

- Work items (WRK-*) stored at workspace-hub level: `.claude/work-queue/`
- Before executing plans, running simulations, or making git commits: present plan, wait for explicit approval
- Never autonomously execute multi-step workflows without user confirmation

## Commands

`./scripts/workspace` | `./scripts/repository_sync`

## Skills

`/skills` for list. Load on-demand only.

## Plan Mode Convention

Save plans to: `specs/modules/<module>/`
- Templates: `specs/templates/plan-template.md` or `plan-template-minimal.md`
- Required metadata: `title`, `description`, `version`, `module`, `session.id`, `session.agent`, `review`

**Cross-Review (MANDATORY)**: All available AI agents must review. Use `scripts/review/cross-review.sh <file> all`.
- **Claude** (current session): inline review by orchestrating agent
- **Codex CLI**: `codex review --commit <sha>` or `codex exec` for content review
- **Gemini CLI**: `gemini --prompt` for non-interactive review
- Minimum: 3 reviewers. If a CLI produces no output, note as NO_OUTPUT and proceed with remaining verdicts.

## SPARC Modes

`/sparc-*` commands: architect, coder, reviewer, tester, planner

## Command Conventions

- `/create-spec` - Assign agents by task, use parallel subagents
- `/execute-tasks` - Use repo uv environment, mark completed tasks `[x]`

## Context Limits

Global 2KB + Workspace 4KB + Project 8KB + Local 2KB = 16KB max. See `docs/CONTEXT_LIMITS.md`.

## Retrieval-Led Reasoning

**IMPORTANT**: Prefer retrieval over training knowledge.
Consult `.claude/docs/`, `.claude/rules/`, and project `CLAUDE.md` before relying on general knowledge.

## Resource Index

```
docs/|orchestrator-pattern:delegation|agent-composition:workflows|command-registry:commands|mcp-tools:tools|execution-patterns:MCP-vs-Task|CONTEXT_LIMITS:budgets|foundational-ai-skills:context-eng
rules/|security:secrets,injection,auth|testing:tdd,coverage|coding-style:naming,sizes|patterns:DI,SOLID|git-workflow:branches,commits
agents/core/|coder|tester|reviewer|planner|researcher|explorer
agents/github/|pr-manager|code-review-swarm|release-manager|repo-architect
agents/sparc/|specification|pseudocode|architecture|refinement
agents/devops/|database|infrastructure|security-audit|observability|ci-cd
agents/swarm/|hierarchical|mesh|adaptive|collective-intelligence|queen|worker
skills/eng/|orcaflex-specialist|hydrodynamic-analysis|mooring-analysis|fatigue-analysis|marine-offshore
skills/data/|polars|pandas|numpy|plotly|pdf|document-rag-pipeline
skills/dev/|github-pr-manager|github-code-review|sparc-*|testing-tdd-london
skills/ops/|docker|github-actions|uv-package-manager|optimization-*
```

---

*Verbose documentation belongs in `.claude/docs/`, not here.*
