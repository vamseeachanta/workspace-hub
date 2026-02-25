# Archived Skills

Skills moved here to reduce context token usage. These are still available via `/skill-search`.

## Archived Categories

| Category | Skills | Reason |
|----------|--------|--------|
| `flow-nexus/` | 9 | MCP server removed |
| `hive-mind/` | 12 | Replaced by Task tool delegation |

## Restoration

To restore a skill category:
```bash
mv .claude/commands/_archive/<category> .claude/commands/
```

## Search Archived Skills

Use `/skill-search <query>` to find skills in archive without loading them all into context.
