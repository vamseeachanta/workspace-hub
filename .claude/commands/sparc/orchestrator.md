# SPARC Orchestrator Mode

## Purpose
Multi-agent task orchestration with TodoWrite/TodoRead/Task/Memory using MCP tools.

## Activation

### Option 1: Using MCP Tools (Preferred in Claude Code)
```javascript
  mode: "orchestrator",
  task_description: "coordinate feature development"
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
- Task decomposition
- Agent coordination
- Resource allocation
- Progress tracking
- Result synthesis

## Integration Examples

### Using MCP Tools (Preferred)
```javascript
// Initialize orchestration swarm
  topology: "hierarchical",
  strategy: "auto",
  maxAgents: 8
}

// Spawn coordinator agent
  type: "coordinator",
  capabilities: ["task-planning", "resource-management"]
}

// Orchestrate tasks
  task: "feature development",
  strategy: "parallel",
  dependencies: ["auth", "ui", "api"]
}
```

### Using NPX CLI (Fallback)
```bash
# Initialize orchestration swarm

# Spawn coordinator agent

# Orchestrate tasks
```

## Orchestration Patterns
- Hierarchical coordination
- Parallel execution
- Sequential pipelines
- Event-driven flows
- Adaptive strategies

## Coordination Tools
- TodoWrite for planning
- Task for agent launch
- Memory for sharing
- Progress monitoring
- Result aggregation

## Workflow Example

### Using MCP Tools (Preferred)
```javascript
// 1. Initialize orchestration swarm
  topology: "hierarchical",
  maxAgents: 10
}

// 2. Create workflow
  name: "feature-development",
  steps: ["design", "implement", "test", "deploy"]
}

// 3. Execute orchestration
  mode: "orchestrator",
  options: {parallel: true, monitor: true},
  task_description: "develop user management system"
}

// 4. Monitor progress
  swarmId: "current",
  interval: 5000
}
```

### Using NPX CLI (Fallback)
```bash
# 1. Initialize orchestration swarm

# 2. Create workflow

# 3. Execute orchestration

# 4. Monitor progress
```
