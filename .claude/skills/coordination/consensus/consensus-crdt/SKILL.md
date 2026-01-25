# CRDT Synchronizer Skill

> Version: 1.0.0
> Created: 2026-01-02
> Last Updated: 2026-01-02

## Overview

Implements Conflict-free Replicated Data Types (CRDTs) for eventually consistent distributed state synchronization. Provides automatic conflict resolution through mathematically guaranteed merge operations.

## Quick Start

```bash
# Invoke skill for CRDT synchronization
/consensus-crdt

# Or via Task tool
Task("CRDT Synchronizer", "Implement conflict-free state synchronization", "crdt-synchronizer")
```

## When to Use

- **Distributed State**: Applications needing replicated state across nodes
- **Offline-First**: Apps that work offline and sync later
- **Collaborative Editing**: Real-time collaborative applications
- **Conflict Resolution**: When automatic, deterministic conflict resolution is required
- **Eventual Consistency**: Systems where strong consistency isn't required

## Core Concepts

### CRDT Types

| Type | Description | Use Case |
|------|-------------|----------|
| G-Counter | Grow-only counter | Page views, likes |
| PN-Counter | Positive-negative counter | Inventory, balance |
| G-Set | Grow-only set | Tags, followers |
| OR-Set | Observed-remove set | Shopping cart |
| LWW-Register | Last-writer-wins register | User profile |
| RGA | Replicated growable array | Collaborative text |

### Key Properties
- **Commutativity**: Order of operations doesn't matter
- **Associativity**: Grouping of operations doesn't matter
- **Idempotency**: Applying same operation twice has same effect as once

## Implementation Pattern

### G-Counter (Grow-Only Counter)

```javascript
class GCounter {
  constructor(nodeId, replicationGroup) {
    this.nodeId = nodeId;
    this.replicationGroup = replicationGroup;
    this.payload = new Map();

    for (const node of replicationGroup) {
      this.payload.set(node, 0);
    }
  }

  increment(amount = 1) {
    if (amount < 0) throw new Error('G-Counter only supports positive increments');
    const oldValue = this.payload.get(this.nodeId) || 0;
    this.payload.set(this.nodeId, oldValue + amount);
    return oldValue + amount;
  }

  value() {
    return Array.from(this.payload.values()).reduce((sum, val) => sum + val, 0);
  }

  merge(otherState) {
    for (const [node, otherValue] of otherState.payload) {
      const currentValue = this.payload.get(node) || 0;
      if (otherValue > currentValue) {
        this.payload.set(node, otherValue);
      }
    }
  }
}
```

### OR-Set (Observed-Remove Set)

```javascript
class ORSet {
  constructor(nodeId) {
    this.nodeId = nodeId;
    this.elements = new Map();
    this.tombstones = new Set();
    this.tagCounter = 0;
  }

  add(element) {
    const tag = \`\${this.nodeId}-\${Date.now()}-\${++this.tagCounter}\`;
    if (!this.elements.has(element)) {
      this.elements.set(element, new Set());
    }
    this.elements.get(element).add(tag);
    return tag;
  }

  remove(element) {
    if (!this.elements.has(element)) return false;
    const tags = this.elements.get(element);
    for (const tag of tags) {
      this.tombstones.add(tag);
    }
    return true;
  }

  has(element) {
    if (!this.elements.has(element)) return false;
    for (const tag of this.elements.get(element)) {
      if (!this.tombstones.has(tag)) return true;
    }
    return false;
  }

  values() {
    const result = new Set();
    for (const [element, tags] of this.elements) {
      for (const tag of tags) {
        if (!this.tombstones.has(tag)) {
          result.add(element);
          break;
        }
      }
    }
    return result;
  }

  merge(otherState) {
    for (const [element, otherTags] of otherState.elements) {
      if (!this.elements.has(element)) {
        this.elements.set(element, new Set());
      }
      for (const tag of otherTags) {
        this.elements.get(element).add(tag);
      }
    }
    for (const tombstone of otherState.tombstones) {
      this.tombstones.add(tombstone);
    }
  }
}
```

### LWW-Register (Last-Writer-Wins Register)

