---
name: core-context-management-validatecontextsh
description: 'Sub-skill of core-context-management: validate_context.sh (+4).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# validate_context.sh (+4)

## validate_context.sh


Location: `scripts/context/validate_context.sh`

Validates context file sizes and generates report.

## analyze_patterns.sh


Location: `scripts/context/analyze_patterns.sh`

Analyzes git history to identify instruction patterns.

## improve_context.sh


Location: `scripts/context/improve_context.sh`

Applies approved improvements to context files.

## daily_context_check.sh


Location: `scripts/context/daily_context_check.sh`

Runs all checks and generates daily report.

## optimize_mcp_context.sh


Location: `scripts/optimize-mcp-context.sh`

Optimizes MCP configuration across workspace repos by removing bloated servers (flow-nexus, agentic-payments) to save ~8,500 tokens per repo.

```bash
# Dry run - see what would change
./scripts/optimize-mcp-context.sh --dry-run

./scripts/optimize-mcp-context.sh --lean


*See sub-skills for full details.*
