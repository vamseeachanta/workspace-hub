# Claude Code Configuration - Workspace Hub

> Central documentation hub for all 26+ repositories. Detailed guides referenced via `@docs/...` paths.

## Critical Rules

**Rule #1**: Get explicit permission before breaking ANY rule.

### Core Principles
- TDD mandatory: Write failing tests first, then implement
- YAGNI: Don't add features not needed now
- Simple solutions over clever ones
- Match surrounding code style
- Fix bugs immediately when found

### Code Quality
- Names describe purpose, not implementation
- Comments explain WHAT/WHY, not history
- All files start with 2-line `ABOUTME:` comment
- Never remove comments unless provably false

### Git Discipline
- Commit frequently with descriptive messages
- Never skip/evade pre-commit hooks
- Ask about uncommitted changes before starting

### Collaboration
- Push back on bad ideas with technical reasons
- Say "I don't know" rather than guess
- Stop and ask rather than assume

## File Organization

**NEVER save to root. Use:** `/src`, `/tests`, `/docs`, `/config`, `/scripts`, `/data`, `/reports`

## Execution Patterns

**Batch all operations in single messages:**
- TodoWrite: ALL todos in ONE call
- Task tool: ALL agents in ONE message
- File/Bash operations: ALL together

## Agent Coordination

Use Claude Code's Task tool for agents: `Task("name", "description", "type")`
MCP tools (`mcp__claude-flow__*`) for coordination setup only.

## Quick Commands

```bash
./scripts/workspace              # Main CLI
./scripts/repository_sync pull all  # Sync repos
```

## Documentation References

### Workflow (MANDATORY)
- @docs/ai/AI_AGENT_GUIDELINES.md - **READ FIRST**
- @docs/workflow/DEVELOPMENT_WORKFLOW.md
- @docs/ai/AI_USAGE_GUIDELINES.md

### Standards
- @docs/standards/FILE_ORGANIZATION_STANDARDS.md
- @docs/standards/HTML_REPORTING_STANDARDS.md
- @docs/standards/TESTING_FRAMEWORK_STANDARDS.md
- @docs/standards/LOGGING_STANDARDS.md

### CLI & Tools
- @docs/cli/WORKSPACE_CLI.md
- @docs/cli/REPOSITORY_SYNC.md

### Agent OS
- @.agent-os/product/mission.md
- @.agent-os/product/tech-stack.md
- @.agent-os/product/roadmap.md
- @~/.agent-os/instructions/create-spec.md
- @~/.agent-os/instructions/execute-tasks.md

## Rule Precedence

1. Security/Safety - highest
2. TDD - mandatory
3. Code Quality - Part 1 standards
4. Orchestration - Part 2 patterns
5. Project-specific - overrides when defined

---
*See @docs/README.md for complete documentation index*
