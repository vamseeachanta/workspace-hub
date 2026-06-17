# Workflow Templates

> Context-efficient workflow definitions for hierarchical agent coordination

## Overview

These YAML workflow templates define patterns for:
- Multi-repository operations with parallel workers
- Summary-only returns to minimize context usage
- Checkpoint creation for state persistence
- Aggregation of worker results

## Available Workflows

| Workflow | Purpose | Parallel | Output |
|----------|---------|----------|--------|
| `pytest-validation.yaml` | Multi-repo pytest validation | Yes (5) | Summary + Checkpoint |
| `aggregation.yaml` | Worker result aggregation patterns | No | Aggregated JSON |
| `checkpoint.yaml` | Summarization checkpoint creation | No | Markdown checkpoint |

## Usage

### With Batch Runner

```bash
# Execute workflow with parallel workers
./scripts/batchtools/batch_runner.sh \
  --parallel 5 \
  --output-format summary \
  < .claude/workflows/pytest-validation.yaml
```

### Manual Workflow Execution

```bash
# Step 1: Run workers
for repo in digitalmodel energy worldenergydata; do
  ./scripts/routing/orchestrate.sh "pytest --collect-only in $repo" &
done
wait

# Step 2: Aggregate results
python .claude/tools/context_manager.py aggregate \
  --input .claude/state/agent_results/*.json \
  --output .claude/state/aggregated_state.json

# Step 3: Create checkpoint
python .claude/tools/context_manager.py checkpoint pytest-validation
```

## Workflow Structure

```yaml
metadata:
  name: workflow-name
  version: 1.0.0
  description: What this workflow does

config:
  parallel_workers: 5
  output_format: summary
  results_dir: .claude/state/agent_results

steps:
  - name: step-name
    agent: agent-type
    description: What this step does
    parallel: true|false
    command: |
      command to execute
    output_file: path/to/output.json
```

## Worker Response Contract

All workers return summary-only responses:

```json
{
  "worker_id": "worker-1",
  "status": "complete|failed|blocked",
  "summary": "Max 300 chars...",
  "output_file": "path/to/full/output.json",
  "next_action": "Max 150 chars...",
  "key_metrics": {
    "metric_name": "value"
  }
}
```

## Integration Points

- **Batch Runner**: `scripts/batchtools/batch_runner.sh`
- **Orchestrator**: `scripts/routing/orchestrate.sh`
- **Context Manager**: `.claude/tools/context_manager.py`
- **Agent Results**: `.claude/state/agent_results/`
- **Checkpoints**: `.claude/checkpoints/`

## Context Management

Workflows integrate with %ctx tracking:

| %ctx | Action |
|------|--------|
| 0-40% | Normal operation |
| 40-60% | Consider checkpoint |
| 60-80% | Create checkpoint, archive older exchanges |
| 80-100% | Trim to essentials |

## Gate-chain templates (#3191)

Three **provider-neutral** templates encode the mandatory gate chain as data (so Claude/Codex/Gemini/Hermes follow the same gates). They carry `kind: gated-workflow` and are validated against `schema/workflow.schema.json` by `tests/workflow/test_gated_workflow_templates.py` (run: `uv run --group dev pytest tests/workflow/`). They are **Level-0/1 data, NOT enforcement** — enforcement lives in `scripts/workflow/plan_approval_gate_check.py` and `.github/workflows/completeness-gate.yml`.

- `issue-gate-chain.yaml` — full lifecycle (issue → plan → USER approves → implement(TDD) → cross-review → close); per-tier review depth (T1=1/T2=2/T3=3 providers); `user_approval` is `USER_ONLY` + `self_approve: forbidden`.
- `tdd-implementation.yaml` — test-first → implement → refactor → review → close; opt-in completeness gate.
- `cross-provider-review-workflow.yaml` — encodes `scripts/review/plan-review-fanout.sh` (default Claude+Codex+Gemini, `on_provider_unavailable: continue_and_record`).

## Choosing a workflow template

| Use case | Template | Schema |
|---|---|---|
| Issue lifecycle / approval gate chain | **`issue-gate-chain.yaml`** | gated-workflow |
| TDD implementation (new work) | **`tdd-implementation.yaml`** | gated-workflow |
| Cross-provider adversarial review | **`cross-provider-review-workflow.yaml`** | gated-workflow |
| Multi-repo pytest validation | `pytest-validation.yaml` | legacy `metadata/config/steps` |
| Hierarchical result aggregation | `aggregation.yaml` | legacy `metadata/config/steps` |
| Context-overflow checkpointing | `checkpoint.yaml` | legacy `metadata/config/steps` |
| Standard TDD phases (**deprecated** — Claude-only, no gates) | `standard-development.yaml` → use `tdd-implementation.yaml` | legacy `name/phases` |
| Data analysis (**deprecated** — Claude-only, no gates) | `data-analysis.yaml` | legacy `name/phases` |

Only `kind: gated-workflow` files are validated by `schema/workflow.schema.json`; the two legacy dialects are out of its scope by construction.

## Related Documentation

- Context Management Skill: `~/.claude/skills/context-management/SKILL.md`
- CLAUDE.md Directives: `.claude/CLAUDE.md`
- Batch Runner: `scripts/batchtools/batch_runner.sh`
- Gate chain source: `AGENTS.md` / `config/agents/SHARED_SOUL.md` (Hard Gates); review fan-out: `scripts/review/plan-review-fanout.sh`
