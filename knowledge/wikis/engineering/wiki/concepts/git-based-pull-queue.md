---
title: "Git-Based Pull Queue"
tags: [architecture, queue, git, solver, pull-pattern]
sources:
  - solver-queue-architecture-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Git-Based Pull Queue

Reusable pattern: asynchronous job dispatch across firewall-separated machines using git as the transport layer.

## Problem

Corporate firewalls block inbound connections to licensed solver machines. Traditional SSH-based push models fail. A pull-based architecture using git as the message bus requires only outbound connections from the solver machine.

## Architecture

```
dev-primary         GitHub              licensed-win-1
----------         ------              --------------
submit-job.sh --push-->  queue/pending/job.yaml
                                        <--pull-- Task Scheduler (30 min)
                                                  process-queue.py
                                                  OrcFxAPI execution
                    queue/completed/    <--push-- results + logs
poll results  <--pull--
```

## Key Design Decisions

1. **Git as transport** (not SSH, not HTTP API) -- zero infrastructure beyond the repo
2. **Pull-based polling** (not push) -- satisfies corporate firewall
3. **YAML job files** (not database) -- human-readable, git-diffable, auditable
4. **PyYAML optional** with built-in flat-key fallback parser
5. **Python 3.9+ compatible** -- matches OrcFxAPI support range

## Reuse Potential

Applies to any scenario where:
- A compute resource is behind a firewall blocking inbound connections
- Job throughput is low enough for 30-minute polling
- Git is available on both sides
- Jobs are describable as small YAML files

Potential: CFD dispatch, FEA batch runs, any licensed-tool automation.

## Cross-References

- **Related entity**: [Solver Queue](../entities/solver-queue.md)
- **Related concept**: [[orchestrator-worker-separation]]
