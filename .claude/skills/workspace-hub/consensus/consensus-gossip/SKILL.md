# Gossip Protocol Coordinator Skill

> Version: 1.0.0
> Created: 2026-01-02
> Last Updated: 2026-01-02

## Overview

Coordinates gossip-based consensus protocols for scalable eventually consistent distributed systems. Implements epidemic dissemination, anti-entropy protocols, and membership management for high-availability systems.

## Quick Start

```bash
# Invoke skill for gossip protocol coordination
/consensus-gossip

# Or via Task tool
Task("Gossip Coordinator", "Implement epidemic dissemination with peer selection", "gossip-coordinator")
```

## When to Use

- **Epidemic Dissemination**: Push/pull gossip protocols for information spread
- **Peer Management**: Random peer selection and failure detection
- **State Synchronization**: Vector clocks and conflict resolution
- **Convergence Monitoring**: Ensuring eventual consistency across nodes
- **Scalability Optimization**: Large-scale distributed systems needing efficient updates

## Core Concepts

### Epidemic Information Spread
- Push gossip: Proactive information spreading
- Pull gossip: Reactive information retrieval
- Push-pull hybrid: Optimal convergence approach
- Rumor spreading: Fast critical update propagation

### Anti-Entropy Protocols
- State synchronization for eventual consistency
- Merkle tree comparison for efficient difference detection
- Vector clocks for causal relationship tracking
- Conflict resolution for concurrent updates

### Membership and Topology
- Join protocol for seamless new node integration
- Failure detection for unresponsive nodes
- Graceful departure handling
- Network topology discovery and optimization

## Implementation Pattern

### Core Gossip Protocol

```javascript
class GossipCoordinator {
  constructor(nodeId, config = {}) {
    this.nodeId = nodeId;
    this.peers = new Set();
    this.state = new Map();
    this.vectorClock = new Map();
    this.rumorBuffer = [];
    this.membershipList = new Map();

    this.fanout = config.fanout || 3;
    this.gossipInterval = config.interval || 1000;
    this.maxRounds = config.maxRounds || 10;

    this.vectorClock.set(this.nodeId, 0);
  }

  start() {
    this.gossipTimer = setInterval(() => {
      this.gossipRound();
    }, this.gossipInterval);
  }

  async gossipRound() {
    const selectedPeers = this.selectRandomPeers(this.fanout);
    if (selectedPeers.length === 0) return;

    const gossipMessage = this.prepareGossipMessage();
    const promises = selectedPeers.map(peer =>
      this.sendGossip(peer, gossipMessage)
    );

    const responses = await Promise.allSettled(promises);

    for (let i = 0; i < responses.length; i++) {
      if (responses[i].status === 'fulfilled') {
        await this.processGossipResponse(selectedPeers[i], responses[i].value);
      } else {
        this.handlePeerFailure(selectedPeers[i]);
      }
    }

    this.ageRumors();
  }

  selectRandomPeers(count) {
    const availablePeers = Array.from(this.peers)
      .filter(peer => this.membershipList.get(peer)?.status === 'alive');

    const shuffled = [...availablePeers];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }

    return shuffled.slice(0, Math.min(count, shuffled.length));
  }

  spreadRumor(update) {
    const rumor = {
      id: \`\${Date.now()}-\${Math.random()}\`,
      origin: this.nodeId,
      update,
      rounds: 0,
      timestamp: Date.now()
    };

    this.rumorBuffer.push(rumor);
  }
}
```

### Anti-Entropy with Merkle Trees

