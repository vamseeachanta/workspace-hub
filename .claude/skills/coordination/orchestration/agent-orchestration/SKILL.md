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
related_skills:
  - sparc-workflow
  - repo-sync
  - compliance-check
hooks:
  pre: |
  post: |
requires: []
see_also: []
---

# Agent Orchestration Skill

> Coordinate multiple AI agents using swarm topologies, parallel execution, and Claude Flow for complex multi-step tasks.

## Quick Start

```javascript
// Initialize a swarm for complex task

// Spawn specialized agents
    agents: [
        { type: "coder", name: "backend" },
        { type: "tester", name: "qa" },
        { type: "reviewer", name: "quality" }
    ]
})

// Orchestrate the task
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
    topology: "ring",
    maxAgents: 4
})
```

## Agent Spawning

### Spawn Single Agent

```javascript
    type: "coder",
    name: "implementation-agent",
    capabilities: ["python", "typescript", "api-development"]
})
```

### Spawn Multiple Agents in Parallel

```javascript
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
    task: "Implement user authentication with JWT",
    strategy: "sequential",
    priority: "high"
})
```

### Complex Task with Dependencies

```javascript
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
    topology: "hierarchical",
    maxAgents: 4
});

// Spawn review agents
    agents: [
        { type: "reviewer", name: "security-reviewer" },
        { type: "reviewer", name: "performance-reviewer" },
        { type: "reviewer", name: "style-reviewer" }
    ]
});

// Orchestrate review
    task: "Review PR #123 for security, performance, and style",
    strategy: "parallel"
});
```

### 2. Feature Implementation

```javascript
// Sequential SPARC workflow

// Phase agents
const phases = [
    { type: "specialist", name: "specification-agent" },
    { type: "specialist", name: "pseudocode-agent" },
    { type: "architect", name: "architecture-agent" },
    { type: "coder", name: "implementation-agent" },
    { type: "tester", name: "testing-agent" }
];


    task: "Implement new feature following SPARC methodology",
    strategy: "sequential"
});
```

### 3. Research and Analysis

```javascript
// Mesh for collaborative research

    agents: [
        { type: "researcher", name: "literature-reviewer" },
        { type: "analyst", name: "data-analyst" },
        { type: "documenter", name: "summary-writer" }
    ]
});

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
```

### Monitor Agent Metrics

```javascript
```

### List Active Agents

```javascript
```

### Get Task Results

```javascript
```

## Memory Management

### Store Information

```javascript
    action: "store",
    key: "project-context",
    value: JSON.stringify(projectData),
    namespace: "project-alpha"
})
```

### Retrieve Information

```javascript
    action: "retrieve",
    key: "project-context",
    namespace: "project-alpha"
})
```

### Search Memory

```javascript
    pattern: "api-*",
    namespace: "project-alpha",
    limit: 10
})
```

## Error Handling

### Agent Spawn Failures

```javascript
// Check agent status after spawning
if (status.agents.length < expectedCount) {
    // Retry failed spawns
}
```

### Task Orchestration Failures

```javascript
// Use fault tolerance for critical tasks
    agentId: "agent-123",
    strategy: "restart"  // or "failover", "ignore"
})
```

### Recovery

```javascript
// Create snapshot before risky operations

// Restore if needed
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
```

### Load Balancing

```javascript
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
```

### Hooks

```bash
# Pre-task hook

# Post-task hook
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
```

### Scale Down

```javascript
    swarmId: "current",
    targetSize: 2
})
```

## References

- [AI Agent Guidelines](../docs/modules/ai/AI_AGENT_GUIDELINES.md)
- [Development Workflow](../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format - added Quick Start, When to Use, Execution Checklist, Error Handling consolidation, Metrics, Integration Points, MCP hooks
- **1.0.0** (2024-10-15): Initial release with swarm topologies, agent spawning, task orchestration, memory management, performance optimization
