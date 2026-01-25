# Byzantine Consensus Coordinator Skill

> Version: 1.0.0
> Created: 2026-01-02
> Last Updated: 2026-01-02

## Overview

Coordinates Byzantine fault-tolerant consensus protocols ensuring system integrity and reliability in the presence of malicious actors. Implements PBFT three-phase protocol with cryptographic verification and attack mitigation.

## Quick Start

```bash
# Invoke skill for Byzantine consensus coordination
/consensus-byzantine

# Or via Task tool
Task("Byzantine Coordinator", "Implement PBFT consensus with malicious actor detection", "byzantine-coordinator")
```

## When to Use

- **PBFT Implementation**: When you need practical Byzantine fault tolerance
- **Malicious Actor Detection**: Systems requiring Byzantine behavior pattern identification
- **Secure Consensus**: Applications needing cryptographic message verification
- **View Change Coordination**: Handling leader failures and protocol transitions
- **Attack Mitigation**: Defending against known Byzantine attack vectors

## Core Concepts

### Byzantine Fault Tolerance
- Tolerates up to f < n/3 malicious nodes
- Three-phase commit: Pre-prepare, Prepare, Commit
- Threshold signature schemes for message validation
- View changes for primary node failure recovery

### Security Integration
- Cryptographic signatures for message authenticity
- Zero-knowledge proofs for vote verification
- Replay attack prevention with sequence numbers
- DoS protection through rate limiting

### Network Resilience
- Automatic network partition detection
- Conflicting state reconciliation after partition healing
- Dynamic quorum size adjustment based on connectivity
- Systematic recovery protocols

## Implementation Pattern

### PBFT Three-Phase Protocol

```javascript
class ByzantineConsensusCoordinator {
  constructor(nodeId, clusterNodes, threshold) {
    this.nodeId = nodeId;
    this.clusterNodes = clusterNodes;
    this.f = Math.floor((clusterNodes.length - 1) / 3); // Max Byzantine nodes
    this.threshold = threshold || (2 * this.f + 1);
    this.viewNumber = 0;
    this.sequenceNumber = 0;
    this.messageLog = new Map();
    this.prepareVotes = new Map();
    this.commitVotes = new Map();
  }

  // Phase 1: Pre-prepare (Leader broadcasts proposal)
  async initiateConsensus(proposal) {
    if (!this.isLeader()) {
      throw new Error('Only leader can initiate consensus');
    }

    const prePrepareMessage = {
      type: 'PRE_PREPARE',
      view: this.viewNumber,
      sequence: ++this.sequenceNumber,
      digest: this.computeDigest(proposal),
      proposal: proposal,
      leader: this.nodeId,
      signature: await this.sign(proposal)
    };

    await this.broadcast(prePrepareMessage);
    return this.waitForConsensus(prePrepareMessage.sequence);
  }

  // Phase 2: Prepare (Nodes validate and vote)
  async handlePrePrepare(message) {
    if (!await this.validatePrePrepare(message)) {
      return this.reportMaliciousBehavior(message.leader, 'INVALID_PRE_PREPARE');
    }

    this.messageLog.set(message.sequence, message);

    const prepareMessage = {
      type: 'PREPARE',
      view: message.view,
      sequence: message.sequence,
      digest: message.digest,
      nodeId: this.nodeId,
      signature: await this.sign(message.digest)
    };

    await this.broadcast(prepareMessage);
    return this.checkPrepareQuorum(message.sequence);
  }

  // Phase 3: Commit (Nodes commit after prepare quorum)
  async handlePrepare(message) {
    if (!await this.validatePrepare(message)) {
      return;
    }

    if (!this.prepareVotes.has(message.sequence)) {
      this.prepareVotes.set(message.sequence, new Set());
    }
    this.prepareVotes.get(message.sequence).add(message.nodeId);

    if (this.prepareVotes.get(message.sequence).size >= this.threshold) {
      await this.enterCommitPhase(message.sequence);
    }
  }

  async enterCommitPhase(sequence) {
    const commitMessage = {
      type: 'COMMIT',
      view: this.viewNumber,
      sequence: sequence,
      nodeId: this.nodeId,
      signature: await this.sign(\`commit_\${sequence}\`)
    };

    await this.broadcast(commitMessage);
  }

  // View change for leader failure
  async initiateViewChange(reason) {
    const viewChangeMessage = {
      type: 'VIEW_CHANGE',
      newView: this.viewNumber + 1,
      nodeId: this.nodeId,
      reason: reason,
      preparedProofs: this.getPrepairedProofs(),
      signature: await this.sign(\`view_change_\${this.viewNumber + 1}\`)
    };

    await this.broadcast(viewChangeMessage);
  }
}
```

