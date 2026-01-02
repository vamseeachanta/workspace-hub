# Swarm Coordination Skills

> Version: 1.0.0
> Created: 2026-01-02
> Category: Multi-Agent Coordination

## Overview

This directory contains skills for swarm coordination and hive mind operations. These skills enable multi-agent orchestration with different topologies, consensus mechanisms, and coordination patterns.

## Skills Index

### Coordination Topologies

| Skill | Description | Priority |
|-------|-------------|----------|
| [swarm-hierarchical](./swarm-hierarchical/SKILL.md) | Queen-led hierarchical coordination with worker delegation | Critical |
| [swarm-mesh](./swarm-mesh/SKILL.md) | Peer-to-peer mesh network with distributed decisions | High |
| [swarm-adaptive](./swarm-adaptive/SKILL.md) | Dynamic topology switching with ML optimization | Critical |

### Hive Mind Agents

| Skill | Description | Priority |
|-------|-------------|----------|
| [swarm-queen](./swarm-queen/SKILL.md) | Sovereign orchestrator for strategic decisions | Critical |
| [swarm-collective](./swarm-collective/SKILL.md) | Distributed cognitive processes and consensus | Critical |
| [swarm-memory](./swarm-memory/SKILL.md) | Distributed memory management and caching | Critical |
| [swarm-scout](./swarm-scout/SKILL.md) | Information reconnaissance and discovery | High |
| [swarm-worker](./swarm-worker/SKILL.md) | Task execution with progress tracking | High |

## When to Use Each Topology

| Topology | Best For | Key Characteristics |
|----------|----------|---------------------|
| Hierarchical | Complex projects, clear accountability | Central control, rapid decisions |
| Mesh | Fault tolerance, parallel work | No single point of failure, distributed |
| Adaptive | Changing requirements | ML-optimized, dynamic switching |

## Quick Start

### Initialize a Swarm

```bash
# Hierarchical swarm
mcp__claude-flow__swarm_init hierarchical --maxAgents=10 --strategy=adaptive

# Mesh network
mcp__claude-flow__swarm_init mesh --maxAgents=12 --strategy=distributed

# Adaptive (auto-selecting)
mcp__claude-flow__swarm_init auto --maxAgents=15 --strategy=adaptive
```

### Spawn Agents

```bash
# Via MCP
mcp__claude-flow__agent_spawn researcher --capabilities="research,analysis"
mcp__claude-flow__agent_spawn coder --capabilities="implementation,testing"

# Via Claude Code Task tool (preferred for execution)
Task("Research agent", "Analyze requirements", "researcher")
Task("Coder agent", "Implement features", "coder")
```

### Memory Coordination

All swarm agents use the coordination namespace:

```javascript
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/[agent]/status",
  namespace: "coordination",
  value: JSON.stringify({...})
}
```

## Memory Key Conventions

| Pattern | Purpose |
|---------|---------|
| `swarm/[agent]/status` | Agent's current status |
| `swarm/[agent]/progress` | Task progress |
| `swarm/[agent]/complete` | Completion details |
| `swarm/shared/*` | Shared coordination data |
| `swarm/broadcast/*` | Broadcast messages |

## Integration with Claude Code

### MCP Tools vs Claude Code Task Tool

- **MCP Tools**: Set up coordination topology, configure agents
- **Claude Code Task Tool**: Spawn agents that do actual work

### Example Workflow

```javascript
// 1. MCP: Set up coordination
mcp__claude-flow__swarm_init hierarchical --maxAgents=8

// 2. Claude Code: Spawn working agents
Task("Backend developer", "Build REST API", "coder")
Task("Frontend developer", "Create React UI", "coder")
Task("Test engineer", "Write tests", "tester")

// 3. MCP: Monitor progress
mcp__claude-flow__swarm_status
mcp__claude-flow__performance_report
```

## Related Skills

- Core agents in `/workspace-hub/agents/`
- GitHub integration in `/workspace-hub/github/`
- Performance analysis in `/workspace-hub/analysis/`

---

*Swarm coordination skills for workspace-hub multi-agent operations*
