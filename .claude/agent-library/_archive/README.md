# Archived Agents

> **Archived:** 2026-01-18
> **Reason:** Complexity overhead - native Task tool delegation is simpler and sufficient

## Why These Were Archived

These agents were designed for complex multi-agent orchestration scenarios that add unnecessary complexity for typical workspace-hub usage. The native Claude Code Task tool with `subagent_type` provides equivalent functionality with less overhead.

## Archived Categories

| Category | Agent Count | Reason |
|----------|-------------|--------|
| `consensus/` | 7 | Byzantine/Raft consensus overkill for single-user |
| `flow-nexus/` | 9 | External platform integration not needed |
| `hive-mind/` | 5 | Complex swarm orchestration replaced by Task tool |
| `optimization/` | 5 | Performance optimization handled by Task tool |
| `neural/` | 0 | Experimental, never fully implemented |
| `goal/` | 0 | Goal planning covered by `core/planner.md` |

## When to Restore

Consider restoring these agents if you need:

1. **consensus/** - Distributed systems with multiple users requiring consensus
2. **flow-nexus/** - Integration with Flow Nexus cloud platform
3. **hive-mind/** - True multi-agent swarm with shared memory
4. **optimization/** - Advanced performance profiling beyond Task tool

## How to Restore

```bash
# Restore a single category
mv .claude/agent-library/_archive/consensus .claude/agent-library/

# Restore all archived agents
mv .claude/agent-library/_archive/* .claude/agent-library/
rmdir .claude/agent-library/_archive
```

## Recommended Alternative

Use Task tool delegation instead:

```
# Instead of complex swarm coordination:
Task(subagent_type="general-purpose", prompt="...", load_agent="@core/coder.md")

# Instead of consensus agents:
Task(subagent_type="Plan", prompt="Design approach and validate")

# Instead of optimization agents:
Task(subagent_type="Bash", prompt="Profile and optimize")
```

## Active Agent Categories

The following categories remain active and recommended:

- `core/` - coder, tester, reviewer, planner, researcher
- `devops/` - database, infrastructure, security-audit, observability
- `github/` - pr-manager, code-review-swarm, release-manager
- `sparc/` - specification, pseudocode, architecture
- `domain/` - engineering domain specialists
- `data/` - ML and data processing
- `visualization/` - chart and dashboard agents
