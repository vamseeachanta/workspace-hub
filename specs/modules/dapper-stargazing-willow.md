# WRK-683 Plan: arch(orchestrator) — Unified AI Agent Session Logs

**Source WRK:** WRK-683
**Route:** B
**Created:** 2026-03-02

---

> **Plan HTML Review Draft** — WRK-683 | Route B | orchestrator=claude
> Submit to cross-review: `scripts/review/cross-review.sh specs/modules/dapper-stargazing-willow.md all`

---

## Context

AI agents (Claude, Codex, Gemini) each store their session logs in separate,
agent-specific home directories:
- Claude: `.claude/state/sessions/session_YYYYMMDD.jsonl` (hook-driven JSONL)
- Codex: `~/.codex/history.jsonl` + `~/.codex/log/codex-tui.log`
- Gemini: `~/.gemini/history/<date>/` (structured history dirs)

Per-WRK orchestrator events go to `.claude/work-queue/logs/WRK-{id}-{stage}.log`.

No unified readable location exists. For cross-orchestrator assessment (e.g., Claude
reviewing Codex's session log, or Gemini reading Claude's gate events), each agent
must know three different native paths. WRK-683 adds `logs/orchestrator/` as the
canonical, single-directory read target for all agent sessions.

**Note:** Codex and Gemini CLIs don't support configurable log output paths.
Implementation uses a pull-based **collector script** that copies from each agent's
native location into `logs/orchestrator/`. Claude's logs are collected the same way
for consistency.

---

## Implementation

### Phase 1 — Directory scaffold

Create stub README at `logs/orchestrator/README.md` to document the structure
(the `logs/` dir is git-ignored for raw content; the README gets a negation rule
so it IS tracked):

```
logs/orchestrator/
├── README.md             ← tracked (canonical doc)
├── claude/               ← gitignored; populated by collector
├── codex/                ← gitignored; populated by collector
└── gemini/               ← gitignored; populated by collector
```

Add to `.gitignore`:
```gitignore
# Allow orchestrator log README to be tracked
!logs/orchestrator/
!logs/orchestrator/README.md
```

### Phase 2 — Collector script

**New file:** `scripts/agents/collect-orchestrator-logs.sh` (~45 lines)

```bash
#!/usr/bin/env bash
# Collect latest session logs from each agent into logs/orchestrator/.
# Idempotent, non-blocking — all errors suppressed. Called at session init.
set -uo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
DEST="${REPO_ROOT}/logs/orchestrator"
mkdir -p "${DEST}/claude" "${DEST}/codex" "${DEST}/gemini"

# Claude — today's session JSONL
today="$(date -u +%Y%m%d)"
src="${REPO_ROOT}/.claude/state/sessions/session_${today}.jsonl"
[[ -f "${src}" ]] && cp "${src}" "${DEST}/claude/" 2>/dev/null || true

# Codex — history + TUI log
[[ -f ~/.codex/history.jsonl ]] && cp ~/.codex/history.jsonl "${DEST}/codex/" 2>/dev/null || true
[[ -f ~/.codex/log/codex-tui.log ]] && cp ~/.codex/log/codex-tui.log "${DEST}/codex/" 2>/dev/null || true

# Gemini — latest non-tmp history directory
latest_dir="$(ls -t ~/.gemini/history/ 2>/dev/null | grep -v '^tmp' | head -1)"
if [[ -n "${latest_dir}" ]]; then
    mkdir -p "${DEST}/gemini/${latest_dir}"
    cp -r ~/.gemini/history/${latest_dir}/. "${DEST}/gemini/${latest_dir}/" 2>/dev/null || true
fi
echo "logs/orchestrator/ refreshed (claude/codex/gemini)"
```

### Phase 3 — Wire into session.sh init

**File:** `scripts/agents/session.sh`

Find the `init)` case block (currently ends after quota snapshot calls). Add one
line after the quota calls:

```bash
# Refresh unified orchestrator log directory
bash "${WORKSPACE_ROOT}/scripts/agents/collect-orchestrator-logs.sh" 2>/dev/null || true
```

### Phase 4 — Documentation

**File:** `AGENTS.md` — add one policy line (currently 21 lines, under limit):
```
- **Peer logs**: `logs/orchestrator/<agent>/` — read peer session logs for cross-agent analysis
```

**File:** `.claude/docs/orchestrator-pattern.md` — add a "Cross-Agent Log Access" section:
- Document `logs/orchestrator/{claude,codex,gemini}/` paths
- Note that `collect-orchestrator-logs.sh` refreshes on each session init
- Note that raw content is gitignored (local-machine only)

---

## Files Changed

| File | Action | Notes |
|------|--------|-------|
| `logs/orchestrator/README.md` | CREATE | Tracked doc of directory structure |
| `.gitignore` | EDIT | 2 negation lines for logs/orchestrator/README.md |
| `scripts/agents/collect-orchestrator-logs.sh` | CREATE | Pull-based log collector (~45 lines) |
| `scripts/agents/session.sh` | EDIT | Wire collector into `init)` case |
| `AGENTS.md` | EDIT | Add peer logs policy line |
| `.claude/docs/orchestrator-pattern.md` | EDIT | Add cross-agent log access section |

---

## Verification

1. Run `bash scripts/agents/collect-orchestrator-logs.sh` — should produce
   `logs/orchestrator/{claude,codex,gemini}/` with copied files.
2. Run `scripts/agents/session.sh init --provider claude` — confirm collector
   runs and directories are populated.
3. Confirm `logs/orchestrator/README.md` is git-tracked; raw content is not.
4. Confirm other agents can `cat logs/orchestrator/codex/history.jsonl` to read
   Codex session context.
