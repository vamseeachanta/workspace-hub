# Migration Guide: Single-Provider to Multi-Provider Orchestration

## Overview
This guide assists users in migrating from the legacy single-provider (Claude-only) workflow to the new Multi-Provider Orchestration System.

## Comparison

| Feature | Legacy (Phase 1) | Multi-Provider (Phase 4) |
| :--- | :--- | :--- |
| **Providers** | Claude Only | Gemini, Claude, Codex |
| **Routing** | Static | Intelligent (Task Classification) |
| **Cost Control** | Manual | Automated Budget Guardrails |
| **Execution** | Sequential | Parallel (Batch Runner) |
| **Feedback** | None | Adaptive Learning |

## Migration Steps

### 1. Verify Credentials
Ensure you have API access enabled for all three providers. The system assumes environment variables or CLI tools are configured:
- `gemini` CLI
- `claude` CLI
- `openai` / `codex` CLI

### 2. Configure Budgets
Review the default budgets in `config/`:
- `config/gemini_usage.json` (Default: $50/day)
- `config/claude_usage.json` (Default: $100/day)
- `config/codex_usage.json` (Default: $100/day)

Adjust these values according to your project's financial constraints.

### 3. Update Workflows

**Legacy Command:**
```bash
./scripts/monitoring/suggest_model.sh <repo> "Task"
```

**New Command:**
```bash
./scripts/routing/orchestrate.sh "Task"
```

### 4. Batch Processing
If you have scripts that loop through tasks sequentially, migrate them to use the Batch Runner for 3x performance gains.

**Legacy Loop:**
```bash
for task in "${tasks[@]}"; do
  ./do_task.sh "$task"
done
```

**New Batch:**
```bash
echo "${tasks_json}" | ./scripts/batchtools/batch_runner.sh --parallel 5
```

## Rollback Plan
If you encounter issues, the legacy scripts in `scripts/monitoring/` remain fully functional. You can switch back at any time.