```javascript
class LWWRegister {
  constructor(nodeId, initialValue = null) {
    this.nodeId = nodeId;
    this.value = initialValue;
    this.timestamp = initialValue ? Date.now() : 0;
  }

  set(newValue, timestamp = null) {
    const ts = timestamp || Date.now();
    if (ts > this.timestamp || (ts === this.timestamp && this.nodeId > this.getLastWriter())) {
      this.value = newValue;
      this.timestamp = ts;
    }
  }

  get() {
    return this.value;
  }

  merge(otherRegister) {
    if (otherRegister.timestamp > this.timestamp ||
        (otherRegister.timestamp === this.timestamp && otherRegister.nodeId > this.nodeId)) {
      this.value = otherRegister.value;
      this.timestamp = otherRegister.timestamp;
    }
  }
}
```

### RGA (Replicated Growable Array)

```javascript
class RGA {
  constructor(nodeId) {
    this.nodeId = nodeId;
    this.sequence = [];
    this.tombstones = new Set();
    this.vertexCounter = 0;
  }

  insert(position, element) {
    const vertex = {
      id: \`\${this.nodeId}-\${++this.vertexCounter}\`,
      element,
      timestamp: Date.now(),
      nodeId: this.nodeId
    };

    let insertionIndex = 0;
    let visibleCount = 0;
    for (let i = 0; i < this.sequence.length; i++) {
      if (!this.tombstones.has(this.sequence[i].id)) {
        if (visibleCount === position) {
          insertionIndex = i;
          break;
        }
        visibleCount++;
      }
      insertionIndex = i + 1;
    }

    this.sequence.splice(insertionIndex, 0, vertex);
    return vertex.id;
  }

  remove(position) {
    let visibleCount = 0;
    for (const vertex of this.sequence) {
      if (!this.tombstones.has(vertex.id)) {
        if (visibleCount === position) {
          this.tombstones.add(vertex.id);
          return true;
        }
        visibleCount++;
      }
    }
    return false;
  }

  toArray() {
    return this.sequence
      .filter(v => !this.tombstones.has(v.id))
      .map(v => v.element);
  }

  toString() {
    return this.toArray().join('');
  }
}
```

## Usage Examples

### Shopping Cart with OR-Set

```javascript
const cart = new ORSet('user-device-1');

cart.add({ id: 'prod-1', name: 'Widget', qty: 2 });
cart.add({ id: 'prod-2', name: 'Gadget', qty: 1 });
cart.remove({ id: 'prod-1', name: 'Widget', qty: 2 });

const serverCart = await fetchServerCart();
cart.merge(serverCart);

console.log('Cart items:', cart.values());
```

### Distributed Counter

```javascript
const nodes = ['node-1', 'node-2', 'node-3'];

const counter1 = new GCounter('node-1', nodes);
const counter2 = new GCounter('node-2', nodes);
const counter3 = new GCounter('node-3', nodes);

counter1.increment(5);
counter2.increment(3);
counter3.increment(7);

counter1.merge(counter2);
counter1.merge(counter3);

console.log('Total count:', counter1.value()); // 15
```

## MCP Integration

```javascript
await mcp__claude-flow__memory_usage({
  action: 'store',
  key: \`crdt_state_\${crdtName}\`,
  value: JSON.stringify({
    type: crdt.constructor.name,
    state: crdt.serialize(),
    vectorClock: Array.from(synchronizer.vectorClock.entries())
  }),
  namespace: 'crdt_synchronization',
  ttl: 0
});
```

## Collaboration

- **Gossip Coordinator**: Epidemic dissemination of CRDT updates
- **Quorum Manager**: Membership coordination
- **Byzantine Coordinator**: Consensus integration
- **Performance Benchmarker**: Sync optimization

## Best Practices

1. **Choose Right CRDT**: Match data type to access patterns
2. **Delta Sync**: Use delta-state CRDTs for bandwidth efficiency
3. **Garbage Collection**: Periodically clean tombstones
4. **Vector Clocks**: Use for causal ordering when needed
5. **Compression**: Compress state for large CRDTs

## Hooks

```bash
# Pre-task hook
echo "CRDT Synchronizer syncing: \$TASK"
if [[ "\$TASK" == *"synchronization"* ]]; then
  echo "Preparing delta state computation"
fi

# Post-task hook
echo "CRDT synchronization complete"
echo "Validating conflict-free state convergence"
```

## Related Skills

- [consensus-gossip](../consensus-gossip/SKILL.md) - Epidemic dissemination
- [consensus-quorum](../consensus-quorum/SKILL.md) - Membership management
- [consensus-raft](../consensus-raft/SKILL.md) - Strong consistency option

---

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from crdt-synchronizer agent
