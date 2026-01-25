# Swarm Mesh Coordinator Skill

> Version: 1.0.0
> Created: 2026-01-02
> Category: Swarm Coordination
> Priority: High

## Overview

Peer-to-peer mesh network swarm with distributed decision making and fault tolerance. Decentralized coordination where each agent is both client and server, contributing to collective intelligence and system resilience.

## Quick Start

```bash
# Initialize mesh network
mcp__claude-flow__swarm_init mesh --maxAgents=12 --strategy=distributed

# Establish peer connections
mcp__claude-flow__daa_communication --from="node-1" --to="node-2" --message='{"type":"peer_connect"}'

# Set up consensus
mcp__claude-flow__daa_consensus --agents="all" --proposal='{"coordination_protocol":"gossip","consensus_threshold":0.67}'

# Monitor network health
mcp__claude-flow__swarm_monitor --interval=3000 --metrics="connectivity,latency,throughput"
```

## When to Use

- High fault tolerance requirements
- Need for decentralized decision making
- Network partition risk exists
- Highly parallelizable workloads
- No single point of failure acceptable
- Load distribution more important than coordination costs

## Core Concepts

### Architecture

```
    MESH TOPOLOGY
   A <-> B <-> C
   ^     ^     ^
   v     v     v
   D <-> E <-> F
   ^     ^     ^
   v     v     v
   G <-> H <-> I
```

Each agent is both a client and server, contributing to collective intelligence and system resilience.

### Core Principles

| Principle | Description |
|-----------|-------------|
| Decentralized Coordination | No single point of failure, distributed decision making |
| Fault Tolerance | Automatic failure detection, dynamic rerouting |
| Collective Intelligence | Distributed problem solving, shared learning |

### Gossip Algorithm

```yaml
Purpose: Information dissemination across the network
Process:
  1. Each node periodically selects random peers
  2. Exchange state information and updates
  3. Propagate changes throughout network
  4. Eventually consistent global state

Implementation:
  - Gossip interval: 2-5 seconds
  - Fanout factor: 3-5 peers per round
  - Anti-entropy mechanisms for consistency
```

### Consensus Protocols

| Protocol | Use Case | Fault Tolerance |
|----------|----------|-----------------|
| Byzantine (pBFT) | Critical decisions | Up to 33% malicious nodes |
| Raft | Leader election | Majority quorum |
| Gossip-based | Eventual consistency | High partition tolerance |

## MCP Tool Integration

### Network Management

```bash
# Initialize mesh network
mcp__claude-flow__swarm_init mesh --maxAgents=12 --strategy=distributed

# Establish peer connections
mcp__claude-flow__daa_communication --from="node-1" --to="node-2" --message='{"type":"peer_connect"}'

# Monitor network health
mcp__claude-flow__swarm_monitor --interval=3000 --metrics="connectivity,latency,throughput"
```

### Consensus Operations

```bash
# Propose network-wide decision
mcp__claude-flow__daa_consensus --agents="all" --proposal='{"task_assignment":"auth-service","assigned_to":"node-3"}'

# Participate in voting
mcp__claude-flow__daa_consensus --agents="current" --vote="approve" --proposal_id="prop-123"

# Monitor consensus status
mcp__claude-flow__neural_patterns analyze --operation="consensus_tracking" --outcome="decision_approved"
```

### Fault Tolerance

```bash
# Detect failed nodes
mcp__claude-flow__daa_fault_tolerance --agentId="node-4" --strategy="heartbeat_monitor"

# Trigger recovery procedures
mcp__claude-flow__daa_fault_tolerance --agentId="failed-node" --strategy="failover_recovery"

# Update network topology
mcp__claude-flow__topology_optimize --swarmId="${SWARM_ID}"
```

## Usage Examples

### Example 1: Work Stealing Protocol

