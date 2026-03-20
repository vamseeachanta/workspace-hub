---
name: file-taxonomy-native-session-stores-gitignored-local-to-each-mac
description: "Sub-skill of file-taxonomy: Native Session Stores (gitignored \u2014\
  \ local to each machine) (+5)."
version: 1.6.0
category: workspace
type: reference
scripts_exempt: true
---

# Native Session Stores (gitignored — local to each machine) (+5)

## Native Session Stores (gitignored — local to each machine)


| Agent | Path | Format | Notes |
|-------|------|--------|-------|
| Claude | `~/.claude/projects/<encoded-path>/*.jsonl` | JSONL | Full session transcripts; managed by Claude CLI |
| Codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | JSONL | ~302 sessions on dev-primary (2026-03-03) |
| Gemini | `~/.gemini/tmp/<project>/chats/session-*.json` | JSON | ~772 sessions on dev-primary (2026-03-03) |

`<encoded-path>` = repo path with `/` replaced by `-` (e.g. `-mnt-local-analysis-workspace-hub`).


## Orchestrator Logs (`logs/orchestrator/` — gitignored per-machine)


Written by hooks and cross-review scripts; **not** native session transcripts.

| Path | Written by | Format |
|------|-----------|--------|
| `logs/orchestrator/claude/session_YYYYMMDD.jsonl` | Claude pre-tool/post-tool hooks | JSONL |
| `logs/orchestrator/codex/*.log` | `scripts/review/submit-to-codex.sh` | text |
| `logs/orchestrator/gemini/*.log` | `scripts/review/submit-to-gemini.sh` | text |

Structure: `logs/orchestrator/{claude,codex,gemini}/` — one dir per agent.


## Derived State (git-tracked — crosses machines via commit)


| Path | Written by | Format |
|------|-----------|--------|
| `.claude/state/session-signals/*.jsonl` | session-end hook | JSONL |
| `.claude/state/session-analysis/` | comprehensive-learning Phases 1–9 | Markdown |
| `.claude/state/session-analysis/compilation-YYYYMMDD.md` | Phase 10a (dev-primary only) | Markdown |
| `.claude/state/skill-scores.yaml` | comprehensive-learning Phase 7 | YAML |
| `.claude/state/candidates/` | comprehensive-learning Phase 6 | YAML |
| `scripts/review/results/` | `submit-to-{codex,gemini}.sh` | text |


## Key Distinction


```
native stores   → raw AI session transcripts (local machine only, gitignored)
orchestrator/   → cross-review invocation logs (sparse — only on cross-review runs)
derived state   → processed analysis output (git-tracked, crosses machines)
```


## Verbose Output Setting — Does NOT Affect Logs


**Verified 2026-03-08 (live test):**

- `--verbose` / "Verbose Output" in the Claude Code config dialog is a **terminal display flag only** — it controls what you see in the terminal, not what gets written to logs.
- There is **no `verbose` field in `settings.json`**; the setting is CLI-only and not persisted.
- `logs/orchestrator/claude/session_YYYYMMDD.jsonl` is written by `session-logger.sh` hook (pre/post every tool call) — **completely independent of verbose**.
- `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` (~296K per session) is written by codex CLI itself — also independent of Claude Code verbose.
- **Comprehensive-learning signal quality is unaffected by verbose=false.**

Test method: ran `scripts/review/submit-to-codex.sh` before/after; codex session file count grew 3→4, Claude hook log grew 694→700 lines, both independent of verbose flag.


## licensed-win-1 (Windows)


Paths follow the same convention but under `%USERPROFILE%` / `C:\Users\<user>\`:
- Claude: `%USERPROFILE%\.claude\projects\<encoded-path>\*.jsonl`
- Codex: `%USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl`
- Gemini: `%USERPROFILE%\.gemini\tmp\<project>\chats\session-*.json`

Use Git Bash to apply Linux-style path patterns on licensed-win-1.
