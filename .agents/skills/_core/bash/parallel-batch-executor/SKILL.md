---
name: parallel-batch-executor
version: 1.0.0
description: Parallel task execution patterns using xargs and job control for significant
  performance gains
author: workspace-hub
category: _core
tags:
- bash
- parallel
- xargs
- performance
- batch
- optimization
platforms:
- linux
- macos
see_also:
- parallel-batch-executor-1-basic-parallel-execution-with-xargs
- parallel-batch-executor-4-progress-tracking
- parallel-batch-executor-1-always-set-a-default
---

# Parallel Batch Executor

## When to Use This Skill

✅ **Use when:**
- Processing multiple independent files or items
- Running the same operation across multiple repositories
- Batch operations that don't depend on each other
- Need significant performance improvements
- Operations are I/O bound rather than CPU bound

❌ **Avoid when:**
- Tasks have dependencies on each other
- Order of execution matters
- Shared resources require synchronization
- Single task that can't be parallelized

## Complete Example: Batch Task Runner

Full implementation from workspace-hub:

```bash
#!/bin/bash
# ABOUTME: Batch Task Executor
# ABOUTME: Executes tasks in parallel using the Multi-Provider Orchestrator

set -e

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORCHESTRATOR="$SCRIPT_DIR/../routing/orchestrate.sh"
PARALLEL=1
LOG_DIR="$SCRIPT_DIR/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'


*See sub-skills for full details.*

## Performance Tuning

### Optimal Parallelism

```bash
# CPU-bound tasks: match CPU cores
PARALLEL=$(nproc)

# I/O-bound tasks: 2-4x CPU cores
PARALLEL=$(($(nproc) * 2))

# Network-bound tasks: higher parallelism
PARALLEL=20

# Memory-constrained: limit based on available RAM
AVAILABLE_MB=$(free -m | awk '/^Mem:/{print $7}')
TASK_MB=100  # Estimate per task
PARALLEL=$((AVAILABLE_MB / TASK_MB))
```
### Throttling

```bash
# Add delay between task starts
printf '%s\n' "${items[@]}" | xargs -I {} -P "$PARALLEL" bash -c "
    sleep 0.1  # 100ms delay
    process_item \"{}\"
"
```

## Resources

- [GNU xargs Manual](https://www.gnu.org/software/findutils/manual/html_node/find_html/xargs-options.html)
- [GNU Parallel Tutorial](https://www.gnu.org/software/parallel/parallel_tutorial.html)
- [Bash Process Substitution](https://mywiki.wooledge.org/ProcessSubstitution)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - extracted from workspace-hub batchtools

## Sub-Skills

- [1. Basic Parallel Execution with xargs (+2)](1-basic-parallel-execution-with-xargs/SKILL.md)
- [4. Progress Tracking (+2)](4-progress-tracking/SKILL.md)
- [1. Always Set a Default (+4)](1-always-set-a-default/SKILL.md)
