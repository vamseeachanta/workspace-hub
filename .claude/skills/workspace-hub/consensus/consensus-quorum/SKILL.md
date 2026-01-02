# Quorum Manager Skill

> Version: 1.0.0
> Created: 2026-01-02
> Last Updated: 2026-01-02

## Overview

Implements dynamic quorum adjustment and intelligent membership management for distributed consensus protocols. Optimizes quorum configuration based on network conditions, performance requirements, and fault tolerance needs.

## Quick Start

```bash
# Invoke skill for quorum management
/consensus-quorum

# Or via Task tool
Task("Quorum Manager", "Calculate optimal quorum configuration", "quorum-manager")
```

## When to Use

- **Dynamic Quorum Calculation**: Adapting quorum requirements to network conditions
- **Membership Management**: Handling node addition, removal, and failures
- **Network Monitoring**: Assessing connectivity, latency, and partitions
- **Weighted Voting**: Implementing capability-based voting weights
- **Fault Tolerance Optimization**: Balancing availability and consistency

## Core Concepts

### Quorum Types

| Type | Formula | Use Case |
|------|---------|----------|
| Simple Majority | n/2 + 1 | Crash fault tolerance |
| Byzantine | 2n/3 + 1 | Byzantine fault tolerance |
| Read Quorum | r | Read consistency |
| Write Quorum | w | Write consistency |
| Intersection | r + w > n | Strong consistency |

### Adjustment Strategies
- **Network-Based**: Optimize based on topology and latency
- **Performance-Based**: Optimize for throughput or latency
- **Fault-Tolerance-Based**: Maximize resilience
- **Hybrid**: Balance multiple objectives

## Implementation Pattern

### Core Quorum Manager

```javascript
class QuorumManager {
  constructor(nodeId, consensusProtocol) {
    this.nodeId = nodeId;
    this.protocol = consensusProtocol;
    this.currentQuorum = new Map();
    this.quorumHistory = [];
    this.adjustmentStrategies = new Map();

    this.initializeStrategies();
  }

  initializeStrategies() {
    this.adjustmentStrategies.set('NETWORK_BASED', new NetworkBasedStrategy());
    this.adjustmentStrategies.set('PERFORMANCE_BASED', new PerformanceBasedStrategy());
    this.adjustmentStrategies.set('FAULT_TOLERANCE_BASED', new FaultToleranceStrategy());
    this.adjustmentStrategies.set('HYBRID', new HybridStrategy());
  }

  async calculateOptimalQuorum(context = {}) {
    const analysisInput = {
      networkConditions: await this.getNetworkConditions(),
      membershipStatus: await this.getMembershipStatus(),
      performanceMetrics: context.performanceMetrics,
      currentQuorum: this.currentQuorum,
      protocol: this.protocol,
      faultToleranceRequirements: context.faultToleranceRequirements
    };

    const strategyResults = new Map();

    for (const [strategyName, strategy] of this.adjustmentStrategies) {
      try {
        const result = await strategy.calculateQuorum(analysisInput);
        strategyResults.set(strategyName, result);
      } catch (error) {
        console.warn(\`Strategy \${strategyName} failed:\`, error);
      }
    }

    const optimalResult = this.selectOptimalStrategy(strategyResults, analysisInput);

    return {
      recommendedQuorum: optimalResult.quorum,
      strategy: optimalResult.strategy,
      confidence: optimalResult.confidence,
      reasoning: optimalResult.reasoning,
      expectedImpact: optimalResult.expectedImpact
    };
  }

  async adjustQuorum(newQuorumConfig, options = {}) {
    const adjustmentId = \`adjustment_\${Date.now()}\`;

    try {
      await this.validateQuorumConfiguration(newQuorumConfig);
      const adjustmentPlan = await this.createAdjustmentPlan(this.currentQuorum, newQuorumConfig);
      const result = await this.executeQuorumAdjustment(adjustmentPlan, adjustmentId, options);
      await this.verifyQuorumAdjustment(result);

      this.currentQuorum = newQuorumConfig.quorum;
      this.recordQuorumChange(adjustmentId, result);

      return { success: true, adjustmentId, newQuorum: this.currentQuorum, impact: result.impact };
    } catch (error) {
      await this.rollbackQuorumAdjustment(adjustmentId);
      throw error;
    }
  }

  async validateQuorumConfiguration(config) {
    const totalNodes = config.quorum.size;
    const quorumSize = config.quorumSize || Math.floor(totalNodes / 2) + 1;

    if (quorumSize < 1) throw new Error('Quorum size must be at least 1');
    if (quorumSize > totalNodes) throw new Error('Quorum size cannot exceed total nodes');

    if (this.protocol === 'byzantine') {
      const minQuorum = Math.floor(2 * totalNodes / 3) + 1;
      if (quorumSize < minQuorum) {
        throw new Error(\`Byzantine protocol requires quorum of at least \${minQuorum}\`);
      }
    }

    return true;
  }
}
```

### Network-Based Strategy

