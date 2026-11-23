---
name: test-oversized-skill
description: A test fixture skill that exceeds 200 lines with multiple H2/H3 sections for split testing.
version: 1.0.0
category: engineering
tags: [test, fixture]
scripts_exempt: true
---

# Test Oversized Skill

> Hub for testing the split-oversized-skill.py script.

## When to Use

- When you need to test the split script
- When you need a fixture with known structure

## Prerequisites

- Python 3.10+
- pytest

## Core Capabilities

### Widget Processing

Widget processing handles the transformation of raw widgets into
processed output. The algorithm uses a three-phase approach:

1. **Parse** — Read the input widget definition
2. **Transform** — Apply transformation rules
3. **Emit** — Write the output

```python
from widget_engine import WidgetProcessor

processor = WidgetProcessor()
result = processor.run("input.yaml")
print(result.summary())
```

Key configuration options:

| Option | Default | Description |
|--------|---------|-------------|
| `mode` | `standard` | Processing mode |
| `parallel` | `false` | Enable parallel processing |
| `timeout` | `30` | Timeout in seconds |

Advanced usage with custom transforms:

```python
processor = WidgetProcessor(
    mode="advanced",
    transforms=[
        CustomTransform("normalize"),
        CustomTransform("validate"),
    ]
)
```

Line padding to ensure this section is substantial enough for testing.
More content here to pad the section.
Additional detail about widget processing internals.
The widget processor maintains an internal state machine.
State transitions are logged for debugging.
Each state has entry and exit actions.
The processor supports both synchronous and asynchronous modes.
Async mode uses Python's asyncio under the hood.
Error handling follows the fail-fast principle.
All exceptions are propagated to the caller.
Retry logic can be configured per-transform.
The default retry count is 3.
Backoff is exponential with a base of 2 seconds.
Maximum backoff is capped at 60 seconds.
Jitter is added to prevent thundering herd.
Metrics are emitted for each processing stage.
Prometheus-compatible metrics are available.
Grafana dashboards can be auto-generated.
The processor supports plugin architecture.
Plugins are loaded at startup via entry points.
Each plugin can register custom transforms.
Plugin priority determines execution order.
Higher priority plugins execute first.

### Gadget Analysis

Gadget analysis provides tools for examining gadget structures
and computing quality metrics.

```python
from gadget_analyzer import GadgetAnalyzer

analyzer = GadgetAnalyzer()
report = analyzer.analyze("gadgets/")
report.save("analysis_report.html")
```

The analyzer supports multiple output formats:

- HTML reports with interactive charts
- JSON for programmatic consumption
- CSV for spreadsheet analysis
- PDF for formal documentation

Quality metrics computed:

| Metric | Range | Threshold |
|--------|-------|-----------|
| Completeness | 0-100 | >80 |
| Consistency | 0-100 | >90 |
| Coverage | 0-100 | >75 |

Advanced analysis with custom rules:

```python
analyzer = GadgetAnalyzer(
    rules=["rule_completeness", "rule_naming"],
    threshold=85,
)
```

More detail about gadget analysis internals.
The analyzer builds an abstract syntax tree of gadget definitions.
Each node in the tree represents a gadget component.
Components are scored individually and aggregated.
The scoring algorithm uses weighted averages.
Default weights can be overridden via configuration.
Configuration files use YAML format.
Schema validation is performed on load.
Invalid configs raise ConfigurationError.
The analyzer caches intermediate results.
Cache invalidation is based on file modification time.
LRU cache with a default size of 1000 entries.
Cache statistics are exposed via the metrics endpoint.
The analyzer supports incremental mode.
In incremental mode only changed files are re-analyzed.
Change detection uses file hashes (SHA-256).
The hash index is stored in .gadget-cache/.
This directory should be gitignored.

### Doohickey Optimization

Doohickey optimization finds the optimal configuration for
doohickey deployments using constraint satisfaction.