### Malicious Actor Detection

```javascript
class ByzantineDetector {
  constructor() {
    this.behaviorHistory = new Map();
    this.reputationScores = new Map();
    this.detectionThresholds = {
      equivocation: 1,
      latency: 5,
      omission: 10
    };
  }

  detectEquivocation(messages) {
    const messagesBySource = new Map();
    const equivocations = [];

    for (const msg of messages) {
      const key = \`\${msg.nodeId}_\${msg.view}_\${msg.sequence}_\${msg.type}\`;

      if (messagesBySource.has(key)) {
        const existing = messagesBySource.get(key);
        if (this.computeHash(existing) !== this.computeHash(msg)) {
          equivocations.push({
            type: 'EQUIVOCATION',
            nodeId: msg.nodeId,
            severity: 'CRITICAL',
            evidence: { message1: existing, message2: msg }
          });
        }
      } else {
        messagesBySource.set(key, msg);
      }
    }

    return equivocations;
  }
}
```

## Usage Examples

### Basic PBFT Consensus

```javascript
const coordinator = new ByzantineConsensusCoordinator(
  'node-1',
  ['node-1', 'node-2', 'node-3', 'node-4'],
  3  // 2f + 1 threshold for f=1
);

const result = await coordinator.initiateConsensus({
  type: 'TRANSACTION',
  data: { from: 'A', to: 'B', amount: 100 },
  timestamp: Date.now()
});
```

### With Attack Detection

```javascript
const detector = new ByzantineDetector();

coordinator.onRoundComplete(async (round) => {
  const anomalies = await detector.detectByzantineBehavior(round);

  if (anomalies.length > 0) {
    for (const anomaly of anomalies) {
      if (anomaly.severity === 'CRITICAL') {
        await coordinator.isolateNode(anomaly.nodeId);
      }
    }
  }
});
```

## MCP Integration

### Memory Coordination

```javascript
await mcp__claude-flow__memory_usage({
  action: 'store',
  key: \`byzantine_state_\${nodeId}\`,
  value: JSON.stringify({
    viewNumber: coordinator.viewNumber,
    sequenceNumber: coordinator.sequenceNumber,
    preparedMessages: Array.from(coordinator.messageLog.entries())
  }),
  namespace: 'consensus_byzantine',
  ttl: 3600000
});
```

## Collaboration

- **Security Manager**: Cryptographic validation and key management
- **Quorum Manager**: Fault tolerance adjustments
- **Performance Benchmarker**: Optimization metrics
- **CRDT Synchronizer**: State consistency after partitions

## Best Practices

1. **Threshold Configuration**: Always use 2f + 1 for safety (f = max Byzantine nodes)
2. **Message Authentication**: Sign all consensus messages with node's private key
3. **Timeout Tuning**: Set view change timeouts based on network latency
4. **Reputation Tracking**: Maintain long-term behavior history for each node
5. **View Change Safety**: Ensure view change messages include prepared proofs

## Hooks

```bash
# Pre-task hook
echo "Byzantine Coordinator initiating: \$TASK"
if [[ "\$TASK" == *"consensus"* ]]; then
  echo "Checking for malicious actors..."
fi

# Post-task hook
echo "Byzantine consensus complete"
echo "Verifying message signatures and ordering"
```

## Related Skills

- [consensus-security](../consensus-security/SKILL.md) - Cryptographic security
- [consensus-quorum](../consensus-quorum/SKILL.md) - Quorum management
- [consensus-benchmark](../consensus-benchmark/SKILL.md) - Performance analysis

---

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from byzantine-coordinator agent
