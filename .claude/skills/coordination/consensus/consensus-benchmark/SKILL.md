# Performance Benchmarker Skill

> Version: 1.0.0
> Created: 2026-01-02
> Last Updated: 2026-01-02

## Overview

Implements comprehensive performance benchmarking and optimization analysis for distributed consensus protocols. Measures throughput, latency, and resource utilization while providing adaptive tuning recommendations.

## Quick Start

```bash
# Invoke skill for performance benchmarking
/consensus-benchmark

# Or via Task tool
Task("Performance Benchmarker", "Benchmark consensus protocol performance", "performance-benchmarker")
```

## When to Use

- **Protocol Benchmarking**: Measuring throughput, latency, and scalability
- **Resource Monitoring**: Tracking CPU, memory, network, and storage utilization
- **Comparative Analysis**: Comparing Byzantine, Raft, and Gossip performance
- **Adaptive Tuning**: Real-time parameter optimization
- **Performance Reporting**: Generating actionable optimization recommendations

## Core Concepts

### Benchmark Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Throughput | Transactions per second | Maximize |
| Latency | End-to-end response time | Minimize |
| P99 Latency | 99th percentile latency | < 100ms |
| CPU Usage | Processing overhead | < 80% |
| Memory | State storage requirements | Stable |

### Benchmark Phases
1. **Warmup**: Initialize system, fill caches
2. **Ramp-up**: Gradually increase load
3. **Steady-state**: Measure at target load
4. **Stress**: Find breaking point
5. **Recovery**: Measure recovery time

## Implementation Pattern

### Core Benchmarking Framework

```javascript
class ConsensusPerformanceBenchmarker {
  constructor() {
    this.benchmarkSuites = new Map();
    this.performanceMetrics = new Map();
    this.historicalData = new TimeSeriesDatabase();
    this.adaptiveOptimizer = new AdaptiveOptimizer();
  }

  registerBenchmarkSuite(protocolName, benchmarkConfig) {
    const suite = new BenchmarkSuite(protocolName, benchmarkConfig);
    this.benchmarkSuites.set(protocolName, suite);
    return suite;
  }

  async runComprehensiveBenchmarks(protocols, scenarios) {
    const results = new Map();

    for (const protocol of protocols) {
      const protocolResults = new Map();

      for (const scenario of scenarios) {
        console.log(\`Running \${scenario.name} benchmark for \${protocol}\`);
        const benchmarkResult = await this.executeBenchmarkScenario(protocol, scenario);
        protocolResults.set(scenario.name, benchmarkResult);

        await this.historicalData.store({
          protocol,
          scenario: scenario.name,
          timestamp: Date.now(),
          metrics: benchmarkResult
        });
      }

      results.set(protocol, protocolResults);
    }

    const analysis = await this.generateComparativeAnalysis(results);
    await this.adaptiveOptimizer.optimizeBasedOnResults(results);

    return {
      benchmarkResults: results,
      comparativeAnalysis: analysis,
      recommendations: await this.generateOptimizationRecommendations(results)
    };
  }

  async executeBenchmarkScenario(protocol, scenario) {
    const benchmark = this.benchmarkSuites.get(protocol);
    if (!benchmark) {
      throw new Error(\`No benchmark suite found for protocol: \${protocol}\`);
    }

    const environment = await this.setupBenchmarkEnvironment(scenario);

    try {
      await benchmark.setup(environment);

      const results = {
        throughput: await this.measureThroughput(benchmark, scenario),
        latency: await this.measureLatency(benchmark, scenario),
        resourceUsage: await this.measureResourceUsage(benchmark, scenario),
        scalability: await this.measureScalability(benchmark, scenario),
        faultTolerance: await this.measureFaultTolerance(benchmark, scenario)
      };

      results.analysis = await this.analyzeBenchmarkResults(results);
      return results;
    } finally {
      await this.cleanupBenchmarkEnvironment(environment);
    }
  }
}
```

### Throughput Measurement

