# Raft Consensus Manager Skill

> Version: 1.0.0
> Created: 2026-01-02
> Last Updated: 2026-01-02

## Overview

Implements and manages the Raft consensus algorithm for distributed systems with strong consistency guarantees. Provides leader election, log replication, and fault-tolerant operation for crash failures.

## Quick Start

```bash
# Invoke skill for Raft consensus management
/consensus-raft

# Or via Task tool
Task("Raft Manager", "Implement leader election and log replication", "raft-manager")
```

## When to Use

- **Leader Election**: Coordinating randomized timeout-based leader selection
- **Log Replication**: Ensuring reliable entry propagation to followers
- **Consistency Management**: Maintaining log consistency across cluster nodes
- **Membership Changes**: Handling dynamic node addition/removal safely
- **Recovery Coordination**: Resynchronizing nodes after network partitions

## Core Concepts

### Leader Election Protocol
- Randomized timeout-based elections prevent split votes
- Candidate state transitions and vote collection
- Leadership maintained through periodic heartbeats
- Intelligent backoff for split vote scenarios

### Log Replication System
- Append entries protocol for reliable log propagation
- Log consistency guarantees across all follower nodes
- Commit index tracking and state machine application
- Log compaction through snapshotting mechanisms

### Fault Tolerance Features
- Leader failure detection and new election triggering
- Network partition handling while maintaining consistency
- Automatic failed node recovery to consistent state
- Safe dynamic cluster membership changes

## Implementation Pattern

### Raft Node States

```javascript
const RaftState = {
  FOLLOWER: 'follower',
  CANDIDATE: 'candidate',
  LEADER: 'leader'
};

class RaftNode {
  constructor(nodeId, clusterNodes) {
    this.nodeId = nodeId;
    this.clusterNodes = clusterNodes;
    this.state = RaftState.FOLLOWER;

    // Persistent state
    this.currentTerm = 0;
    this.votedFor = null;
    this.log = [];

    // Volatile state
    this.commitIndex = 0;
    this.lastApplied = 0;

    // Leader state
    this.nextIndex = new Map();
    this.matchIndex = new Map();

    // Timing
    this.electionTimeout = this.randomElectionTimeout();
    this.heartbeatInterval = 150;
    this.lastHeartbeat = Date.now();
  }

  randomElectionTimeout() {
    return 150 + Math.floor(Math.random() * 150);
  }

  async startElection() {
    this.state = RaftState.CANDIDATE;
    this.currentTerm++;
    this.votedFor = this.nodeId;
    this.lastHeartbeat = Date.now();

    const lastLogIndex = this.log.length - 1;
    const lastLogTerm = lastLogIndex >= 0 ? this.log[lastLogIndex].term : 0;

    const voteRequest = {
      type: 'REQUEST_VOTE',
      term: this.currentTerm,
      candidateId: this.nodeId,
      lastLogIndex,
      lastLogTerm
    };

    let votesReceived = 1;
    const majority = Math.floor(this.clusterNodes.length / 2) + 1;

    const responses = await Promise.all(
      this.clusterNodes
        .filter(node => node !== this.nodeId)
        .map(node => this.sendRPC(node, voteRequest).catch(() => ({ voteGranted: false })))
    );

    for (const response of responses) {
      if (response.term > this.currentTerm) {
        this.currentTerm = response.term;
        this.state = RaftState.FOLLOWER;
        return false;
      }
      if (response.voteGranted) votesReceived++;
    }

    if (votesReceived >= majority && this.state === RaftState.CANDIDATE) {
      this.becomeLeader();
      return true;
    }

    return false;
  }

  becomeLeader() {
    this.state = RaftState.LEADER;
    for (const node of this.clusterNodes) {
      if (node !== this.nodeId) {
        this.nextIndex.set(node, this.log.length);
        this.matchIndex.set(node, 0);
      }
    }
    this.startHeartbeatLoop();
  }
}
```

