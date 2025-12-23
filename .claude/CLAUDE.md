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

## Key References

- Full agent list: @docs/modules/ai/AI_AGENT_GUIDELINES.md
- HTML standards: @docs/modules/standards/HTML_REPORTING_STANDARDS.md
- File organization: @docs/modules/standards/FILE_ORGANIZATION_STANDARDS.md
- Development workflow: @docs/modules/workflow/DEVELOPMENT_WORKFLOW.md

---
*Root CLAUDE.md contains critical rules. This file adds orchestration context.*
