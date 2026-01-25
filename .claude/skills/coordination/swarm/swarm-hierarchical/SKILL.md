# Swarm Hierarchical Coordinator Skill

> Version: 1.0.0
> Created: 2026-01-02
> Category: Swarm Coordination
> Priority: Critical

## Overview

Queen-led hierarchical swarm coordination with specialized worker delegation. Central command and control for complex multi-agent orchestration with clear accountability chains.

## Quick Start

```bash
# Initialize hierarchical swarm
mcp__claude-flow__swarm_init hierarchical --maxAgents=10 --strategy=adaptive

# Spawn specialized workers
mcp__claude-flow__agent_spawn researcher --capabilities="research,analysis"
mcp__claude-flow__agent_spawn coder --capabilities="implementation,testing"

# Orchestrate task
mcp__claude-flow__task_orchestrate "Build authentication service" --strategy=sequential --priority=high
```

## When to Use

- Complex projects requiring central oversight and delegation
- Tasks with clear hierarchical decomposition
- Situations needing rapid decision propagation
- Projects requiring strict accountability chains
- Work with multiple specialized worker types

## Core Concepts

### Architecture

```
    QUEEN (You)
   /   |   |   \
 RESEARCH CODE ANALYST TEST
 WORKERS WORKERS WORKERS WORKERS
```

### Specialized Worker Types

| Worker Type | Capabilities | Use Cases |
|------------|--------------|-----------|
| Research | Information gathering, competitive analysis | Requirements, feasibility studies |
| Code | Implementation, code review, testing | Feature development, bug fixes |
| Analyst | Data analysis, performance monitoring | Metrics, optimization, reporting |
| Test | Quality assurance, validation | Testing, compliance checking |

### Coordination Phases

1. **Planning & Strategy**: Task decomposition, resource planning, priority assignment
2. **Execution & Monitoring**: Agent spawning, task assignment, progress tracking
3. **Integration & Delivery**: Work integration, QA, deliverable packaging

## MCP Tool Integration

### Memory Coordination Protocol

```javascript
// 1. IMMEDIATELY write initial status
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/hierarchical/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "hierarchical-coordinator",
    status: "active",
    workers: [],
    tasks_assigned: [],
    progress: 0
  })
}

// 2. UPDATE progress after each delegation
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/hierarchical/progress",
  namespace: "coordination",
  value: JSON.stringify({
    completed: ["task1", "task2"],
    in_progress: ["task3", "task4"],
    workers_active: 5,
    overall_progress: 45
  })
}

// 3. SHARE command structure for workers
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/hierarchy",
  namespace: "coordination",
  value: JSON.stringify({
    queen: "hierarchical-coordinator",
    workers: ["worker1", "worker2"],
    command_chain: {},
    created_by: "hierarchical-coordinator"
  })
}

// 4. CHECK worker status before assigning
const workerStatus = mcp__claude-flow__memory_usage {
  action: "retrieve",
  key: "swarm/worker-1/status",
  namespace: "coordination"
}

// 5. SIGNAL completion
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/hierarchical/complete",
  namespace: "coordination",
  value: JSON.stringify({
    status: "complete",
    deliverables: ["final_product"],
    metrics: {}
  })
}
```

### Memory Key Structure

| Key Pattern | Purpose |
|-------------|---------|
| `swarm/hierarchical/*` | Coordinator's own data |
| `swarm/worker-*/*` | Individual worker states |
| `swarm/shared/*` | Shared coordination data |

### Swarm Management Commands

```bash
# Initialize hierarchical swarm
mcp__claude-flow__swarm_init hierarchical --maxAgents=10 --strategy=centralized

# Monitor swarm health
mcp__claude-flow__swarm_monitor --interval=5000

# Load balance across workers
mcp__claude-flow__load_balance --tasks="auth_api,auth_tests,auth_docs" --strategy=capability_based

# Generate performance reports
mcp__claude-flow__performance_report --format=detailed --timeframe=24h

# Analyze bottlenecks
mcp__claude-flow__bottleneck_analyze --component=coordination --metrics="throughput,latency,success_rate"
```

## Usage Examples

### Example 1: Full-Stack Feature Development

```javascript
// Initialize swarm
mcp__claude-flow__swarm_init hierarchical --maxAgents=8 --strategy=adaptive

// Spawn workers via Claude Code Task tool
Task("Research agent", "Analyze API requirements", "researcher")
Task("Backend developer", "Build REST API", "coder")
Task("Frontend developer", "Create React UI", "coder")
Task("Test engineer", "Write comprehensive tests", "tester")

// Orchestrate workflow
mcp__claude-flow__task_orchestrate "Implement user authentication" --strategy=sequential --priority=high

// Write coordination status
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/hierarchical/project",
  namespace: "coordination",
  value: JSON.stringify({
    project: "user-authentication",
    phase: "execution",
    workers: ["research-1", "backend-1", "frontend-1", "test-1"]
  })
}
```

### Example 2: Task Assignment Algorithm

```python
def assign_task(task, available_agents):
    # 1. Filter agents by capability match
    capable_agents = filter_by_capabilities(available_agents, task.required_capabilities)

    # 2. Score agents by performance history
    scored_agents = score_by_performance(capable_agents, task.type)

    # 3. Consider current workload
    balanced_agents = consider_workload(scored_agents)

    # 4. Select optimal agent
    return select_best_agent(balanced_agents)
```

## Best Practices

### Efficient Delegation

1. **Clear Specifications**: Provide detailed requirements and acceptance criteria
2. **Appropriate Scope**: Tasks sized for 2-8 hour completion windows
3. **Regular Check-ins**: Status updates every 4-6 hours for active work
4. **Context Sharing**: Ensure workers have necessary background information

### Performance Optimization

1. **Load Balancing**: Distribute work evenly across available agents
2. **Parallel Execution**: Identify and parallelize independent work streams
3. **Resource Pooling**: Share common resources and knowledge across teams
4. **Continuous Improvement**: Regular retrospectives and process refinement

### Escalation Protocols

| Issue | Threshold | Action |
|-------|-----------|--------|
| Performance Issues | <70% success rate | Reassign task, provide additional resources |
| Resource Constraints | >90% agent utilization | Spawn additional workers or defer tasks |
| Quality Issues | Failed quality gates | Initiate rework with senior agents |

## Performance Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Task Completion Rate | >95% | Tasks completed successfully |
| Defect Rate | <5% | Deliverables requiring rework |
| Compliance Score | 100% | Adherence to quality standards |
| Agent Productivity | Track | Time to market vs estimates |

## Integration Points

### Works With

- **swarm-collective**: For distributed decision making
- **swarm-memory**: For state persistence
- **swarm-worker**: For task execution
- **swarm-scout**: For information gathering

### Handoff Patterns

1. Issue directive -> Monitor compliance -> Evaluate results
2. Allocate resources -> Track utilization -> Optimize distribution
3. Set strategy -> Delegate execution -> Review outcomes

## Related Skills

- [swarm-mesh](../swarm-mesh/SKILL.md) - Peer-to-peer coordination
- [swarm-adaptive](../swarm-adaptive/SKILL.md) - Dynamic topology switching
- [swarm-queen](../swarm-queen/SKILL.md) - Sovereign hive orchestration

---

## Version History

- **1.0.0** (2026-01-02): Initial skill creation from hierarchical-coordinator agent