### Log Replication

```javascript
class RaftLogReplicator {
  constructor(raftNode) {
    this.node = raftNode;
  }

  async appendEntry(command) {
    if (this.node.state !== RaftState.LEADER) {
      throw new Error('Not the leader');
    }

    const entry = {
      term: this.node.currentTerm,
      command,
      index: this.node.log.length
    };
    this.node.log.push(entry);

    await this.replicateToFollowers();
    return entry;
  }

  async replicateToNode(nodeId) {
    const nextIdx = this.node.nextIndex.get(nodeId);
    const prevLogIndex = nextIdx - 1;
    const prevLogTerm = prevLogIndex >= 0 ? this.node.log[prevLogIndex].term : 0;

    const appendRequest = {
      type: 'APPEND_ENTRIES',
      term: this.node.currentTerm,
      leaderId: this.node.nodeId,
      prevLogIndex,
      prevLogTerm,
      entries: this.node.log.slice(nextIdx),
      leaderCommit: this.node.commitIndex
    };

    const response = await this.node.sendRPC(nodeId, appendRequest);

    if (response.success) {
      this.node.nextIndex.set(nodeId, nextIdx + appendRequest.entries.length);
      this.node.matchIndex.set(nodeId, nextIdx + appendRequest.entries.length - 1);
    } else if (response.term > this.node.currentTerm) {
      this.node.currentTerm = response.term;
      this.node.state = RaftState.FOLLOWER;
    } else {
      this.node.nextIndex.set(nodeId, Math.max(0, nextIdx - 1));
      await this.replicateToNode(nodeId);
    }
  }
}
```

## Usage Examples

### Basic Raft Cluster

```javascript
const nodes = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5'];
const raftNode = new RaftNode('node-1', nodes);
const replicator = new RaftLogReplicator(raftNode);

setInterval(async () => {
  if (raftNode.state === RaftState.FOLLOWER && raftNode.shouldStartElection()) {
    await raftNode.startElection();
  }
}, 50);

if (raftNode.state === RaftState.LEADER) {
  const entry = await replicator.appendEntry({
    type: 'SET',
    key: 'config',
    value: { maxConnections: 100 }
  });
}
```

## MCP Integration

```javascript
await mcp__claude-flow__memory_usage({
  action: 'store',
  key: \`raft_state_\${nodeId}\`,
  value: JSON.stringify({
    currentTerm: raftNode.currentTerm,
    votedFor: raftNode.votedFor,
    log: raftNode.log,
    commitIndex: raftNode.commitIndex,
    state: raftNode.state
  }),
  namespace: 'consensus_raft',
  ttl: 0
});
```

## Collaboration

- **Quorum Manager**: Membership adjustments and fault tolerance
- **Performance Benchmarker**: Optimization analysis
- **CRDT Synchronizer**: Eventual consistency scenarios
- **Security Manager**: Secure communication channels

## Best Practices

1. **Election Timeout**: Use random timeouts (150-300ms) to prevent split votes
2. **Heartbeat Frequency**: Set heartbeat interval to 1/3 of election timeout
3. **Log Compaction**: Create snapshots periodically to limit log size
4. **Membership Changes**: Use joint consensus for safe configuration changes
5. **Persistence**: Always persist term, votedFor, and log before responding

## Hooks

```bash
# Pre-task hook
echo "Raft Manager starting: \$TASK"
if [[ "\$TASK" == *"election"* ]]; then
  echo "Preparing leader election process"
fi

# Post-task hook
echo "Raft operation complete"
echo "Validating log replication and consistency"
```

## Related Skills

- [consensus-quorum](../consensus-quorum/SKILL.md) - Quorum management
- [consensus-benchmark](../consensus-benchmark/SKILL.md) - Performance analysis
- [consensus-crdt](../consensus-crdt/SKILL.md) - Eventual consistency

---

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from raft-manager agent
