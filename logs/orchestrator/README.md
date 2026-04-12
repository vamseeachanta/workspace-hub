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
├── hermes/
│   ├── session_YYYYMMDD.jsonl             ← exported from native Hermes sessions
│   ├── corrections/session_YYYYMMDD.jsonl ← Hermes self-correction sessions
│   └── skill-patches.jsonl                ← Hermes skill patch log (unique to Hermes)
└── gemini/
    └── WRK-NNN-YYYYMMDDTHHMMSSZ.log      ← per invocation (submit-to-gemini.sh)
```

## Write Method

| Agent  | Written by            | Frequency      | Format |
|--------|-----------------------|----------------|--------|
| Claude | `session-logger.sh`   | Per tool call  | JSONL  |
| Codex  | `submit-to-codex.sh`  | Per invocation | text   |
| Hermes | export script (below) | Per export run | JSONL  |
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
4. **dev-primary Phase 10a** runs `git pull` to aggregate all machines, writes compilation report

Raw logs in `logs/orchestrator/` are local-only (gitignored). Only derived state crosses machines.

## Provider session ecosystem audit

Use the provider-wide audit below to compare Claude/Codex/Hermes/Gemini session artifacts against the current checkout and catch workflow drift after refactors:

```bash
uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py --stdout
```

Native provider sessions should be exported with:

```bash
bash scripts/cron/hermes-session-export.sh
bash scripts/cron/codex-session-export.sh
bash scripts/cron/gemini-session-export.sh
```

**Important: run exports BEFORE the audit.** The audit reads `session_*.jsonl` files
in each provider directory. If exports haven't run recently, the audit produces stale
results. The recommended sequence is: export all providers → run audit → commit outputs.

Exporter state files:
- Hermes: `logs/orchestrator/hermes/.last-export-ts`
- Codex: `logs/orchestrator/codex/.export-state.json` (per-tool-call dedupe for mutable rollout files)
- Gemini: `logs/orchestrator/gemini/.export-state.json` (per-tool-call dedupe for mutable native sessions)

Canonical tracked outputs:
- `analysis/provider-session-ecosystem-audit.json`
- `docs/reports/provider-session-ecosystem-audit.md`

Scheduled refresh:
- task id: `provider-session-ecosystem-audit`
- wrapper: `scripts/cron/provider-session-ecosystem-audit.sh`
- log: `logs/quality/provider-session-ecosystem-audit-*.log`

This report surfaces:
- provider-by-provider session volume and tool mix
- hottest missing repo-local reads and symbolic skill/tool reads
- bare `python3` usage inside Bash calls vs `uv run ... python`
- cross-provider observability gaps (for example, missing `session_*.jsonl` inputs)

Input expectations:
- Claude: `logs/orchestrator/claude/session_*.jsonl`
- Codex: `logs/orchestrator/codex/session_*.jsonl` (exported from native Codex sessions)
- Hermes: `logs/orchestrator/hermes/session_*.jsonl`
- Gemini: `logs/orchestrator/gemini/session_*.jsonl` once Gemini export is enabled; cross-review `.log` files alone are not enough for parity analysis
