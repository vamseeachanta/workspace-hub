# WRK-1187 Research Report: Script-Based Workflow Engine

## Executive Summary

**Recommendation: Enhance the existing system, don't replace it.**

The workspace-hub already has a production-grade 20-stage FSM workflow engine
(80+ L2 scripts, 20 stage contracts, checkpoint persistence, human gates, audit
trail). External orchestrators (Temporal, Airflow, Prefect) offer patterns worth
borrowing but are overweight for a solo-developer ecosystem with no external infra.

**Three targeted enhancements** close the remaining gaps in ~190 lines of new code:

1. **Event-sourced crash recovery** (from Temporal) — ~50 lines
2. **Explicit transition table** (from FSM theory) — ~80 lines
3. **Content-addressed stage skipping** (from Dagger) — ~60 lines

Then **codify 5 prose-only workflows** as L2 scripts to promote them from L0/L1.

## Current State Assessment

### What Already Exists (L2/L3 — Strong)

| Component | Scripts | Coverage |
|-----------|---------|----------|
| WRK stage lifecycle | exit_stage.py, start_stage.py, checkpoint_writer.py | 20 stages, 4 human gates |
| Gate validation | verify-gate-evidence.py, is-human-gate.sh, gate_check.py | All gate types |
| Queue management | next-id.sh, claim-item.sh, close-item.sh, archive-item.sh | Full CRUD |
| Agent orchestration | session.sh, work.sh, plan.sh, execute.sh, review.sh | Multi-provider |
| Feature decomposition | new-feature.sh, feature-close-check.sh | Parent→children cascade |
| Audit trail | log-action.sh, log-gate-event.sh, audit-chain-state.json | Immutable JSONL |
| Nightly automation | comprehensive_learning_pipeline.py (10 phases) | Closed loop |
| Tests | 28+ test files in scripts/work-queue/tests/ | Regression coverage |

### What's Missing (L0/L1 — Prose Only)

These workflows exist only as skill prose — no script enforcement:

1. **Dark intelligence extraction** — Excel→YAML test data pipeline
2. **Research-literature gathering** — paper→action-item capture
3. **Calculation implementation** — TDD→implement→calc-report→commit
4. **Data source ingestion** — loader→tests→schema→commit
5. **Phase B doc extraction** — index→extract→classify→ledger→capmap

### Gaps in the Core Engine

| Gap | Impact | Fix Cost |
|-----|--------|----------|
| No crash recovery (replay) | Re-run entire pipeline on failure | ~50 LOC |
| Implicit transition order | Stage skipping possible via manual edits | ~80 LOC |
| No redundant-work avoidance | Re-execute expensive stages unnecessarily | ~60 LOC |
| No rollback support | Cannot formally revert to previous stage | Included in transition table |

## External Pattern Evaluation

### Temporal.io / Prefect / Airflow

| Pattern | Value | Adopt? |
|---------|-------|--------|
| Durable execution (event sourcing) | High — crash recovery via replay | **Yes** — append-only JSONL run log |
| Activity isolation | Already natural (script = activity) | Already have |
| Retry with backoff | Medium — per-step retry | **Yes** — 20-line bash function |
| DAG inference from decorators | Low — pipelines are linear | No |
| Human-in-the-loop signals | Already implemented via is-human-gate.sh | Already have |

### GitHub Actions / Dagger.io

| Pattern | Value | Adopt? |
|---------|-------|--------|
| Step dependency graph (`needs:`) | Already modeled by stage ordering | Already have |
| Artifact passing | Already have (exit_artifacts / entry_reads) | Already have |
| Conditional execution (`if:`) | Already have (pre_checks + blocking_condition) | Already have |
| Content-addressed caching | High — skip unchanged stages | **Yes** — hash entry_reads |
| Matrix strategy | Medium — multi-repo parallelism | Defer |

### Finite State Machine Patterns

| Pattern | Value | Adopt? |
|---------|-------|--------|
| Explicit transition table | High — formal state→state map | **Yes** — generate from stage YAML |
| Transition guards | Already have (pre_checks, gate predicates) | Already have |
| Rollback transitions | Medium — revert to previous stage | **Yes** — include in table |
| Hierarchical FSM | Already have (Feature WRK children) | Already have |

### Lightweight Tools (Make, Just, Taskfile, Luigi)

**Verdict: None provide meaningful value over the existing system.**

- Make: no state persistence, no human gates
- Just/Taskfile: pure command runners, no workflow features
- Luigi: class-heavy, requires pip install, no human gates

