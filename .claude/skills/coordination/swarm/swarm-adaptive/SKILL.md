# Swarm Adaptive Coordinator Skill

> Version: 1.0.0
> Created: 2026-01-02
> Category: Swarm Coordination
> Priority: Critical

## Overview

Dynamic topology switching coordinator with self-organizing swarm patterns and real-time optimization. Intelligent orchestrator that adapts swarm topology and coordination strategies based on performance metrics, workload patterns, and environmental conditions.

## Quick Start

```bash
# Initialize with auto-detection
mcp__claude-flow__swarm_init auto --maxAgents=15 --strategy=adaptive

# Analyze workload patterns
mcp__claude-flow__neural_patterns analyze --operation="workload_analysis" --metadata='{"task":"complex_feature"}'

# Train adaptive models
mcp__claude-flow__neural_train coordination --training_data="historical_swarm_data" --epochs=30

# Auto-optimize topology
mcp__claude-flow__topology_optimize --swarmId="${SWARM_ID}"
```

## When to Use

- Mixed workload characteristics requiring different approaches
- Need for continuous optimization based on performance
- Projects with changing requirements over time
- Want to leverage machine learning for coordination
- Uncertain which topology is optimal

## Core Concepts

### Architecture

```
ADAPTIVE INTELLIGENCE LAYER
    v Real-time Analysis v
TOPOLOGY SWITCHING ENGINE
    v Dynamic Optimization v
+-----------------------------+
| HIERARCHICAL | MESH | RING  |
|      ^       |  ^   |   ^   |
|   WORKERS    |PEERS |CHAIN  |
+-----------------------------+
    v Performance Feedback v
LEARNING & PREDICTION ENGINE
```

### Intelligence Systems

| System | Function |
|--------|----------|
| Topology Adaptation | Real-time monitoring, dynamic switching, predictive scaling |
| Self-Organizing | Emergent behaviors, adaptive load balancing, intelligent routing |
| Machine Learning | Neural pattern analysis, predictive analytics, reinforcement learning |

### Topology Switching Conditions

```yaml
Switch to HIERARCHICAL when:
  - Task complexity score > 0.8
  - Inter-agent coordination requirements > 0.7
  - Need for centralized decision making
  - Resource conflicts requiring arbitration

Switch to MESH when:
  - Task parallelizability > 0.8
  - Fault tolerance requirements > 0.7
  - Network partition risk exists
  - Load distribution benefits outweigh coordination costs

Switch to RING when:
  - Sequential processing required
  - Pipeline optimization possible
  - Memory constraints exist
  - Ordered execution mandatory

Switch to HYBRID when:
  - Mixed workload characteristics
  - Multiple optimization objectives
  - Transitional phases between topologies
  - Experimental optimization required
```

## MCP Tool Integration

### Pattern Recognition & Learning

```bash
# Analyze coordination patterns
mcp__claude-flow__neural_patterns analyze --operation="topology_analysis" --metadata='{"current_topology":"mesh","performance_metrics":{}}'

# Train adaptive models
mcp__claude-flow__neural_train coordination --training_data="swarm_performance_history" --epochs=50

# Make predictions
mcp__claude-flow__neural_predict --modelId="adaptive-coordinator" --input='{"workload":"high_complexity","agents":10}'

# Learn from outcomes
mcp__claude-flow__neural_patterns learn --operation="topology_switch" --outcome="improved_performance_15%" --metadata='{"from":"hierarchical","to":"mesh"}'
```

### Performance Optimization

```bash
# Real-time performance monitoring
mcp__claude-flow__performance_report --format=json --timeframe=1h

# Bottleneck analysis
mcp__claude-flow__bottleneck_analyze --component="coordination" --metrics="latency,throughput,success_rate"

# Automatic optimization
mcp__claude-flow__topology_optimize --swarmId="${SWARM_ID}"

# Load balancing optimization
mcp__claude-flow__load_balance --swarmId="${SWARM_ID}" --strategy="ml_optimized"
```

### Predictive Scaling

```bash
# Analyze usage trends
mcp__claude-flow__trend_analysis --metric="agent_utilization" --period="7d"

# Predict resource needs
mcp__claude-flow__neural_predict --modelId="resource-predictor" --input='{"time_horizon":"4h","current_load":0.7}'

# Auto-scale swarm
mcp__claude-flow__swarm_scale --swarmId="${SWARM_ID}" --targetSize="12" --strategy="predictive"
```

## Usage Examples

### Example 1: Workload Analyzer

```python
class WorkloadAnalyzer:
    def analyze_task_characteristics(self, task):
        return {
            'complexity': self.measure_complexity(task),
            'parallelizability': self.assess_parallelism(task),
            'interdependencies': self.map_dependencies(task),
            'resource_requirements': self.estimate_resources(task),
            'time_sensitivity': self.evaluate_urgency(task)
        }

    def recommend_topology(self, characteristics):
        if characteristics['complexity'] == 'high' and characteristics['interdependencies'] == 'many':
            return 'hierarchical'  # Central coordination needed
        elif characteristics['parallelizability'] == 'high' and characteristics['time_sensitivity'] == 'low':
            return 'mesh'  # Distributed processing optimal
        elif characteristics['interdependencies'] == 'sequential':
            return 'ring'  # Pipeline processing
        else:
            return 'hybrid'  # Mixed approach
```

