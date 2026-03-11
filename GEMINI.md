# Gemini Harness Adapter

All WRK execution must go through wrapper scripts:
- `scripts/agents/session.sh` — session init/close
- `scripts/agents/work.sh` — /work run routing
- `scripts/agents/plan.sh` — plan draft/review
- `scripts/agents/execute.sh` — implementation
- `scripts/agents/review.sh` — cross-review

Direct provider API calls bypass gate logging. Use wrappers.

See `.claude/docs/orchestrator-gate-contract.md` for the full gate contract.
Gate evidence required: `verify-gate-evidence.py WRK-NNN` must PASS before claim/close.