```python
from doohickey_optimizer import DoohickeyOptimizer

optimizer = DoohickeyOptimizer(
    constraints={"max_cost": 1000, "min_quality": 0.9},
)
result = optimizer.optimize("deployment.yaml")
print(f"Optimal config: {result.config}")
print(f"Cost: {result.cost}")
```

Supported constraint types:

- Budget constraints (max cost)
- Quality constraints (min quality score)
- Time constraints (max deployment time)
- Resource constraints (max CPU/memory)

The optimizer uses a branch-and-bound algorithm.
Search space pruning reduces computation time.
Feasibility checks are performed at each node.
The algorithm guarantees optimality for linear constraints.
Non-linear constraints use approximation methods.
Approximation quality is configurable.
Default approximation tolerance is 1e-6.
The optimizer supports warm-starting from previous solutions.
Warm starts can reduce optimization time by up to 80%.
Solution history is maintained for warm-start support.
The history is stored in memory by default.
Persistent history can be enabled via configuration.
The optimizer emits events during optimization.
Events can be consumed by custom callbacks.
Built-in callbacks include progress reporting.
Progress is reported as percentage of search space explored.
The optimizer is thread-safe for concurrent use.
Connection pooling is used for database-backed constraints.
Pool size defaults to 10 connections.
Idle connections are recycled after 60 seconds.
More padding content here.
Additional optimization details.
The optimizer log includes timing information.
Each iteration records start time, end time, and result.

## Integration Examples

### CI/CD Integration

```bash
# Run in CI pipeline
python -m widget_engine --ci --output results/
python -m gadget_analyzer --ci --threshold 80
python -m doohickey_optimizer --validate-only
```

### Docker Integration

```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["python", "-m", "widget_engine", "--serve"]
```

Configuration for Docker:

```yaml
# docker-compose.yml
services:
  engine:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    environment:
      - ENGINE_MODE=production
      - LOG_LEVEL=info
```

More CI/CD content and examples.
Pipeline stages for full integration.
Stage 1: Lint and format check.
Stage 2: Unit tests with coverage.
Stage 3: Integration tests.
Stage 4: Widget processing benchmark.
Stage 5: Gadget analysis validation.
Stage 6: Doohickey optimization dry run.
Stage 7: Deploy to staging.
Stage 8: Smoke tests on staging.
Stage 9: Deploy to production.
Stage 10: Post-deployment verification.

## Best Practices

### Configuration Management

- Use environment variables for secrets
- Keep configuration in version control
- Validate all configs on startup
- Use schema validation for YAML configs
- Document all configuration options
- Provide sensible defaults
- Support environment-specific overrides

### Error Handling

- Use specific exception types
- Include context in error messages
- Log errors with structured data
- Implement retry logic for transient failures
- Set appropriate timeouts
- Use circuit breakers for external services
- Monitor error rates and alert on anomalies

### Performance

- Profile before optimizing
- Use caching for expensive computations
- Implement pagination for large result sets
- Use connection pooling for databases
- Monitor memory usage
- Set resource limits in production
- Use async I/O for I/O-bound operations

## Troubleshooting

### Common Issues

**Widget processor hangs:**
```bash
# Check for deadlocks
python -m widget_engine --diagnose
# Increase timeout
export WIDGET_TIMEOUT=120
```

**Gadget analysis slow:**
```bash
# Enable incremental mode
python -m gadget_analyzer --incremental
# Clear cache if stale
rm -rf .gadget-cache/
```

**Optimizer fails to converge:**
- Relax constraints (increase max_cost or decrease min_quality)
- Check for infeasible constraint combinations
- Enable verbose logging for debugging

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# All components respect the standard logging configuration
```

## Related Skills

- [widget-engine](../widget-engine/SKILL.md) — Core widget processing
- [gadget-tools](../gadget-tools/SKILL.md) — Gadget utilities
- [optimizer-suite](../optimizer-suite/SKILL.md) — Optimization algorithms

## References

- Widget Engine Documentation: https://example.com/widget-docs
- Gadget Analysis Guide: https://example.com/gadget-guide
