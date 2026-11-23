# auto agent

Automatically spawn and manage agents based on task requirements.

## Usage

```bash
```

## Options

- `--task, -t <description>` - Task description for agent analysis
- `--max-agents, -m <number>` - Maximum agents to spawn (default: auto)
- `--min-agents <number>` - Minimum agents required (default: 1)
- `--strategy, -s <type>` - Selection strategy: optimal, minimal, balanced
- `--no-spawn` - Analyze only, don't spawn agents

## Examples

### Basic auto-spawning

```bash
```

### Constrained spawning

```bash
```

### Analysis only

```bash
```

### Minimal strategy

```bash
```

## How It Works

1. **Task Analysis**

   - Parses task description
   - Identifies required skills
   - Estimates complexity
   - Determines parallelization opportunities

2. **Agent Selection**

   - Matches skills to agent types
   - Considers task dependencies
   - Optimizes for efficiency
   - Respects constraints

3. **Topology Selection**

   - Chooses optimal swarm structure
   - Configures communication patterns
   - Sets up coordination rules
   - Enables monitoring

4. **Automatic Spawning**
   - Creates selected agents
   - Assigns specific roles
   - Distributes subtasks
   - Initiates coordination

## Agent Types Selected

- **Architect**: System design, architecture decisions
- **Coder**: Implementation, code generation
- **Tester**: Test creation, quality assurance
- **Analyst**: Performance, optimization
- **Researcher**: Documentation, best practices
- **Coordinator**: Task management, progress tracking

## Strategies

### Optimal

- Maximum efficiency
- May spawn more agents
- Best for complex tasks
- Highest resource usage

### Minimal

- Minimum viable agents
- Conservative approach
- Good for simple tasks
- Lowest resource usage

### Balanced

- Middle ground
- Adaptive to complexity
- Default strategy
- Good performance/resource ratio

## Integration with Claude Code

```javascript
// In Claude Code after auto-spawning
  task: "Build authentication system",
  strategy: "balanced",
  maxAgents: 6
}
```

## See Also

- `agent spawn` - Manual agent creation
- `swarm init` - Initialize swarm manually
- `smart spawn` - Intelligent agent spawning
- `workflow select` - Choose predefined workflows
