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

## Model Selection Rules (MANDATORY)

**Before every task, select the appropriate Claude model to optimize usage:**

### Quick Selection Guide

- **🔴 OPUS** (30% target): Complex decisions, architecture, multi-file refactoring (>5 files)
- **🔵 SONNET** (40% target): Standard implementations, code review, documentation
- **🟡 HAIKU** (30% target): Quick queries, status checks, simple operations

### Automated Model Suggestion (Recommended)

**Use the intelligent model suggestion tool before each task:**

```bash
# Get model recommendation
./scripts/monitoring/suggest_model.sh <repository> "<task description>"

# Examples:
./scripts/monitoring/suggest_model.sh digitalmodel "Design authentication system architecture"
# → Recommends: OPUS (complexity score: 4)

./scripts/monitoring/suggest_model.sh aceengineercode "Implement user login with JWT"
# → Recommends: SONNET (complexity score: 1)

./scripts/monitoring/suggest_model.sh hobbies "Quick check if file exists"
# → Recommends: HAIKU (complexity score: -3)
```

**How it works:**
- Analyzes task keywords (architecture, implement, check, etc.)
- Considers repository tier (Work Tier 1-3 vs Personal)
- Calculates complexity score
- Provides recommendation with reasoning and alternatives
- Optionally logs selection for tracking

**Integration:** Run before starting work to get intelligent model recommendation with confidence score and rationale.

**Full automation guide:** @docs/AI_MODEL_SELECTION_AUTOMATION.md

### Usage Monitoring

**CRITICAL:** Check usage before starting work → https://claude.ai/settings/usage

**Alert Thresholds:**
- Sonnet >70% → Switch to Opus/Haiku
- Session >80% → Batch work or wait for reset
- Overall >80% → Defer non-critical work

### Repository-Specific Rules

**Work Repositories** (Higher quality priority):
- Tier 1 (digitalmodel, energy): 60% Opus, 30% Sonnet, 10% Haiku
- Tier 2 (aceengineercode, worldenergydata): 30% Opus, 50% Sonnet, 20% Haiku
- Tier 3 (maintenance): 10% Opus, 30% Sonnet, 60% Haiku

**Personal Repositories** (Efficiency priority):
- Active: 20% Opus, 40% Sonnet, 40% Haiku
- Experimental: 5% Opus, 25% Sonnet, 70% Haiku
- Archive: 0% Opus, 20% Sonnet, 80% Haiku

**Full guide:** @docs/AI_AGENT_USAGE_OPTIMIZATION_PLAN.md
**Quick reference:** @docs/CLAUDE_MODEL_SELECTION_QUICK_REFERENCE.md

## Quick Commands

```bash
./scripts/workspace              # Main CLI
./scripts/repository_sync pull all  # Sync repos

# AI Usage Optimization
./scripts/monitoring/suggest_model.sh <repo> "<task>"  # Get model recommendation
./scripts/monitoring/check_claude_usage.sh             # Monitor AI usage
```

## Documentation References

### Workflow (MANDATORY)
- @docs/modules/ai/AI_AGENT_GUIDELINES.md - **READ FIRST**
- @docs/modules/ai/GEMINI_REVIEW_WORKFLOW.md - **Gemini Review Workflow**
- @docs/modules/workflow/DEVELOPMENT_WORKFLOW.md
- @docs/modules/ai/AI_USAGE_GUIDELINES.md
- @docs/AI_AGENT_USAGE_OPTIMIZATION_PLAN.md - **Model selection strategy**

### Standards
- @docs/modules/standards/FILE_ORGANIZATION_STANDARDS.md
- @docs/modules/standards/HTML_REPORTING_STANDARDS.md
- @docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md
- @docs/modules/standards/LOGGING_STANDARDS.md

### CLI & Tools
- @docs/modules/cli/WORKSPACE_CLI.md
- @docs/modules/cli/REPOSITORY_SYNC.md

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
