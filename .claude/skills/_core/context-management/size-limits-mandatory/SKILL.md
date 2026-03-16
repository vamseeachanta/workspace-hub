---
name: core-context-management-size-limits-mandatory
description: 'Sub-skill of core-context-management: Size Limits (MANDATORY) (+3).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# Size Limits (MANDATORY) (+3)

## Size Limits (MANDATORY)


| File | Max Size | Max Lines | Purpose |
|------|----------|-----------|---------|
| `~/.claude/CLAUDE.md` | 2KB | 50 | Global preferences |
| Workspace `CLAUDE.md` | 4KB | 100 | Delegation patterns |
| Project `CLAUDE.md` | 8KB | 200 | Project rules |
| `CLAUDE.local.md` | 2KB | 50 | User overrides |

## Validation Command


```bash
# Run validation across all repos
./scripts/context/validate_context.sh

# Check single repo
./scripts/context/validate_context.sh digitalmodel
```

## Content Categories


**MUST be in CLAUDE.md:**
- Mandatory behavioral rules (TDD, batching, etc.)
- Plan mode conventions
- Cross-review requirements
- File organization rules
- Key delegation patterns

**MUST be in .claude/docs/ (reference):**
- Agent lists and descriptions
- MCP tool reference tables
- Execution workflow diagrams
- Code examples and patterns
- Memory namespace details

## Automated Improvement


The skill analyzes past work to suggest improvements:

1. **Pattern Detection**: Identifies frequently used instructions
2. **Redundancy Removal**: Flags duplicate content across files
3. **Usage Analysis**: Tracks which docs are actually loaded
4. **Suggestion Generation**: Proposes optimizations

---
