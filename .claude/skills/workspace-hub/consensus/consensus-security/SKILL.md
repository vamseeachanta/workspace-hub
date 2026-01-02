# Consensus Security Manager Skill

> Version: 1.0.0
> Created: 2026-01-02
> Last Updated: 2026-01-02

## Overview

Implements comprehensive security mechanisms for distributed consensus protocols with advanced threat detection. Provides cryptographic infrastructure, attack detection, key management, and real-time security countermeasures.

## Quick Start

```bash
# Invoke skill for consensus security
/consensus-security

# Or via Task tool
Task("Security Manager", "Implement cryptographic security for consensus", "security-manager")
```

## When to Use

- **Cryptographic Infrastructure**: Threshold signatures and zero-knowledge proofs
- **Attack Detection**: Byzantine, Sybil, Eclipse, and DoS attack identification
- **Key Management**: Distributed key generation and rotation
- **Secure Communications**: TLS 1.3 and message authentication
- **Threat Mitigation**: Real-time security countermeasures

## Core Concepts

### Attack Types

| Attack | Description | Defense |
|--------|-------------|---------|
| Byzantine | Malicious nodes send conflicting messages | PBFT, detection, reputation |
| Sybil | Attacker creates multiple fake identities | PoW, PoS, identity verification |
| Eclipse | Isolating a node from honest peers | Peer diversity, connection limits |
| DoS | Overwhelming system with requests | Rate limiting, circuit breakers |

### Cryptographic Primitives
- **Threshold Signatures**: t-of-n signing without single key holder
- **Zero-Knowledge Proofs**: Prove knowledge without revealing secret
- **Message Authentication**: Verify message integrity and origin
- **Key Derivation**: Secure key generation and rotation

## Implementation Pattern

### Threshold Signature System

```javascript
class ThresholdSignatureSystem {
  constructor(threshold, totalParties) {
    this.t = threshold;
    this.n = totalParties;
    this.masterPublicKey = null;
    this.privateKeyShares = new Map();
    this.publicKeyShares = new Map();
  }

  async generateDistributedKeys() {
    const secretPolynomial = this.generateSecretPolynomial();
    const commitments = this.generateCommitments(secretPolynomial);
    await this.broadcastCommitments(commitments);

    const secretShares = this.generateSecretShares(secretPolynomial);
    await this.distributeSecretShares(secretShares);

    const validShares = await this.verifyReceivedShares();
    this.masterPublicKey = this.combineMasterPublicKey(validShares);

    return {
      masterPublicKey: this.masterPublicKey,
      privateKeyShare: this.privateKeyShares.get(this.nodeId),
      publicKeyShares: this.publicKeyShares
    };
  }

  async createThresholdSignature(message, signatories) {
    if (signatories.length < this.t) {
      throw new Error('Insufficient signatories for threshold');
    }

    const partialSignatures = [];
    for (const signatory of signatories) {
      const partialSig = await this.createPartialSignature(message, signatory);
      partialSignatures.push({
        signatory,
        signature: partialSig,
        publicKeyShare: this.publicKeyShares.get(signatory)
      });
    }

    const validPartials = partialSignatures.filter(ps =>
      this.verifyPartialSignature(message, ps.signature, ps.publicKeyShare)
    );

    if (validPartials.length < this.t) {
      throw new Error('Insufficient valid partial signatures');
    }

    return this.combinePartialSignatures(message, validPartials.slice(0, this.t));
  }
}
```

### Attack Detection System

```javascript
class ConsensusSecurityMonitor {
  constructor() {
    this.reputationSystem = new ReputationSystem();
    this.alertSystem = new SecurityAlertSystem();
  }

  async detectByzantineAttacks(consensusRound) {
    const { participants, messages } = consensusRound;
    const anomalies = [];

    const contradictions = this.detectContradictoryMessages(messages);
    if (contradictions.length > 0) {
      anomalies.push({
        type: 'CONTRADICTORY_MESSAGES',
        severity: 'HIGH',
        details: contradictions
      });
    }

    const timingAnomalies = this.detectTimingAnomalies(messages);
    if (timingAnomalies.length > 0) {
      anomalies.push({
        type: 'TIMING_ATTACK',
        severity: 'MEDIUM',
        details: timingAnomalies
      });
    }

    const collusionPatterns = await this.detectCollusion(participants, messages);
    if (collusionPatterns.length > 0) {
      anomalies.push({
        type: 'COLLUSION_DETECTED',
        severity: 'HIGH',
        details: collusionPatterns
      });
    }

    for (const participant of participants) {
      await this.reputationSystem.updateReputation(
        participant,
        anomalies.filter(a => a.details.includes?.(participant))
      );
    }

    return anomalies;
  }

  detectContradictoryMessages(messages) {
    const messagesBySource = new Map();
    const contradictions = [];

    for (const msg of messages) {
      const key = \`\${msg.nodeId}_\${msg.view}_\${msg.sequence}_\${msg.type}\`;

      if (messagesBySource.has(key)) {
        const existing = messagesBySource.get(key);
        if (this.computeHash(existing) !== this.computeHash(msg)) {
          contradictions.push({
            nodeId: msg.nodeId,
            message1: existing,
            message2: msg,
            type: 'EQUIVOCATION'
          });
        }
      } else {
        messagesBySource.set(key, msg);
      }
    }

    return contradictions;
  }

  async preventSybilAttacks(nodeJoinRequest) {
    const verifiers = [
      this.verifyProofOfWork(nodeJoinRequest),
      this.verifyStakeProof(nodeJoinRequest),
      this.verifyIdentityCredentials(nodeJoinRequest),
      this.checkReputationHistory(nodeJoinRequest)
    ];

    const results = await Promise.all(verifiers);
    const passedVerifications = results.filter(r => r.valid);

    if (passedVerifications.length < 2) {
      throw new SecurityError('Insufficient identity verification');
    }

    return true;
  }

  async mitigateDoSAttacks(incomingRequests) {
    const anomalousRequests = await this.detectAnomalies(incomingRequests);

    if (anomalousRequests.length > 0) {
      await Promise.all([
        this.applyRateLimiting(anomalousRequests),
        this.implementPriorityQueuing(incomingRequests),
        this.activateCircuitBreakers(anomalousRequests),
        this.deployTemporaryBlacklisting(anomalousRequests)
      ]);
    }

    return this.filterLegitimateRequests(incomingRequests, anomalousRequests);
  }
}
```