```javascript
class NetworkBasedStrategy {
  async calculateQuorum(analysisInput) {
    const { networkConditions, membershipStatus } = analysisInput;

    const topologyAnalysis = await this.analyzeNetworkTopology(membershipStatus.activeNodes);
    const partitionRisk = await this.assessPartitionRisk(networkConditions, topologyAnalysis);

    const minQuorum = this.calculateMinimumQuorum(
      membershipStatus.activeNodes.length,
      partitionRisk.maxPartitionSize
    );

    const optimizedQuorum = await this.optimizeForNetworkConditions(
      minQuorum, networkConditions, topologyAnalysis
    );

    return {
      quorum: optimizedQuorum,
      strategy: 'NETWORK_BASED',
      confidence: this.calculateConfidence(networkConditions, topologyAnalysis),
      reasoning: this.generateReasoning(optimizedQuorum, partitionRisk),
      expectedImpact: {
        availability: this.estimateAvailability(optimizedQuorum),
        performance: this.estimatePerformance(optimizedQuorum, networkConditions)
      }
    };
  }

  calculateMinimumQuorum(totalNodes, maxPartitionSize) {
    const byzantineMinimum = Math.floor(2 * totalNodes / 3) + 1;
    const partitionMinimum = Math.floor((totalNodes - maxPartitionSize) / 2) + 1;
    return Math.max(byzantineMinimum, partitionMinimum);
  }
}
```

### Membership Management

```javascript
class MembershipManager {
  constructor(quorumManager) {
    this.quorum = quorumManager;
  }

  async addNode(nodeId, nodeInfo) {
    const validation = await this.validateNodeAddition(nodeId, nodeInfo);
    if (!validation.valid) throw new Error(validation.reason);

    const newConfig = await this.quorum.calculateOptimalQuorum({
      membershipStatus: {
        activeNodes: [...this.quorum.currentQuorum.keys(), nodeId]
      }
    });

    await this.applyMembershipChange({
      type: 'ADD',
      nodeId,
      nodeInfo,
      newQuorumConfig: newConfig.recommendedQuorum
    });

    return { success: true, newQuorum: newConfig };
  }

  async removeNode(nodeId, options = {}) {
    if (options.graceful !== false) {
      await this.drainNode(nodeId);
    }

    const remainingNodes = Array.from(this.quorum.currentQuorum.keys())
      .filter(id => id !== nodeId);

    const newConfig = await this.quorum.calculateOptimalQuorum({
      membershipStatus: { activeNodes: remainingNodes }
    });

    await this.applyMembershipChange({
      type: 'REMOVE',
      nodeId,
      graceful: options.graceful !== false,
      newQuorumConfig: newConfig.recommendedQuorum
    });

    return { success: true, newQuorum: newConfig };
  }
}
```

## Usage Examples

### Basic Quorum Management

```javascript
const quorumManager = new QuorumManager('node-1', 'raft');

const optimal = await quorumManager.calculateOptimalQuorum({
  faultToleranceRequirements: {
    minLikelihoodToConsider: 0.01,
    byzantineFaultTolerance: false
  }
});

console.log('Recommended quorum:', optimal.recommendedQuorum);
console.log('Strategy:', optimal.strategy);
console.log('Confidence:', optimal.confidence);

await quorumManager.adjustQuorum({
  quorum: optimal.recommendedQuorum,
  quorumSize: optimal.recommendedQuorum.nodes.size
});
```

### Weighted Voting

```javascript
const weightedQuorum = new Map([
  ['node-1', { weight: 2.0, role: 'primary' }],
  ['node-2', { weight: 1.0, role: 'secondary' }],
  ['node-3', { weight: 1.5, role: 'secondary' }]
]);

await quorumManager.adjustQuorum({
  quorum: weightedQuorum,
  weightedVoting: true,
  requiredWeight: 2.5
});
```

## MCP Integration

```javascript
await mcp__claude-flow__memory_usage({
  action: 'store',
  key: \`quorum_config_\${nodeId}\`,
  value: JSON.stringify({
    currentQuorum: Array.from(quorumManager.currentQuorum.entries()),
    strategy: quorumManager.activeStrategy,
    adjustmentHistory: quorumManager.quorumHistory.slice(-10)
  }),
  namespace: 'quorum_management',
  ttl: 3600000
});
```

## Collaboration

- **Byzantine Coordinator**: Fault tolerance adjustments
- **Raft Manager**: Membership changes
- **Performance Benchmarker**: Optimization analysis
- **Security Manager**: Secure membership updates

## Best Practices

1. **Gradual Changes**: Use joint consensus for membership changes
2. **Validation**: Always validate quorum meets safety requirements
3. **Monitoring**: Track quorum health continuously
4. **Diversity**: Select nodes across failure domains
5. **Rollback Plan**: Always have rollback capability for adjustments

## Hooks

```bash
# Pre-task hook
echo "Quorum Manager adjusting: \$TASK"
if [[ "\$TASK" == *"quorum"* ]]; then
  echo "Analyzing network topology and node health"
fi

# Post-task hook
echo "Quorum adjustment complete"
echo "Verifying fault tolerance and availability guarantees"
```

## Related Skills

- [consensus-byzantine](../consensus-byzantine/SKILL.md) - Byzantine fault tolerance
- [consensus-raft](../consensus-raft/SKILL.md) - Raft consensus
- [consensus-benchmark](../consensus-benchmark/SKILL.md) - Performance analysis

---

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from quorum-manager agent
