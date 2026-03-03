# Orchestrator Log Directory

Unified log location for all AI agent session activity.

## Structure

```
logs/orchestrator/
├── README.md                               ← tracked; documents structure
├── claude/
│   └── session_YYYYMMDD.jsonl             ← real-time, per tool-call (hook)
├── codex/
│   └── WRK-NNN-YYYYMMDDTHHMMSSZ.log      ← per invocation (submit-to-codex.sh)
└── gemini/
    └── WRK-NNN-YYYYMMDDTHHMMSSZ.log      ← per invocation (submit-to-gemini.sh)
```

## Write Method

| Agent  | Written by            | Frequency      | Format |
|--------|-----------------------|----------------|--------|
| Claude | `session-logger.sh`   | Per tool call  | JSONL  |
| Codex  | `submit-to-codex.sh`  | Per invocation | text   |
| Gemini | `submit-to-gemini.sh` | Per invocation | text   |

## Native Session Stores (per-agent, outside repo)

Each AI CLI also maintains its own native session store. These are the primary source
for all AI activity (not just cross-reviews):

| Agent  | Native path                                              | Format | Notes |
|--------|----------------------------------------------------------|--------|-------|
| Claude | `logs/orchestrator/claude/` (this repo, hook-written)    | JSONL  | Dual-write with `.claude/state/sessions/` |
| Codex  | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`           | JSONL  | All Codex CLI invocations |
| Gemini | `~/.gemini/tmp/<project>/chats/session-*.json`           | JSON   | All Gemini CLI sessions for this project |

`logs/orchestrator/codex/` and `logs/orchestrator/gemini/` only contain cross-review
invocations (written by `submit-to-codex.sh` / `submit-to-gemini.sh`).

## Notes

- Raw content is **gitignored** (`logs/` excluded); this README is tracked via negation rule
- Claude JSONL mirrors `.claude/state/sessions/` (dual-write; same format)
- Codex/Gemini orchestrator logs mirror `scripts/review/results/` output (tee; same content)
- Local-machine only — not synced across machines
- Any agent can read peer logs from `logs/orchestrator/<agent>/` for cross-session context

## Per-Machine Analysis Flow

Each machine runs `comprehensive-learning` locally against its own `logs/orchestrator/`:

1. **Phase 1** reads `logs/orchestrator/<agent>/` for raw tool-call and review data
2. **Phases 1–9** produce derived state: `session-signals/`, `candidates/`, `skill-scores.yaml`
3. **Commit step** pushes derived state to git (hooks bypassed: `git -c core.hooksPath=/dev/null`)
4. **ace-linux-1 Phase 10a** runs `git pull` to aggregate all machines, writes compilation report

Raw logs in `logs/orchestrator/` are local-only (gitignored). Only derived state crosses machines.
