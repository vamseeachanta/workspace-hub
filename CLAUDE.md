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
7. **Session-exit improvement** - Run `/improve` before ending every session

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
- Force-pushed refs: detect via `git rev-list --count HEAD..origin/main`; always fetch first
- Stash before pull when uncommitted changes exist; report stash pop conflicts, don't auto-resolve
- Windows: report path limitations (trailing spaces, long paths, symlinks) immediately, don't retry
- Shell scripts: use `#!/usr/bin/env bash`, ensure LF line endings (CRLF breaks MINGW)

## Work Items & Approval Gates

- Work items (WRK-*) stored at workspace-hub level: `.claude/work-queue/` — NEVER in local project dirs
- Before executing plans, running simulations, or making git commits: present plan, wait for explicit approval
- Never autonomously execute multi-step workflows without user confirmation
- Multi-phase work (plan/implement/test/commit): pause between phases for user confirmation

## Windows Compatibility

- Symlinks require admin — fall back to README cross-references or `core.symlinks false`
- MINGW root path: `while [ "$(pwd)" != / ]` loops never terminate — use `WORKSPACE_HUB` env var
- Test all bash scripts for Git Bash (MINGW64) + Linux compatibility

## Commands

`./scripts/workspace` | `./scripts/repository_sync`

## Skills

`/skills` for list. Load on-demand only.

## Plan Mode Convention

Save plans to: `specs/modules/<module>/`
- Templates: `specs/templates/plan-template.md` or `plan-template-minimal.md`
- Required metadata: `title`, `description`, `version`, `module`, `session.id`, `session.agent`, `review`

**Cross-Review (MANDATORY)**: All available AI agents must review. Use `scripts/review/cross-review.sh <file> all`.
- **Codex CLI** (REQUIRED): `codex review --commit <sha>` or `codex exec` — **must produce a verdict**. If Codex fails or is unavailable, the review is BLOCKED until resolved. Do not proceed without Codex approval.
- **Claude** (current session): inline review by orchestrating agent
- **Gemini CLI**: `gemini --prompt` for non-interactive review
- Minimum: 3 reviewers. Codex is a hard gate; Claude and Gemini failures may be noted as NO_OUTPUT and proceeded with.

## SPARC Modes

`/sparc-*` commands: architect, coder, reviewer, tester, planner

## Command Conventions

- `/create-spec` - Assign agents by task, use parallel subagents
- `/execute-tasks` - Use repo uv environment, mark completed tasks `[x]`

## Context Limits

Global 2KB + Workspace 4KB + Project 8KB + Local 2KB = 16KB max. See `docs/CONTEXT_LIMITS.md`.

## Retrieval-Led Reasoning

**IMPORTANT**: Prefer retrieval over training knowledge.
Consult `.claude/docs/`, `.claude/rules/`, `.claude/memory/`, and project `CLAUDE.md` before relying on general knowledge.

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