```javascript
class ThroughputBenchmark {
  constructor(protocol, configuration) {
    this.protocol = protocol;
    this.config = configuration;
    this.metrics = new MetricsCollector();
    this.loadGenerator = new LoadGenerator();
  }

  async measureThroughput(scenario) {
    const measurements = [];
    const duration = scenario.duration || 60000;
    const startTime = Date.now();

    await this.loadGenerator.initialize({
      requestRate: scenario.initialRate || 10,
      rampUp: scenario.rampUp || false,
      pattern: scenario.pattern || 'constant'
    });

    this.metrics.startCollection(['transactions_per_second', 'success_rate']);

    let currentRate = scenario.initialRate || 10;
    const rateIncrement = scenario.rateIncrement || 5;
    const measurementInterval = 5000;

    while (Date.now() - startTime < duration) {
      const intervalStart = Date.now();
      const transactions = await this.generateTransactionLoad(currentRate, measurementInterval);
      const intervalMetrics = await this.measureIntervalThroughput(transactions, measurementInterval);

      measurements.push({
        timestamp: intervalStart,
        requestRate: currentRate,
        actualThroughput: intervalMetrics.throughput,
        successRate: intervalMetrics.successRate,
        averageLatency: intervalMetrics.averageLatency,
        p95Latency: intervalMetrics.p95Latency,
        p99Latency: intervalMetrics.p99Latency
      });

      if (scenario.rampUp && intervalMetrics.successRate > 0.95) {
        currentRate += rateIncrement;
      } else if (intervalMetrics.successRate < 0.8) {
        currentRate = Math.max(1, currentRate - rateIncrement);
      }

      const elapsed = Date.now() - intervalStart;
      if (elapsed < measurementInterval) {
        await this.sleep(measurementInterval - elapsed);
      }
    }

    this.metrics.stopCollection();
    return this.analyzeThroughputMeasurements(measurements);
  }

  analyzeThroughputMeasurements(measurements) {
    const totalMeasurements = measurements.length;
    const avgThroughput = measurements.reduce((sum, m) => sum + m.actualThroughput, 0) / totalMeasurements;
    const maxThroughput = Math.max(...measurements.map(m => m.actualThroughput));
    const avgSuccessRate = measurements.reduce((sum, m) => sum + m.successRate, 0) / totalMeasurements;

    const optimalPoints = measurements.filter(m => m.successRate >= 0.95);
    const optimalThroughput = optimalPoints.length > 0 ?
      Math.max(...optimalPoints.map(m => m.actualThroughput)) : 0;

    return {
      averageThroughput: avgThroughput,
      maxThroughput,
      optimalThroughput,
      averageSuccessRate: avgSuccessRate,
      measurements,
      sustainableThroughput: this.calculateSustainableThroughput(measurements)
    };
  }
}
```

### Latency Analysis

```javascript
class LatencyBenchmark {
  constructor(protocol, configuration) {
    this.protocol = protocol;
    this.config = configuration;
    this.percentileCalculator = new PercentileCalculator();
  }

  async measureLatency(scenario) {
    const measurements = [];
    const sampleSize = scenario.sampleSize || 10000;
    const warmupSize = scenario.warmupSize || 1000;

    await this.performWarmup(warmupSize);

    for (let i = 0; i < sampleSize; i++) {
      const latencyMeasurement = await this.measureSingleTransactionLatency();
      measurements.push(latencyMeasurement);

      if (i % 1000 === 0) {
        console.log(\`Completed \${i}/\${sampleSize} latency measurements\`);
      }
    }

    return this.analyzeLatencyDistribution(measurements);
  }

  async measureSingleTransactionLatency() {
    const transaction = {
      id: \`latency_tx_\${Date.now()}_\${Math.random()}\`,
      type: 'benchmark',
      data: { value: Math.random() },
      phases: {}
    };

    const submissionStart = performance.now();
    const submissionPromise = this.protocol.submitTransaction(transaction);
    transaction.phases.submission = performance.now() - submissionStart;

    const consensusStart = performance.now();
    const result = await submissionPromise;
    transaction.phases.consensus = performance.now() - consensusStart;

    transaction.phases.application = result.applicationTime || 0;

    const totalLatency = transaction.phases.submission +
                        transaction.phases.consensus +
                        transaction.phases.application;

    return {
      transactionId: transaction.id,
      totalLatency,
      phases: transaction.phases,
      success: result.committed === true,
      timestamp: Date.now()
    };
  }

  analyzeLatencyDistribution(measurements) {
    const successfulMeasurements = measurements.filter(m => m.success);
    const latencies = successfulMeasurements.map(m => m.totalLatency);

    const percentiles = this.percentileCalculator.calculate(latencies, [
      50, 75, 90, 95, 99, 99.9, 99.99
    ]);

    return {
      sampleSize: successfulMeasurements.length,
      mean: latencies.reduce((sum, l) => sum + l, 0) / latencies.length,
      median: percentiles[50],
      standardDeviation: this.calculateStandardDeviation(latencies),
      percentiles,
      phaseAnalysis: this.analyzePhaseLatencies(successfulMeasurements)
    };
  }
}
```

### Resource Usage Monitor

```javascript
class ResourceUsageMonitor {
  constructor() {
    this.monitoringActive = false;
    this.samplingInterval = 1000;
    this.measurements = [];
  }

  async collectResourceMeasurement() {
    return {
      timestamp: Date.now(),
      cpu: {
        totalUsage: await this.getCPUUsage(),
        loadAverage: await this.getLoadAverage()
      },
      memory: {
        totalUsed: await this.getMemoryUsed(),
        processRSS: process.memoryUsage().rss,
        processHeap: process.memoryUsage().heapUsed
      },
      network: {
        bytesIn: await this.getNetworkBytesIn(),
        bytesOut: await this.getNetworkBytesOut()
      }
    };
  }

  identifyResourceBottlenecks() {
    const bottlenecks = [];

    const avgCPU = this.measurements.reduce((sum, m) => sum + m.cpu.totalUsage, 0) /
                   this.measurements.length;
    if (avgCPU > 80) {
      bottlenecks.push({
        type: 'CPU',
        severity: 'HIGH',
        description: \`High CPU usage (\${avgCPU.toFixed(1)}%)\`
      });
    }

    const memoryGrowth = this.calculateMemoryGrowth();
    if (memoryGrowth.rate > 1024 * 1024) {
      bottlenecks.push({
        type: 'MEMORY',
        severity: 'MEDIUM',
        description: \`High memory growth rate (\${(memoryGrowth.rate / 1024 / 1024).toFixed(2)} MB/s)\`
      });
    }

    return bottlenecks;
  }
}
```

