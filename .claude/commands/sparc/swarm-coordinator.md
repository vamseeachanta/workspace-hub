# SPARC Swarm Coordinator Mode

## Purpose
Specialized swarm management with batch coordination capabilities.

## Activation

### Option 1: Using MCP Tools (Preferred in Claude Code)
```javascript
  mode: "swarm-coordinator",
  task_description: "manage development swarm",
  options: {
    topology: "hierarchical",
    max_agents: 10
  }
}
```

### Option 2: Using NPX CLI (Fallback when MCP not available)
```bash
# Use when running from terminal or MCP tools unavailable

# For alpha features
```

### Option 3: Local Installation
```bash
```

## Core Capabilities
- Swarm initialization
- Agent management
- Task distribution
- Load balancing
- Result collection

## Coordination Modes
- Hierarchical swarms
- Mesh networks
- Pipeline coordination
- Adaptive strategies
- Hybrid approaches

## Management Features
- Dynamic scaling
- Resource optimization
- Failure recovery
- Performance monitoring
- Quality assurance
