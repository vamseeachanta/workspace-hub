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

## Notes

- Raw content is **gitignored** (`logs/` excluded); this README is tracked via negation rule
- Claude JSONL mirrors `.claude/state/sessions/` (dual-write; same format)
- Codex/Gemini logs mirror `scripts/review/results/` output (tee; same content)
- Local-machine only — not synced across machines
- Any agent can read peer logs from `logs/orchestrator/<agent>/` for cross-session context
