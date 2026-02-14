---
name: multi-agent-patterns
description: Design multi-agent systems with supervisor, peer-to-peer, and hierarchical architectures. Use for agent coordination, context isolation, and distributed workflows. Based on muratcankoylan/Agent-Skills-for-Context-Engineering.
version: 1.0.0
category: agents
last_updated: 2026-01-19
source: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering
related_skills:
  - memory-systems
  - parallel-dispatch
  - subagent-driven
---

# Multi-Agent Patterns Skill

## Overview

This skill addresses multi-agent system design, covering scenarios where supervisor patterns, swarm architectures, or agent coordination strategies are needed. Core insight: "Sub-agents exist primarily to isolate context, not to anthropomorphize role division."

## Quick Start

1. **Identify need** - Why multiple agents? (context limits, parallelism, specialization)
2. **Choose pattern** - Supervisor, peer-to-peer, or hierarchical
3. **Design communication** - Message passing, handoffs, state sharing
4. **Implement safeguards** - Validation, timeouts, conflict resolution
5. **Monitor** - Token usage, bottlenecks, failures

## When to Use

- Context window limits prevent single-agent solutions
- Tasks benefit from parallel execution
- Different domains require specialized knowledge
- Complex workflows need coordination
- Resilience through redundancy is required

## Three Primary Patterns

### 1. Supervisor/Orchestrator

**Structure:** Central coordinator delegates to specialists and synthesizes results.

```
         [Supervisor]
        /     |      \
   [Agent A] [Agent B] [Agent C]
       ↑        ↑         ↑
       └────────┴─────────┘
           Results flow up
```

**Best for:**
- Tasks with clear decomposition
- Human oversight needs
- Sequential dependencies
- Quality control requirements

**Key consideration:** The "telephone game problem" emerges when supervisors paraphrase sub-agent responses incorrectly.

**Solution:** Implement `forward_message` tool enabling direct sub-agent-to-user communication:

```python
def forward_message(agent_id: str, message: str, to: str = "user"):
    """Forward agent message directly without supervisor interpretation."""
    return {"from": agent_id, "message": message, "forwarded": True}
```

### 2. Peer-to-Peer/Swarm

**Structure:** No central control; agents communicate directly through protocols.

```
   [Agent A] ←→ [Agent B]
       ↑↓          ↑↓
   [Agent C] ←→ [Agent D]
```

**Best for:**
- Flexible exploration
- Emergent problem-solving
- Parallel processing
- Resilient architectures

**Key requirements:**
- Predefined communication protocols
- Explicit handoff mechanisms
- Shared state management
- Conflict resolution rules

### 3. Hierarchical

**Structure:** Layers of agents with strategy, planning, and execution tiers.

```
        [Strategy Layer]
              ↓
        [Planning Layer]
        /      |      \
   [Exec A] [Exec B] [Exec C]
```

**Best for:**
- Complex organizational workflows
- Multi-level abstraction
- Clear separation of concerns
- Enterprise-scale systems

**Layer responsibilities:**
- **Strategy:** Goals, priorities, resource allocation
- **Planning:** Task decomposition, scheduling, coordination
- **Execution:** Actual work, reporting, feedback

## Token Economics

**Reality check:** Multi-agent systems consume ~15x baseline tokens compared to single-agent approaches.

| Approach | Token Multiplier | Use Case |
|----------|------------------|----------|
| Single Agent | 1x | Simple, focused tasks |
| 2-3 Agents | 3-5x | Moderate complexity |
| Full Swarm | 10-20x | Complex, parallel work |

**Optimization strategies:**
- Model selection often provides larger gains than more agents
- Use smaller models for routine tasks
- Reserve large models for synthesis and decisions
- Implement aggressive context compression

## Communication Patterns

### Message Passing

```python
class AgentMessage:
    sender: str
    recipient: str
    content: str
    message_type: Literal["request", "response", "broadcast"]
    requires_ack: bool = False
```

