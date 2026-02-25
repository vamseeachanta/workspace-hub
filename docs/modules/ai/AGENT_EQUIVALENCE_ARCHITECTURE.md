# Agent Equivalence Architecture

## Goal
Provide workflow-equivalent behavior across Claude Code, Codex CLI, and Gemini CLI while preserving existing Claude process as source-of-truth.

## Session Rule
The provider where the session starts is the **orchestrator**. Other providers are **subagents** for that session.

- Orchestrator: can delegate and transition stages.
- Subagents: execute delegated stages; cannot alter orchestration state.

## Source of Truth
- Work lifecycle: `.claude/work-queue/process.md`
- Work items: `.claude/work-queue/*/WRK-*.md`
- Behavior contract: `config/agents/behavior-contract.yaml`
- Session state: `.claude/work-queue/session-state.yaml`

## Wrappers
- `scripts/agents/session.sh` - initialize/show orchestrator lock.
- `scripts/agents/work.sh` - provider-neutral work wrapper.
- `scripts/agents/plan.sh` - plan gate wrapper.
- `scripts/agents/execute.sh` - implementation gate wrapper.
- `scripts/agents/review.sh` - review stage wrapper.

## Providers
- `scripts/agents/providers/claude.sh`
- `scripts/agents/providers/codex.sh`
- `scripts/agents/providers/gemini.sh`

## Review Normalization
Use `scripts/review/normalize-verdicts.sh` to map free-text review output to:
- `APPROVE`
- `MINOR`
- `MAJOR`
- `NO_OUTPUT`
- `ERROR`

## Quick Start
```bash
scripts/agents/session.sh init --provider claude
scripts/agents/plan.sh --provider claude WRK-NNN
scripts/agents/execute.sh --provider claude WRK-NNN
scripts/agents/review.sh WRK-NNN --all-providers
scripts/agents/report-equivalence.sh
```
