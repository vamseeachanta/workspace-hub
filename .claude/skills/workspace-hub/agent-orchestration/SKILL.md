---
name: agent-orchestration
description: Orchestrate AI agents using Claude Flow, swarm coordination, and multi-agent workflows. Use for complex tasks requiring multiple specialized agents, parallel execution, or coordinated problem-solving.
version: 1.1.0
category: workspace-hub
type: skill
capabilities:
  - swarm_coordination
  - agent_spawning
  - task_orchestration
  - memory_management
  - parallel_execution
tools:
  - Task
  - Bash
  - mcp__claude-flow__swarm_init
  - mcp__claude-flow__agent_spawn
  - mcp__claude-flow__agents_spawn_parallel
  - mcp__claude-flow__task_orchestrate
  - mcp__claude-flow__swarm_status
  - mcp__claude-flow__agent_list
  - mcp__claude-flow__memory_usage
  - mcp__claude-flow__memory_search
related_skills:
  - sparc-workflow
  - repo-sync
  - compliance-check
hooks:
  pre: |
    npx claude-flow@alpha hooks pre-task --description "Agent orchestration"
  post: |
    npx claude-flow@alpha hooks post-task --task-id "swarm-complete"
---

# Agent Orchestration Skill

> Coordinate multiple AI agents using swarm topologies, parallel execution, and Claude Flow for complex multi-step tasks.

## Quick Start

```javascript
// Initialize a swarm for complex task
mcp__claude-flow__swarm_init({ topology: "hierarchical", maxAgents: 5 })

// Spawn specialized agents
mcp__claude-flow__agents_spawn_parallel({
    agents: [
        { type: "coder", name: "backend" },
        { type: "tester", name: "qa" },
        { type: "reviewer", name: "quality" }
    ]
})

// Orchestrate the task
mcp__claude-flow__task_orchestrate({
    task: "Build REST API with tests",
    strategy: "adaptive"
})
```

## When to Use

- Complex tasks requiring multiple specialized agents (coder, tester, reviewer)
- Parallel execution to speed up independent subtasks
- Code review requiring multiple perspectives (security, performance, style)
- Research tasks needing distributed information gathering
- Cross-repository changes requiring coordinated commits

## Prerequisites

- Claude Flow MCP server configured (`claude mcp add claude-flow npx claude-flow@alpha mcp start`)
- Understanding of swarm topologies
- Familiarity with agent types and capabilities
- Claude Code Task tool for agent execution

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

## Execution Checklist

- [ ] Determine task complexity and required agent types
- [ ] Select appropriate swarm topology
- [ ] Initialize swarm with correct configuration
- [ ] Spawn required agents (prefer parallel spawning)
- [ ] Define task with clear objectives and dependencies
- [ ] Orchestrate with appropriate strategy
- [ ] Monitor progress with status checks
- [ ] Collect and consolidate results
- [ ] Clean up swarm when complete

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

## Error Handling

### Agent Spawn Failures

```javascript
// Check agent status after spawning
const status = await mcp__claude-flow__agent_list({ swarmId: "current" });
if (status.agents.length < expectedCount) {
    // Retry failed spawns
    await mcp__claude-flow__agent_spawn({ type: "coder", name: "retry-agent" });
}
```

### Task Orchestration Failures

```javascript
// Use fault tolerance for critical tasks
mcp__claude-flow__daa_fault_tolerance({
    agentId: "agent-123",
    strategy: "restart"  // or "failover", "ignore"
})
```

### Recovery

```javascript
// Create snapshot before risky operations
mcp__claude-flow__state_snapshot({ name: "before-risky-operation" })

// Restore if needed
mcp__claude-flow__context_restore({ snapshotId: "snapshot-id" })
```

### Swarm Coordination Issues

- **Topology mismatch**: Choose topology based on task structure
- **Agent overload**: Scale down or use load balancing
- **Memory conflicts**: Use namespaced memory storage
- **Timeout issues**: Set reasonable timeouts, monitor progress

## Metrics & Success Criteria

- **Agent Spawn Time**: < 2 seconds per agent
- **Task Completion Rate**: >= 95%
- **Coordination Overhead**: < 10% of total execution time
- **Memory Usage**: Efficient namespace isolation
- **Parallel Speedup**: 2-4x improvement for parallelizable tasks

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

## Integration Points

### MCP Tools

```javascript
// Full orchestration example
mcp__claude-flow__swarm_init({ topology: "hierarchical", maxAgents: 6 })
mcp__claude-flow__agents_spawn_parallel({ agents: [...] })
mcp__claude-flow__task_orchestrate({ task: "...", strategy: "adaptive" })
mcp__claude-flow__swarm_status({})
mcp__claude-flow__swarm_destroy({ swarmId: "..." })
```

### Hooks

```bash
# Pre-task hook
npx claude-flow@alpha hooks pre-task --description "[task]"

# Post-task hook
npx claude-flow@alpha hooks post-task --task-id "[task]"
```

### Related Skills

- [sparc-workflow](../sparc-workflow/SKILL.md) - SPARC methodology
- [repo-sync](../repo-sync/SKILL.md) - Repository management
- [compliance-check](../compliance-check/SKILL.md) - Standards verification

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

## References

- [Claude Flow Documentation](https://github.com/ruvnet/claude-flow)
- [AI Agent Guidelines](../docs/modules/ai/AI_AGENT_GUIDELINES.md)
- [Development Workflow](../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format - added Quick Start, When to Use, Execution Checklist, Error Handling consolidation, Metrics, Integration Points, MCP hooks
- **1.0.0** (2024-10-15): Initial release with swarm topologies, agent spawning, task orchestration, memory management, performance optimization
