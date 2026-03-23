# WRK-1386 Completion

## Result
- **17 repos** CLAUDE.md trimmed from 31-747 lines → 8 lines (adapter format)
- **2 repos** skipped: aceengineercode, pyproject-starter (archived, read-only)
- **CODEX.md**: no files found in child repos (already clean)
- **0 repos** had CODEX.md to delete

## Repos Updated
aceengineer-admin, sabithaandkrishnaestates, achantas-data, teamresumes,
OGManufacturing, frontierdeepwater, client_projects, doris, aceengineer-website,
acma-projects, saipem, rock-oil-field, investments, seanation, sd-work,
pdf-large-reader, achantas-media

## Adapter Template (8 lines)
```
# {repo} — Claude Adapter
> Canonical instructions: workspace-hub/AGENTS.md | Rules: `.claude/rules/`
## Claude-Specific
- Retrieval first — consult `.claude/rules/`, `.claude/docs/`, workspace-hub docs before training knowledge
- Lifecycle skills (MANDATORY): work-queue-workflow + workflow-gatepass
- Context budget: 16KB max (Global 2KB + Workspace 4KB + Project 8KB + Local 2KB)
## Repo Overrides
<!-- Add repo-specific overrides below without weakening required gates -->
```

## Script
`scripts/operations/compliance/trim_claude_md.sh` — reusable for future compliance runs
