# Module: Adding Context — Claude Code in Action

## Key Principle
Too much irrelevant context DECREASES performance. Guide Claude toward relevant files only.

## /init Command
- Run once when starting in a new project
- Claude analyzes codebase → writes `CLAUDE.md`
- Permission prompts: Enter = approve each write; Shift+Tab = allow all writes freely

## CLAUDE.md Locations

| File | Scope | Committed? |
|------|-------|-----------|
| `CLAUDE.md` | Project — shared with all engineers | Yes |
| `CLAUDE.local.md` | Project — personal only | No |
| `~/.claude/CLAUDE.md` | All projects on this machine | N/A |

## Adding Custom Instructions — # Memory Mode
Type `#` to enter memory mode. Claude merges the instruction into CLAUDE.md intelligently.
Example: `# Use comments sparingly. Only comment complex code.`

## @ File Mentions
- In chat: `@auth` → Claude shows matching files, includes selected one in context
- In CLAUDE.md: `@prisma/schema.prisma` → file included in every request automatically

Example CLAUDE.md entry:
```
The database schema is defined in the @prisma/schema.prisma file. Reference it anytime
you need to understand the structure of data stored in the database.
```

## Workspace Gap Analysis

| Course feature | Workspace status | Decision |
|---------------|-----------------|----------|
| CLAUDE.md per project | ✓ All 6 repos have CLAUDE.md (≤20 line limit enforced) | Keep |
| ~/.claude/CLAUDE.md | ✓ Exists (global rules) | Keep |
| CLAUDE.local.md | Not used | **Rejected** — siloed knowledge breaks multi-machine workflows. All workstation knowledge lives in shared `workstations/SKILL.md` (WRK-1110) |
| @ mentions in CLAUDE.md | Partially used | **Adopt** — build full context pipeline (WRK-1111) |
| # memory mode | Known but rarely used | Keep as-is; prefer direct skill edits |
| /init | Not needed | CLAUDE.md already maintained manually |

## Spun-off WRKs

- **WRK-1110**: Enhance workstations skill — hardware utility analysis, future planning, upgrade roadmap
- **WRK-1111**: @ file reference pipeline — auto-include key schemas/configs in CLAUDE.md across all repos