### Example 2: Real-Time Topology Optimizer

```python
class TopologyOptimizer:
    def __init__(self):
        self.performance_history = []
        self.topology_costs = {}
        self.adaptation_threshold = 0.2  # 20% improvement needed

    def evaluate_current_performance(self):
        metrics = self.collect_performance_metrics()
        current_score = self.calculate_performance_score(metrics)

        # Compare with historical performance
        if len(self.performance_history) > 10:
            avg_historical = sum(self.performance_history[-10:]) / 10
            if current_score < avg_historical * (1 - self.adaptation_threshold):
                return self.trigger_topology_analysis()

        self.performance_history.append(current_score)

    def trigger_topology_analysis(self):
        current_topology = self.get_current_topology()
        alternative_topologies = ['hierarchical', 'mesh', 'ring', 'hybrid']

        best_topology = current_topology
        best_predicted_score = self.predict_performance(current_topology)

        for topology in alternative_topologies:
            if topology != current_topology:
                predicted_score = self.predict_performance(topology)
                if predicted_score > best_predicted_score * (1 + self.adaptation_threshold):
                    best_topology = topology
                    best_predicted_score = predicted_score

        if best_topology != current_topology:
            return self.initiate_topology_switch(current_topology, best_topology)
```

### Example 3: Rollback Mechanisms

```python
class TopologyRollback:
    def __init__(self):
        self.topology_snapshots = {}
        self.rollback_triggers = {
            'performance_degradation': 0.25,  # 25% worse performance
            'error_rate_increase': 0.15,      # 15% more errors
            'agent_failure_rate': 0.3         # 30% agent failures
        }

    def create_snapshot(self, topology_name):
        snapshot = {
            'topology': self.get_current_topology_config(),
            'agent_assignments': self.get_agent_assignments(),
            'performance_baseline': self.get_performance_metrics(),
            'timestamp': time.time()
        }
        self.topology_snapshots[topology_name] = snapshot

    def monitor_for_rollback(self):
        current_metrics = self.get_current_metrics()
        baseline = self.get_last_stable_baseline()

        for trigger, threshold in self.rollback_triggers.items():
            if self.evaluate_trigger(current_metrics, baseline, trigger, threshold):
                return self.initiate_rollback()
```

## Topology Transition Protocol

### Migration Phases

| Phase | Activities |
|-------|------------|
| Pre-Migration | Performance baseline, capability assessment, dependency mapping |
| Planning | Optimal timing, agent reassignment, rollback strategy |
| Transition | Incremental changes, continuous monitoring, dynamic adjustment |
| Post-Migration | Fine-tuning, validation, model updates |

## Best Practices

### Adaptive Strategy Design

1. **Gradual Transitions**: Avoid abrupt topology changes that disrupt work
2. **Performance Validation**: Always validate improvements before committing
3. **Rollback Preparedness**: Have quick recovery options for failed adaptations
4. **Learning Integration**: Continuously incorporate new insights into models

### Machine Learning Optimization

1. **Feature Engineering**: Identify relevant metrics for decision making
2. **Model Validation**: Use cross-validation for robust evaluation
3. **Online Learning**: Update models continuously with new data
4. **Ensemble Methods**: Combine multiple models for better predictions

### System Monitoring

1. **Multi-Dimensional Metrics**: Track performance, resource usage, and quality
2. **Real-Time Dashboards**: Provide visibility into adaptation decisions
3. **Alert Systems**: Notify of significant performance changes or failures
4. **Historical Analysis**: Learn from past adaptations and outcomes

## Performance Metrics

### Adaptation Effectiveness

| Metric | Description |
|--------|-------------|
| Topology Switch Success Rate | Percentage of beneficial switches |
| Performance Improvement | Average gain from adaptations |
| Adaptation Speed | Time to complete transitions |
| Prediction Accuracy | Correctness of forecasts |

### Learning Progress

| Metric | Description |
|--------|-------------|
| Model Accuracy Improvement | Enhancement in prediction precision |
| Pattern Recognition Rate | Recurring optimization opportunities |
| Transfer Learning Success | Pattern application across contexts |
| Adaptation Convergence Time | Speed to optimal configurations |

## Integration Points

### Works With

- **swarm-hierarchical**: Target topology option
- **swarm-mesh**: Target topology option
- **swarm-memory**: For state persistence
- **swarm-collective**: For consensus on topology changes

### Handoff Patterns

1. Analyze workload -> Recommend topology -> Execute switch
2. Monitor performance -> Detect degradation -> Trigger adaptation
3. Train models -> Make predictions -> Validate outcomes

## Related Skills

- [swarm-hierarchical](../swarm-hierarchical/SKILL.md) - Central coordination
- [swarm-mesh](../swarm-mesh/SKILL.md) - Peer-to-peer coordination
- [swarm-collective](../swarm-collective/SKILL.md) - Consensus building

---

## Version History

- **1.0.0** (2026-01-02): Initial skill creation from adaptive-coordinator agent
