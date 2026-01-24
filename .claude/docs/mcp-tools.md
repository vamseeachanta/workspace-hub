# MCP Tools Reference

> Load on-demand for MCP coordination setup

## Setup

```bash
claude mcp add claude-flow npx claude-flow@alpha mcp start
claude mcp add ruv-swarm npx ruv-swarm mcp start        # Optional
claude mcp add flow-nexus npx flow-nexus@latest mcp start  # Optional
```

## Tool Categories

### Coordination
| Tool | Purpose |
|------|---------|
| `swarm_init` | Initialize topology (mesh/hierarchical/ring/star) |
| `agent_spawn` | Register agent types |
| `task_orchestrate` | High-level workflow orchestration |

### Monitoring
| Tool | Purpose |
|------|---------|
| `swarm_status` | Track coordination health |
| `agent_list` | List active agents |
| `agent_metrics` | Performance metrics |
| `task_status` | Task progress |
| `task_results` | Completed task results |

### Memory & Neural
| Tool | Purpose |
|------|---------|
| `memory_usage` | Store/retrieve shared state |
| `neural_status` | Neural agent status |
| `neural_train` | Train patterns |
| `neural_patterns` | Get cognitive patterns |

### GitHub Integration
| Tool | Purpose |
|------|---------|
| `github_swarm` | Repository coordination |
| `repo_analyze` | Analyze repository |
| `pr_enhance` | Enhance pull requests |
| `issue_triage` | Triage issues |
| `code_review` | Code review |

### System
| Tool | Purpose |
|------|---------|
| `benchmark_run` | Performance benchmarks |
| `features_detect` | Detect capabilities |
| `swarm_monitor` | Real-time monitoring |

## Key Principle

**MCP tools coordinate, Claude Code Task tool executes.**

- MCP: Define topology, register agents, orchestrate workflows
- Task tool: Spawn real agents, create files, run code

## Context Budget Allocation

> Managing token budgets across MCP servers prevents context exhaustion and maintains orchestrator efficiency.

### Why Budget Allocation Matters

MCP tools consume context tokens in two ways:
1. **Tool definitions** - Schema loaded at session start
2. **Tool responses** - Data returned from each invocation

Without budget discipline:
- Context fills rapidly with verbose tool outputs
- Orchestrator loses planning capacity
- Session degrades into reactive mode
- Critical state gets evicted from context

### Token Budget by Server

| MCP Server | Token Budget | Priority | Notes |
|------------|--------------|----------|-------|
| claude-flow | 2000 | High | Core orchestration, swarm coordination |
| Browser tools | 500 | Low | Web automation, use sparingly |
| Memory tools | 1000 | Medium | State persistence, selective retrieval |
| GitHub tools | 800 | Medium | PR/issue management, batch operations |
| Neural tools | 600 | Low | Pattern training, infrequent use |

**Total MCP allocation**: ~5000 tokens (25% of recommended orchestrator budget)

### How to Prioritize MCP Usage

**High Priority (always available)**
- `swarm_init` - Essential for topology setup
- `swarm_status` - Quick health checks
- `task_orchestrate` - Workflow coordination

**Medium Priority (use when needed)**
- `memory_usage` - Store critical state only
- `agent_spawn` - Register new agent types
- `github_swarm` - Batch repository operations

**Low Priority (minimize usage)**
- `agent_metrics` - Verbose output, delegate to subagent
- `neural_train` - Heavy operation, always delegate
- Browser tools - High token cost, use read_page sparingly

### Warning Signs of Budget Exhaustion

Watch for these indicators:

| Symptom | Likely Cause | Remediation |
|---------|--------------|-------------|
| Repeated tool calls | Forgetting previous results | Store key data in memory tool |
| Truncated responses | Context overflow | Delegate verbose operations |
| Lost planning state | Eviction pressure | Reduce MCP response sizes |
| Slow responses | Context processing overhead | Batch tool calls |

### Tips for Efficient MCP Usage

1. **Batch operations**
   - Combine multiple queries into single tool calls
   - Use filters to reduce response size
   - Request only fields you need

2. **Delegate verbose outputs**
   - `agent_metrics` → spawn subagent to analyze
   - `repo_analyze` → subagent for detailed review
   - Browser `read_page` → subagent for page parsing

3. **Use memory strategically**
   - Store summarized results, not raw output
   - Key critical state with semantic names
   - Retrieve selectively, not wholesale

4. **Monitor consumption**
   ```
   Rule of thumb: If MCP output > 500 tokens, delegate
   ```

5. **Prefer lightweight checks**
   - `swarm_status` over `agent_metrics`
   - `task_status` over `task_results`
   - Targeted queries over full scans

### Budget Recovery Strategies

When approaching exhaustion:

1. **Summarize and store** - Compress verbose state into memory
2. **Spawn fresh subagent** - Isolate heavy operations
3. **Reset non-critical tools** - Clear cached browser state
4. **Prioritize core tools** - Keep claude-flow, drop browser tools