### Secure Key Management

```javascript
class SecureKeyManager {
  constructor() {
    this.keyStore = new EncryptedKeyStore();
    this.rotationScheduler = new KeyRotationScheduler();
  }

  async rotateKeys(currentKeyId, participants) {
    const threshold = Math.floor(participants.length / 2) + 1;
    const newKey = await this.generateDistributedKey(participants, threshold);

    const transitionPeriod = 24 * 60 * 60 * 1000;
    await this.scheduleKeyTransition(currentKeyId, newKey.masterPublicKey, transitionPeriod);
    await this.notifyKeyRotation(participants, newKey);

    setTimeout(async () => {
      await this.deactivateKey(currentKeyId);
    }, transitionPeriod);

    return newKey;
  }

  async backupKeyShares(keyShares, backupThreshold) {
    const backupShares = this.createBackupShares(keyShares, backupThreshold);

    const encryptedBackups = await Promise.all(
      backupShares.map(async (share, index) => ({
        id: \`backup_\${index}\`,
        encryptedShare: await this.encryptBackupShare(share, \`password_\${index}\`),
        checksum: this.computeChecksum(share)
      }))
    );

    await this.distributeBackups(encryptedBackups);
    return encryptedBackups.map(b => ({ id: b.id, checksum: b.checksum }));
  }
}
```

## Usage Examples

### Threshold Signatures

```javascript
const tss = new ThresholdSignatureSystem(3, 5);
const keys = await tss.generateDistributedKeys();

const message = 'Consensus proposal #123';
const signatories = ['node-1', 'node-2', 'node-3'];

const signature = await tss.createThresholdSignature(message, signatories);
const valid = tss.verifyThresholdSignature(message, signature);
```

### Attack Detection

```javascript
const monitor = new ConsensusSecurityMonitor();

const anomalies = await monitor.detectByzantineAttacks({
  participants: ['node-1', 'node-2', 'node-3', 'node-4'],
  messages: consensusMessages
});

if (anomalies.length > 0) {
  for (const anomaly of anomalies) {
    if (anomaly.severity === 'HIGH') {
      await monitor.initiateEmergencyResponse(anomaly);
    }
  }
}
```

## MCP Integration

```javascript
await mcp__claude-flow__memory_usage({
  action: 'store',
  key: \`security_metrics_\${Date.now()}\`,
  value: JSON.stringify({
    attacksDetected: monitor.attacksDetected,
    reputationScores: Array.from(monitor.reputationSystem.scores.entries()),
    keyRotationEvents: keyManager.rotationHistory
  }),
  namespace: 'consensus_security',
  ttl: 86400000
});
```

## Collaboration

- **Byzantine Coordinator**: Byzantine consensus integration
- **Quorum Manager**: Secure membership changes
- **Performance Benchmarker**: Security operation optimization
- **CRDT Synchronizer**: Secure state synchronization

## Best Practices

1. **Key Security**: Never store private keys in plaintext
2. **Threshold Selection**: Use t > n/2 for safety
3. **Rotation Frequency**: Rotate keys regularly (monthly minimum)
4. **Logging**: Log all security events for forensics
5. **Defense in Depth**: Layer multiple security mechanisms

## Hooks

```bash
# Pre-task hook
echo "Security Manager securing: \$TASK"
if [[ "\$TASK" == *"consensus"* ]]; then
  echo "Activating cryptographic verification"
fi

# Post-task hook
echo "Security protocols verified"
echo "Conducting post-operation security audit"
```

## Related Skills

- [consensus-byzantine](../consensus-byzantine/SKILL.md) - Byzantine fault tolerance
- [consensus-quorum](../consensus-quorum/SKILL.md) - Quorum management
- [consensus-benchmark](../consensus-benchmark/SKILL.md) - Performance analysis

---

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from security-manager agent
