---
name: agent-orchestration-agent-selection
description: 'Sub-skill of agent-orchestration: Agent Selection (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Agent Selection (+2)

## Agent Selection


1. **Match agent to task**: Use specialized agents
2. **Limit concurrency**: Don't spawn too many agents
3. **Clear instructions**: Provide detailed prompts
4. **Monitor progress**: Check status regularly


## Swarm Management


1. **Choose appropriate topology**: Based on task structure
2. **Set reasonable timeouts**: Prevent hung agents
3. **Use memory for context**: Share information between agents
4. **Clean up**: Destroy swarms when done


## Error Handling


1. **Plan for failures**: Use fault tolerance
2. **Create snapshots**: Before risky operations
3. **Log extensively**: For debugging
4. **Graceful degradation**: Handle partial failures