### Handoff Protocol

```python
class Handoff:
    from_agent: str
    to_agent: str
    context: dict  # Compressed relevant state
    task: str
    expected_output: str
    timeout_seconds: int = 300
```

### State Sharing

```python
class SharedState:
    version: int
    last_updated: datetime
    data: dict
    lock_holder: Optional[str] = None

    def acquire_lock(self, agent_id: str) -> bool: ...
    def release_lock(self, agent_id: str) -> bool: ...
    def update(self, agent_id: str, changes: dict) -> bool: ...
```

## Implementation Guidance

### Validation Requirements

- Validate outputs before inter-agent transfer
- Check message format and completeness
- Verify agent capabilities before assignment
- Validate state consistency after updates

### Consensus Mechanisms

| Mechanism | Description | Best For |
|-----------|-------------|----------|
| Simple Majority | >50% agreement | Quick decisions |
| Weighted Voting | Votes weighted by confidence | Quality-sensitive |
| Quorum | Minimum respondents required | Fault tolerance |
| Leader Election | Designated decision maker | Speed |

**Recommendation:** Implement weighted voting rather than simple majority:

```python
def weighted_consensus(votes: List[Vote]) -> Decision:
    weighted_sum = sum(v.confidence * v.value for v in votes)
    total_weight = sum(v.confidence for v in votes)
    return Decision(value=weighted_sum / total_weight)
```

### Safeguards

1. **Execution TTL** - Prevent infinite loops:
   ```python
   max_execution_time = 300  # seconds
   max_iterations = 100
   ```

2. **Checkpoint Monitoring** - Detect supervisor bottlenecks:
   ```python
   checkpoint_interval = 30  # seconds
   alert_threshold = 3  # missed checkpoints
   ```

3. **Circuit Breaker** - Handle cascading failures:
   ```python
   failure_threshold = 3
   recovery_timeout = 60  # seconds
   ```

## Best Practices

### Do

1. Start with simplest pattern that works
2. Define explicit handoff protocols
3. Include state management from the start
4. Monitor token usage per agent
5. Implement graceful degradation
6. Log all inter-agent communication

### Don't

1. Use multi-agent for single-agent problems
2. Assume agents will coordinate implicitly
3. Ignore token costs during design
4. Skip validation between agents
5. Create deeply nested hierarchies
6. Forget timeout handling

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Agent timeout | Task too complex | Break into subtasks, extend timeout |
| Conflicting outputs | Ambiguous task | Clarify requirements, add validation |
| Lost messages | Network/state issues | Implement acknowledgments, retry |
| Infinite loop | Missing termination | Add TTL, iteration limits |
| Supervisor bottleneck | Too many reports | Add intermediate aggregators |

## Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Task completion rate | >95% | Successfully completed tasks |
| Token efficiency | >0.5 | Output value / tokens used |
| Coordination overhead | <30% | Tokens for coordination vs. work |
| Agent utilization | >70% | Active time vs. waiting |
| Error rate | <5% | Failed inter-agent operations |

## Pattern Selection Guide

```
Is context window sufficient?
├── Yes → Single agent
└── No → Are tasks parallelizable?
    ├── Yes → Can agents work independently?
    │   ├── Yes → Peer-to-peer
    │   └── No → Supervisor with parallel workers
    └── No → Is there clear hierarchy?
        ├── Yes → Hierarchical
        └── No → Supervisor/Orchestrator
```

## Related Skills

- [memory-systems](../memory-systems/SKILL.md) - Cross-session persistence
- [parallel-dispatch](../parallel-dispatch/SKILL.md) - Concurrent agent execution
- [subagent-driven](../../development/subagent-driven/SKILL.md) - Task execution pattern

---

## Version History

- **1.0.0** (2026-01-19): Initial release adapted from Agent-Skills-for-Context-Engineering