```python
class WorkStealingProtocol:
    def __init__(self):
        self.local_queue = TaskQueue()
        self.peer_connections = PeerNetwork()

    def steal_work(self):
        if self.local_queue.is_empty():
            # Find overloaded peers
            candidates = self.find_busy_peers()
            for peer in candidates:
                stolen_task = peer.request_task()
                if stolen_task:
                    self.local_queue.add(stolen_task)
                    break

    def distribute_work(self, task):
        if self.is_overloaded():
            # Find underutilized peers
            target_peer = self.find_available_peer()
            if target_peer:
                target_peer.assign_task(task)
                return
        self.local_queue.add(task)
```

### Example 2: Auction-Based Task Assignment

```python
class TaskAuction:
    def conduct_auction(self, task):
        # Broadcast task to all peers
        bids = self.broadcast_task_request(task)

        # Evaluate bids based on:
        evaluated_bids = []
        for bid in bids:
            score = self.evaluate_bid(bid, criteria={
                'capability_match': 0.4,
                'current_load': 0.3,
                'past_performance': 0.2,
                'resource_availability': 0.1
            })
            evaluated_bids.append((bid, score))

        # Award to highest scorer
        winner = max(evaluated_bids, key=lambda x: x[1])
        return self.award_task(task, winner[0])
```

### Example 3: Heartbeat Monitoring

```python
class HeartbeatMonitor:
    def __init__(self, timeout=10, interval=3):
        self.peers = {}
        self.timeout = timeout
        self.interval = interval

    def monitor_peer(self, peer_id):
        last_heartbeat = self.peers.get(peer_id, 0)
        if time.time() - last_heartbeat > self.timeout:
            self.trigger_failure_detection(peer_id)

    def trigger_failure_detection(self, peer_id):
        # Initiate failure confirmation protocol
        confirmations = self.request_failure_confirmations(peer_id)
        if len(confirmations) >= self.quorum_size():
            self.handle_peer_failure(peer_id)
```

## Best Practices

### Network Design

1. **Optimal Connectivity**: Maintain 3-5 connections per node
2. **Redundant Paths**: Ensure multiple routes between nodes
3. **Geographic Distribution**: Spread nodes across network zones
4. **Capacity Planning**: Size network for peak load + 25% headroom

### Consensus Optimization

1. **Quorum Sizing**: Use smallest viable quorum (>50%)
2. **Timeout Tuning**: Balance responsiveness vs. stability
3. **Batching**: Group operations for efficiency
4. **Preprocessing**: Validate proposals before consensus

### Fault Tolerance

1. **Proactive Monitoring**: Detect issues before failures
2. **Graceful Degradation**: Maintain core functionality
3. **Recovery Procedures**: Automated healing processes
4. **Backup Strategies**: Replicate critical state/data

## Performance Metrics

### Network Health

| Metric | Description |
|--------|-------------|
| Connectivity | Percentage of nodes reachable |
| Latency | Average message delivery time |
| Throughput | Messages processed per second |
| Partition Resilience | Recovery time from splits |

### Consensus Efficiency

| Metric | Description |
|--------|-------------|
| Decision Latency | Time to reach consensus |
| Vote Participation | Percentage of nodes voting |
| Byzantine Tolerance | Fault threshold maintained |
| View Changes | Leader election frequency |

### Load Distribution

| Metric | Description |
|--------|-------------|
| Load Variance | Standard deviation of node utilization |
| Migration Frequency | Task redistribution rate |
| Hotspot Detection | Identification of overloaded nodes |
| Resource Utilization | Overall system efficiency |

## Integration Points

### Works With

- **swarm-hierarchical**: When centralized coordination needed
- **swarm-adaptive**: For dynamic topology switching
- **swarm-memory**: For distributed state management
- **swarm-collective**: For consensus building

### Handoff Patterns

1. Receive peer request -> Validate -> Process or forward
2. Detect failure -> Confirm with quorum -> Recover
3. Receive task -> Bid/auction -> Execute or delegate

## Related Skills

- [swarm-hierarchical](../swarm-hierarchical/SKILL.md) - Central coordination
- [swarm-adaptive](../swarm-adaptive/SKILL.md) - Dynamic topology
- [swarm-collective](../swarm-collective/SKILL.md) - Consensus building

---

## Version History

- **1.0.0** (2026-01-02): Initial skill creation from mesh-coordinator agent