## Architecture Decision

### Stay With: Bash/Python FSM + YAML Stage Contracts

The existing architecture is already more capable than any lightweight alternative.
The 20-stage contract model with checkpoint persistence, human gates, and audit
trail is production-grade for this use case.

### Add: Three Targeted Enhancements

#### Enhancement 1: Event-Sourced Run Log (~50 LOC)

```
# On stage completion, append to run log:
.claude/work-queue/assets/WRK-NNN/run-log.jsonl

{"stage":10,"status":"done","ts":"2026-03-15T...","entry_hash":"abc123"}

# On resume: read run-log.jsonl, skip stages already marked done
```

Integrates into `exit_stage.py` — one JSONL append per stage exit.
On `start_stage.py` resume — read log, skip completed stages.

#### Enhancement 2: Transition Table Generator (~80 LOC)

```python
# scripts/work-queue/generate-transition-table.py
# Reads stages/stage-NN-*.yaml → produces transitions.yaml
#
# transitions:
#   - from: 4   to: 5   guard: "exit_artifacts exist"  rollback_to: 4
#   - from: 5   to: 6   guard: "human_gate passed"     rollback_to: 4
#   - from: 7   to: 8   guard: "human_gate passed"     rollback_to: 4
```

Makes implicit linear ordering explicit. Enables formal rollback.
Validates no stage can be skipped without passing guards.

#### Enhancement 3: Content-Addressed Stage Skipping (~60 LOC)

```bash
# At stage entry: hash entry_reads files
HASH=$(sha256sum $ENTRY_FILES | sha256sum | cut -d' ' -f1)
# Compare to previous run's hash in run-log.jsonl
# If match + stage completed → skip
```

Avoids re-executing expensive stages (TDD, cross-review) when
inputs haven't changed. Integrates with Enhancement 1's run log.

### Codify: 5 Prose Workflows as L2 Scripts

Each workflow gets a YAML definition + bash/Python executor:

| Workflow | Entry Script | Stages |
|----------|-------------|--------|
| Dark intelligence extraction | `scripts/workflows/dark-intel-extract.sh` | scan→parse→validate→emit-tests |
| Research-literature gathering | `scripts/workflows/research-gather.sh` | fetch→summarize→extract-actions→capture-wrk |
| Calculation implementation | `scripts/workflows/calc-implement.sh` | tdd-red→implement→tdd-green→calc-report→commit |
| Data source ingestion | `scripts/workflows/data-ingest.sh` | loader→schema→tests→commit |
| Phase B doc extraction | `scripts/workflows/doc-extract.sh` | index→extract→classify→ledger→capmap |

Each follows the same pattern as the WRK stage queue:
- YAML workflow definition (stages, gates, artifacts)
- Bash executor reads YAML, runs stages sequentially
- Checkpoint persistence (resume on crash)
- Audit trail (append to run-log.jsonl)

## Decomposition into Child WRKs

This Feature WRK should decompose into:

| Child | Scope | Blocked By |
|-------|-------|------------|
| **A**: Run-log crash recovery | Enhancement 1: JSONL run log + exit_stage.py integration | — |
| **B**: Transition table generator | Enhancement 2: generate-transition-table.py + validation | — |
| **C**: Content-addressed skipping | Enhancement 3: hash-based skip in start_stage.py | A |
| **D**: Workflow executor framework | Generic YAML-driven workflow runner (shared infra for E) | A |
| **E**: Codify 5 workflows | Create YAML definitions + test for each workflow | D |

## What NOT to Build

- No external dependencies (no pytransitions, no Luigi, no Taskfile)
- No DAG execution engine (pipelines are linear; parallelism at feature-children level)
- No Python decorator frameworks (Prefect-style) — script-per-stage is more auditable
- No database (SQLite/Redis) — YAML/JSONL files are sufficient for this scale
- No web UI — HTML reports + terminal output are sufficient

## Sources

- Temporal vs Prefect comparison (codilime.com/blog)
- Kestra vs Temporal vs Prefect 2025 Guide (procycons.com)
- pytransitions/transitions on GitHub (5k+ stars)
- Taskfile: Modern Alternative to Makefile (marmelab.com)
- Dagger.io Programmable Workflows (docs.dagger.io)
- Build a Crash-Proof Pipeline in ~150 Lines of Bash (earezki.com)
- Workflow Engine vs State Machine (workflowengine.io/blog)
