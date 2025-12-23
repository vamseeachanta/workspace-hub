---
name: agent-orchestration
description: Orchestrate AI agents using Claude Flow, swarm coordination, and multi-agent workflows. Use for complex tasks requiring multiple specialized agents, parallel execution, or coordinated problem-solving.
---

# Agent Orchestration Skill

## Overview

This skill enables orchestration of multiple AI agents for complex tasks. It covers swarm initialization, agent spawning, task coordination, and multi-agent workflows using Claude Flow and the workspace-hub agent ecosystem.

## Agent Categories

### Core Agents

| Agent | Purpose |
|-------|---------|
| `coder` | Implementation and coding |
| `reviewer` | Code review and quality |
| `tester` | Testing and verification |
| `planner` | Strategic planning |
| `researcher` | Information gathering |

### SPARC Agents

| Agent | Purpose |
|-------|---------|
| `specification` | Requirements analysis |
| `pseudocode` | Algorithm design |
| `architecture` | System design |
| `refinement` | TDD implementation |

### Specialized Agents

| Agent | Purpose |
|-------|---------|
| `backend-dev` | Backend/API development |
| `ml-developer` | Machine learning |
| `cicd-engineer` | CI/CD pipelines |
| `system-architect` | Architecture design |
| `api-docs` | API documentation |

### GitHub Agents

| Agent | Purpose |
|-------|---------|
| `pr-manager` | Pull request management |
| `code-review-swarm` | Automated code review |
| `issue-tracker` | Issue management |

## Swarm Topologies

### Hierarchical

Coordinator delegates to specialized workers:

```
        ┌─────────────────┐
        │   Coordinator   │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌───────┐  ┌───────┐  ┌───────┐
│Worker1│  │Worker2│  │Worker3│
└───────┘  └───────┘  └───────┘
```

**Best for:** Complex tasks with clear subtask boundaries

```javascript
// Initialize hierarchical swarm
mcp__claude-flow__swarm_init({
    topology: "hierarchical",
    maxAgents: 5,
    strategy: "auto"
})
```

### Mesh

Peer-to-peer collaboration:

```
┌───────┐     ┌───────┐
│Agent A│◄───►│Agent B│
└───┬───┘     └───┬───┘
    │      ╲  ╱   │
    │       ╲╱    │
    │       ╱╲    │
    │      ╱  ╲   │
┌───▼───┐     ┌───▼───┐
│Agent C│◄───►│Agent D│
└───────┘     └───────┘
```

**Best for:** Collaborative tasks requiring shared context

```javascript
mcp__claude-flow__swarm_init({
    topology: "mesh",
    maxAgents: 4
})
```

### Star

Central hub with peripheral agents:

```
         ┌───────┐
         │Agent A│
         └───┬───┘
             │
┌───────┐  ┌─▼─┐  ┌───────┐
│Agent B├──►Hub◄──┤Agent C│
└───────┘  └─┬─┘  └───────┘
             │
         ┌───▼───┐
         │Agent D│
         └───────┘
```

**Best for:** Tasks with central coordination point

```javascript
mcp__claude-flow__swarm_init({
    topology: "star",
    maxAgents: 6
})
```

### Ring

Sequential processing:

```
┌───────┐     ┌───────┐
│Agent A│────►│Agent B│
└───┬───┘     └───┬───┘
    ▲             │
    │             ▼
┌───┴───┐     ┌───────┐
│Agent D│◄────│Agent C│
└───────┘     └───────┘
```

**Best for:** Pipeline processing, sequential workflows

```javascript
mcp__claude-flow__swarm_init({
    topology: "ring",
    maxAgents: 4
})
```

## Agent Spawning

### Spawn Single Agent

```javascript
mcp__claude-flow__agent_spawn({
    type: "coder",
    name: "implementation-agent",
    capabilities: ["python", "typescript", "api-development"]
})
```

### Spawn Multiple Agents in Parallel

```javascript
mcp__claude-flow__agents_spawn_parallel({
    agents: [
        { type: "coder", name: "backend-coder" },
        { type: "tester", name: "test-writer" },
        { type: "reviewer", name: "code-reviewer" }
    ],
    maxConcurrency: 3
})
```

### Agent Types

```javascript
// Available agent types
const agentTypes = [
    "coordinator",
    "analyst",
    "optimizer",
    "documenter",
    "monitor",
    "specialist",
    "architect",
    "task-orchestrator",
    "code-analyzer",
    "perf-analyzer",
    "api-docs",
    "performance-benchmarker",
    "system-architect",
    "researcher",
    "coder",
    "tester",
    "reviewer"
];
```

## Task Orchestration

### Simple Task

```javascript
mcp__claude-flow__task_orchestrate({
    task: "Implement user authentication with JWT",
    strategy: "sequential",
    priority: "high"
})
```

### Complex Task with Dependencies

```javascript
mcp__claude-flow__task_orchestrate({
    task: "Build complete API with tests and documentation",
    strategy: "adaptive",
    priority: "high",
    dependencies: [
        "design-api-spec",
        "write-tests",
        "implement-endpoints",
        "create-documentation"
    ]
})
```

### Orchestration Strategies

| Strategy | Description |
|----------|-------------|
| `parallel` | Execute independent tasks simultaneously |
| `sequential` | Execute tasks in order |
| `adaptive` | Dynamically adjust based on results |
| `balanced` | Balance load across agents |

