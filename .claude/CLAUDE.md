# Claude Code - Workspace Hub (Extended)

> This file extends root CLAUDE.md with additional context. Root rules take precedence.

## SPARC Methodology

Phases: Specification → Pseudocode → Architecture → Refinement (TDD) → Completion

```bash
npx claude-flow sparc run <mode> "<task>"
npx claude-flow sparc tdd "<feature>"
```

## Available Agents

**Core:** coder, reviewer, tester, planner, researcher
**SPARC:** specification, pseudocode, architecture, refinement
**GitHub:** pr-manager, code-review-swarm, issue-tracker
**Specialized:** backend-dev, ml-developer, cicd-engineer, system-architect

## MCP Setup

```bash
claude mcp add claude-flow npx claude-flow@alpha mcp start
```

## HTML Reporting

- Interactive plots only (Plotly, Bokeh, Altair, D3.js)
- NO static matplotlib exports
- CSV data with relative paths in `/data/`

## Agent Hooks

```bash
# Before: npx claude-flow@alpha hooks pre-task --description "[task]"
# After:  npx claude-flow@alpha hooks post-task --task-id "[task]"
```

## Multi-Provider Orchestration

Intelligent routing to Gemini, Claude, and Codex.

```bash
# Single Task
./scripts/routing/orchestrate.sh "<task>"

# Batch Execution (Parallel)
./scripts/batchtools/batch_runner.sh --parallel 5 < tasks.json
```

## Key References

- Full agent list: @docs/modules/ai/AI_AGENT_GUIDELINES.md
- HTML standards: @docs/modules/standards/HTML_REPORTING_STANDARDS.md
- File organization: @docs/modules/standards/FILE_ORGANIZATION_STANDARDS.md
- Development workflow: @docs/modules/workflow/DEVELOPMENT_WORKFLOW.md

## Context Management (MANDATORY)

**Prevent context overflow through efficient response patterns.**

### %ctx Tracking

```bash
# Check context status
python .claude/tools/context_manager.py status <current_tokens>

# Create checkpoint
python .claude/tools/context_manager.py checkpoint <task-name>
```

**Health Indicators:**
| %ctx | Status | Action |
|------|--------|--------|
| 0-40% | 🟢 Healthy | Normal operation |
| 40-60% | 🟡 Elevated | Consider summarizing |
| 60-80% | 🟠 High | Archive older exchanges |
| 80-100% | 🔴 Critical | Trim to essentials |

### Response Format Rules

- **Tables:** Max 10 rows, summarize remainder with counts
- **Code blocks:** Max 50 lines, split larger into files
- **Lists:** Max 15 items, aggregate beyond that
- **Large outputs:** Write to `.claude/outputs/`, return path only

### Mandatory Response Ending

Every response MUST end with status line:
```
STATUS: [complete|in_progress|blocked] | NEXT: [single action] | KEY: [metric=value pairs]
```

### Prohibited Actions

1. **No Echo:** Never repeat input data back to user
2. **No Redundancy:** Don't repeat previous findings unless asked
3. **No Over-Explanation:** Keep explanations ≤3 sentences
4. **No Raw Content:** Use file paths instead of pasting contents

### File-Based State

```
.claude/
├── state/              # Current task state (JSON)
│   └── agent_results/  # Worker outputs
├── checkpoints/        # Summarization checkpoints (MD)
├── outputs/            # Large outputs (reports/, data/)
└── tools/              # Context management tools
    └── context_manager.py
```

**Full skill reference:** @~/.claude/skills/context-management/SKILL.md

---
*Root CLAUDE.md contains critical rules. This file adds orchestration context.*