```javascript
class AntiEntropyProtocol {
  constructor(gossipCoordinator) {
    this.coordinator = gossipCoordinator;
    this.merkleTree = new MerkleTree();
  }

  async syncWithPeer(peerId) {
    const localRoot = this.buildMerkleTree();
    const peerRoot = await this.coordinator.requestRootHash(peerId);

    if (localRoot === peerRoot) {
      return { synced: true, differences: 0 };
    }

    const differences = await this.findDifferences(peerId, this.merkleTree.root);

    for (const diff of differences) {
      await this.resolveConflict(peerId, diff);
    }

    return { synced: true, differences: differences.length };
  }

  compareVectorClocks(vc1, vc2) {
    let vc1Greater = false;
    let vc2Greater = false;

    const allKeys = new Set([...Object.keys(vc1), ...Object.keys(vc2)]);

    for (const key of allKeys) {
      const val1 = vc1[key] || 0;
      const val2 = vc2[key] || 0;

      if (val1 > val2) vc1Greater = true;
      if (val2 > val1) vc2Greater = true;
    }

    if (vc1Greater && !vc2Greater) return 'AFTER';
    if (vc2Greater && !vc1Greater) return 'BEFORE';
    if (!vc1Greater && !vc2Greater) return 'EQUAL';
    return 'CONCURRENT';
  }
}
```

### SWIM Membership Protocol

```javascript
class SwimMembershipProtocol {
  constructor(gossipCoordinator) {
    this.coordinator = gossipCoordinator;
    this.suspicionTimeout = 5000;
    this.pingTimeout = 1000;
  }

  async probeRound() {
    const target = this.selectProbeTarget();
    if (!target) return;

    const result = await this.probe(target);

    if (!result.alive) {
      const indirectResult = await this.indirectProbe(target);
      if (!indirectResult.alive) {
        this.markSuspect(target);
      }
    }
  }

  markSuspect(nodeId) {
    const member = this.coordinator.membershipList.get(nodeId);

    if (member && member.status === 'alive') {
      member.status = 'suspect';
      member.suspectTime = Date.now();

      this.coordinator.spreadRumor({
        type: 'SUSPECT',
        target: nodeId,
        reporter: this.coordinator.nodeId,
        timestamp: Date.now()
      });

      setTimeout(() => this.confirmDeath(nodeId), this.suspicionTimeout);
    }
  }
}
```

## Usage Examples

### Basic Gossip Cluster

```javascript
const gossip = new GossipCoordinator('node-1', {
  fanout: 3,
  interval: 1000,
  maxRounds: 10
});

gossip.peers.add('node-2');
gossip.peers.add('node-3');
gossip.peers.add('node-4');

gossip.start();

gossip.spreadRumor({
  type: 'CONFIG_UPDATE',
  key: 'max_connections',
  value: 100
});
```

## MCP Integration

```javascript
await mcp__claude-flow__memory_usage({
  action: 'store',
  key: \`gossip_state_\${nodeId}\`,
  value: JSON.stringify({
    vectorClock: Object.fromEntries(gossip.vectorClock),
    membershipList: Array.from(gossip.membershipList.entries()),
    stateDigest: gossip.getStateDigest()
  }),
  namespace: 'consensus_gossip',
  ttl: 3600000
});
```

## Collaboration

- **Performance Benchmarker**: Gossip optimization analysis
- **CRDT Synchronizer**: Conflict-free data types integration
- **Quorum Manager**: Membership coordination
- **Security Manager**: Secure peer communication

## Best Practices

1. **Fanout Selection**: Use fanout of 2-3 for good balance of speed and bandwidth
2. **Rumor Lifetime**: Limit rounds to prevent infinite propagation
3. **Failure Detection**: Use indirect probes before marking nodes dead
4. **Anti-Entropy**: Run periodic full syncs to ensure consistency
5. **Incarnation Numbers**: Use to distinguish between restarts and failures

## Hooks

```bash
# Pre-task hook
echo "Gossip Coordinator broadcasting: \$TASK"
if [[ "\$TASK" == *"dissemination"* ]]; then
  echo "Establishing peer network topology"
fi

# Post-task hook
echo "Gossip protocol cycle complete"
echo "Monitoring eventual consistency convergence"
```

## Related Skills

- [consensus-crdt](../consensus-crdt/SKILL.md) - Conflict-free data types
- [consensus-quorum](../consensus-quorum/SKILL.md) - Membership management
- [consensus-benchmark](../consensus-benchmark/SKILL.md) - Performance analysis

---

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from gossip-coordinator agent