## Workflow Patterns

### 1. Code Review Swarm

```javascript
// Initialize review swarm
await mcp__claude-flow__swarm_init({
    topology: "hierarchical",
    maxAgents: 4
});

// Spawn review agents
await mcp__claude-flow__agents_spawn_parallel({
    agents: [
        { type: "reviewer", name: "security-reviewer" },
        { type: "reviewer", name: "performance-reviewer" },
        { type: "reviewer", name: "style-reviewer" }
    ]
});

// Orchestrate review
await mcp__claude-flow__task_orchestrate({
    task: "Review PR #123 for security, performance, and style",
    strategy: "parallel"
});
```

### 2. Feature Implementation

```javascript
// Sequential SPARC workflow
await mcp__claude-flow__swarm_init({ topology: "ring" });

// Phase agents
const phases = [
    { type: "specialist", name: "specification-agent" },
    { type: "specialist", name: "pseudocode-agent" },
    { type: "architect", name: "architecture-agent" },
    { type: "coder", name: "implementation-agent" },
    { type: "tester", name: "testing-agent" }
];

await mcp__claude-flow__agents_spawn_parallel({ agents: phases });

await mcp__claude-flow__task_orchestrate({
    task: "Implement new feature following SPARC methodology",
    strategy: "sequential"
});
```

### 3. Research and Analysis

```javascript
// Mesh for collaborative research
await mcp__claude-flow__swarm_init({ topology: "mesh" });

await mcp__claude-flow__agents_spawn_parallel({
    agents: [
        { type: "researcher", name: "literature-reviewer" },
        { type: "analyst", name: "data-analyst" },
        { type: "documenter", name: "summary-writer" }
    ]
});

await mcp__claude-flow__task_orchestrate({
    task: "Research and analyze best practices for microservices",
    strategy: "adaptive"
});
```

## Monitoring and Status

### Check Swarm Status

```javascript
mcp__claude-flow__swarm_status({ swarmId: "current" })
```

### Monitor Agent Metrics

```javascript
mcp__claude-flow__agent_metrics({ agentId: "agent-123" })
```

### List Active Agents

```javascript
mcp__claude-flow__agent_list({ swarmId: "current" })
```

### Get Task Results

```javascript
mcp__claude-flow__task_results({ taskId: "task-456" })
```

## Memory Management

### Store Information

```javascript
mcp__claude-flow__memory_usage({
    action: "store",
    key: "project-context",
    value: JSON.stringify(projectData),
    namespace: "project-alpha"
})
```

### Retrieve Information

```javascript
mcp__claude-flow__memory_usage({
    action: "retrieve",
    key: "project-context",
    namespace: "project-alpha"
})
```

### Search Memory

```javascript
mcp__claude-flow__memory_search({
    pattern: "api-*",
    namespace: "project-alpha",
    limit: 10
})
```

## Performance Optimization

### Topology Selection

Choose topology based on task:

| Task Type | Recommended Topology |
|-----------|---------------------|
| Code review | Hierarchical |
| Brainstorming | Mesh |
| Pipeline processing | Ring |
| Centralized coordination | Star |
| Mixed workloads | Adaptive |

### Auto-Optimize

```javascript
mcp__claude-flow__topology_optimize({ swarmId: "current" })
```

### Load Balancing

```javascript
mcp__claude-flow__load_balance({
    swarmId: "current",
    tasks: ["task1", "task2", "task3"]
})
```

## Error Handling

### Fault Tolerance

```javascript
mcp__claude-flow__daa_fault_tolerance({
    agentId: "agent-123",
    strategy: "restart"  // or "failover", "ignore"
})
```

### Recovery

```javascript
// Create snapshot
mcp__claude-flow__state_snapshot({ name: "before-risky-operation" })

// Restore if needed
mcp__claude-flow__context_restore({ snapshotId: "snapshot-id" })
```

## Integration with Claude Code

### Using Task Tool

For complex tasks, use Claude Code's Task tool:

```javascript
Task({
    description: "Complex multi-step analysis",
    prompt: "Analyze codebase and suggest improvements",
    subagent_type: "code-analyzer"
})
```

### Parallel Agent Execution

Launch multiple agents in parallel:

```javascript
// Single message with multiple Task calls
Task({ subagent_type: "researcher", ... })
Task({ subagent_type: "coder", ... })
Task({ subagent_type: "reviewer", ... })
```

## Best Practices

### Agent Selection

1. **Match agent to task**: Use specialized agents
2. **Limit concurrency**: Don't spawn too many agents
3. **Clear instructions**: Provide detailed prompts
4. **Monitor progress**: Check status regularly

### Swarm Management

1. **Choose appropriate topology**: Based on task structure
2. **Set reasonable timeouts**: Prevent hung agents
3. **Use memory for context**: Share information between agents
4. **Clean up**: Destroy swarms when done

### Error Handling

1. **Plan for failures**: Use fault tolerance
2. **Create snapshots**: Before risky operations
3. **Log extensively**: For debugging
4. **Graceful degradation**: Handle partial failures

## Cleanup

### Destroy Swarm

```javascript
mcp__claude-flow__swarm_destroy({ swarmId: "swarm-123" })
```

### Scale Down

```javascript
mcp__claude-flow__swarm_scale({
    swarmId: "current",
    targetSize: 2
})
```
