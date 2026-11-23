# Multi-Provider AI Orchestration System

This system intelligently routes tasks to the best AI provider (Google Gemini, Claude 3.5 Max, OpenAI Codex) based on task type, cost, and availability.

## Quick Start

### Single Task Execution
```bash
./scripts/routing/orchestrate.sh "Your task description here"
```
*Example:*
```bash
./scripts/routing/orchestrate.sh "Design a distributed system architecture"
# -> Recommendation: Claude
```

### Batch Execution (Parallel)
```bash
# Create a JSON list of tasks
echo '["Task 1", "Task 2"]' > tasks.json

# Run with 5 parallel workers
./scripts/batchtools/batch_runner.sh --parallel 5 < tasks.json
```

## Configuration

Provider profiles and usage tracking are located in `/config/`:
- `*_profile.json`: Defines capabilities, rates, and keywords.
- `*_usage.json`: Tracks daily usage and budget.

## Features

1.  **Intelligent Routing:** Classifies tasks using keyword analysis (e.g., "design" -> Claude, "analyze" -> Gemini).
2.  **Cost Optimization:** Estimates costs and enforces daily budgets.
3.  **Hard & Soft Blocking:** Automatically filters providers that hit rate limits.
4.  **Audit Trail:** Logs all decisions to `scripts/routing/logs/provider_recommendations.jsonl`.
5.  **Feedback Loop:** Collects user ratings to improve future selection.

## Advanced Usage

### Budget Guardrails
If a task's estimated cost exceeds the remaining daily budget, the system will trigger a **ROLLBACK** and prevent execution. Increase the `daily_budget` in `config/<provider>_usage.json` to resolve.

### Providing Feedback
To help the system learn:
```bash
./scripts/routing/feedback.sh <timestamp> <rating_1-5> "Comment"
```
Then run `./scripts/routing/optimize_weights.sh` to see suggestions.