### Adaptive Optimizer

```javascript
class AdaptiveOptimizer {
  constructor() {
    this.optimizationHistory = new Map();
    this.performanceModel = new PerformanceModel();
  }

  async optimizeBasedOnResults(benchmarkResults) {
    const optimizations = [];

    for (const [protocol, results] of benchmarkResults) {
      const protocolOptimizations = await this.optimizeProtocol(protocol, results);
      optimizations.push(...protocolOptimizations);
    }

    await this.applyOptimizations(optimizations);
    return optimizations;
  }

  identifyPerformanceBottlenecks(results) {
    const bottlenecks = [];

    for (const [scenario, result] of results) {
      if (result.throughput && result.throughput.optimalThroughput < result.throughput.maxThroughput * 0.8) {
        bottlenecks.push({
          type: 'THROUGHPUT_DEGRADATION',
          scenario,
          severity: 'HIGH',
          impact: (result.throughput.maxThroughput - result.throughput.optimalThroughput) /
                 result.throughput.maxThroughput
        });
      }

      if (result.latency && result.latency.p99 > result.latency.p50 * 10) {
        bottlenecks.push({
          type: 'LATENCY_TAIL',
          scenario,
          severity: 'MEDIUM',
          impact: result.latency.p99 / result.latency.p50
        });
      }

      if (result.resourceUsage && result.resourceUsage.bottlenecks.length > 0) {
        bottlenecks.push({
          type: 'RESOURCE_CONSTRAINT',
          scenario,
          severity: 'HIGH',
          details: result.resourceUsage.bottlenecks
        });
      }
    }

    return bottlenecks;
  }
}
```

## Usage Examples

### Basic Benchmarking

```javascript
const benchmarker = new ConsensusPerformanceBenchmarker();

benchmarker.registerBenchmarkSuite('raft', {
  protocol: raftConsensus,
  warmupDuration: 10000,
  measurementDuration: 60000
});

const results = await benchmarker.runComprehensiveBenchmarks(
  ['raft', 'pbft', 'gossip'],
  [
    { name: 'low_load', initialRate: 10, rampUp: false },
    { name: 'high_load', initialRate: 100, rampUp: true },
    { name: 'stress', initialRate: 1000, duration: 120000 }
  ]
);

console.log('Throughput:', results.benchmarkResults.get('raft').get('high_load').throughput);
console.log('Recommendations:', results.recommendations);
```

### Resource Monitoring

```javascript
const monitor = new ResourceUsageMonitor();

const resourceResults = await monitor.measureResourceUsage(protocol, {
  duration: 60000,
  samplingInterval: 1000
});

console.log('CPU Analysis:', resourceResults.resourceUsage.cpu);
console.log('Memory Analysis:', resourceResults.resourceUsage.memory);
console.log('Bottlenecks:', resourceResults.resourceUsage.bottlenecks);
```

## MCP Integration

```javascript
await mcp__claude-flow__memory_usage({
  action: 'store',
  key: \`benchmark_results_\${protocol}_\${Date.now()}\`,
  value: JSON.stringify({
    protocol,
    timestamp: Date.now(),
    throughput: throughputResults,
    latency: latencyResults,
    resourceUsage: resourceResults,
    optimizations: appliedOptimizations
  }),
  namespace: 'performance_benchmarks',
  ttl: 604800000
});
```

## Collaboration

- **Byzantine Coordinator**: Byzantine protocol benchmarking
- **Raft Manager**: Raft protocol benchmarking
- **Gossip Coordinator**: Gossip protocol benchmarking
- **Quorum Manager**: Quorum configuration optimization

## Best Practices

1. **Warmup**: Always include warmup phase before measurement
2. **Sample Size**: Use sufficient samples for statistical significance
3. **Isolation**: Run benchmarks in isolated environments
4. **Baseline**: Establish baselines before optimization
5. **Reproducibility**: Document all benchmark parameters

## Hooks

```bash
# Pre-task hook
echo "Performance Benchmarker analyzing: \$TASK"
if [[ "\$TASK" == *"benchmark"* ]]; then
  echo "Starting performance metric collection"
fi

# Post-task hook
echo "Performance analysis complete"
echo "Compiling benchmarking results and recommendations"
```

## Related Skills

- [consensus-byzantine](../consensus-byzantine/SKILL.md) - Byzantine consensus
- [consensus-raft](../consensus-raft/SKILL.md) - Raft consensus
- [consensus-quorum](../consensus-quorum/SKILL.md) - Quorum management

---

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from performance-benchmarker agent
