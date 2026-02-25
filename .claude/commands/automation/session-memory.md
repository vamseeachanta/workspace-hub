# Cross-Session Memory

## Purpose
Maintain context and learnings across Claude Code sessions for continuous improvement.

## Memory Features

### 1. Automatic State Persistence
At session end, automatically saves:
- Active agents and specializations
- Task history and patterns
- Performance metrics
- Neural network weights
- Knowledge base updates

### 2. Session Restoration
```javascript
// Using MCP tools for memory operations
  "action": "retrieve",
  "key": "session-state",
  "namespace": "sessions"
})

// Restore swarm state
  "snapshotId": "sess-123"
})
```

**Fallback with npx:**
```bash
```

### 3. Memory Types

**Project Memory:**
- File relationships
- Common edit patterns
- Testing approaches
- Build configurations

**Agent Memory:**
- Specialization levels
- Task success rates
- Optimization strategies
- Error patterns

**Performance Memory:**
- Bottleneck history
- Optimization results
- Token usage patterns
- Efficiency trends

### 4. Privacy & Control
```javascript
// List memory contents
  "action": "list",
  "namespace": "sessions"
})

// Delete specific memory
  "action": "delete",
  "key": "session-123",
  "namespace": "sessions"
})

// Backup memory
  "path": "./backups/memory-backup.json"
})
```

**Manual control:**
```bash
# View stored memory

# Disable memory
export CLAUDE_FLOW_MEMORY_PERSIST=false
```

## Benefits
- 🧠 Contextual awareness
- 📈 Cumulative learning
- ⚡ Faster task completion
- 🎯 Personalized optimization
