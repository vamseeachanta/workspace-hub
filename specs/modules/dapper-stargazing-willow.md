# WRK-683 Plan HTML Review — Draft

> **WRK:** WRK-683 | **Route:** B | **Orchestrator:** claude | **Status:** DRAFT

---

## Summary

**Title:** arch(orchestrator): unify AI agent session logs in `logs/orchestrator/`

**Problem:** Claude, Codex, and Gemini write session logs to separate, agent-specific
home directories. No unified location exists for cross-orchestrator log reading or
cross-agent assessment.

**Key finding from config audit:**

| Agent | Native config | Log path configurable? | Write method |
|-------|--------------|----------------------|--------------|
| Claude | `.claude/settings.json` (hooks) | **Yes — hook system** | Update `session-logger.sh` to dual-write |
| Codex | `~/.codex/config.toml` | No log path setting | Capture via `submit-to-codex.sh` tee |
| Gemini | `~/.gemini/settings.json` | No log path setting | Capture via `submit-to-gemini.sh` tee |

**Approach:** Claude writes natively via updated hook. Codex and Gemini logs are
captured at invocation time by the submit wrapper scripts (already write results to
`scripts/review/results/`; add parallel tee to `logs/orchestrator/`).

---

## Proposed Log File Naming Convention

```
logs/orchestrator/
├── README.md                                   ← tracked; documents structure
├── claude/
│   └── session_YYYYMMDD.jsonl                  ← real-time, appended by hook per tool call
├── codex/
│   └── WRK-NNN-YYYYMMDD-HHMMSS.log            ← written by submit-to-codex.sh per invocation
└── gemini/
    └── WRK-NNN-YYYYMMDD-HHMMSS.log            ← written by submit-to-gemini.sh per invocation
```

Raw content is gitignored (`logs/` is already in `.gitignore`); `README.md` tracked
via negation rule.

---

## Deliverables

### 1. `logs/orchestrator/README.md` (CREATE — tracked)
Documents the directory structure, naming conventions, and write method for each agent.

### 2. `.gitignore` (EDIT — +2 lines)
```gitignore
!logs/orchestrator/
!logs/orchestrator/README.md
```

### 3. `.claude/hooks/session-logger.sh` (EDIT — dual-write for Claude)
After the existing write to `.claude/state/sessions/`, also append the same JSONL
line to `logs/orchestrator/claude/session_$(date +%Y%m%d).jsonl`:
```bash
# Dual-write: native sessions path + unified orchestrator log
mkdir -p "${REPO_ROOT}/logs/orchestrator/claude"
echo "${log_line}" >> "${REPO_ROOT}/logs/orchestrator/claude/session_$(date +%Y%m%d).jsonl"
```
Guard with `[[ -n "${REPO_ROOT}" ]] && ...` to ensure no error when run outside repo.

### 4. `scripts/review/submit-to-codex.sh` (EDIT — tee output)
After capturing the Codex response (already written to `scripts/review/results/`),
also tee to `logs/orchestrator/codex/`:
```bash
log_file="${REPO_ROOT}/logs/orchestrator/codex/WRK-${wrk_id}-$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "$(dirname "${log_file}")"
echo "${response}" >> "${log_file}"
```

### 5. `scripts/review/submit-to-gemini.sh` (EDIT — tee output)
Same pattern as submit-to-codex.sh:
```bash
log_file="${REPO_ROOT}/logs/orchestrator/gemini/WRK-${wrk_id}-$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "$(dirname "${log_file}")"
echo "${response}" >> "${log_file}"
```

### 6. `AGENTS.md` (EDIT — +1 policy line)
```
- **Peer logs**: `logs/orchestrator/<agent>/` — read peer session logs for cross-agent analysis
```

### 7. `.claude/docs/orchestrator-pattern.md` (EDIT — new section)
"Cross-Agent Log Access" section: paths, naming convention, when each file is written,
and that raw content is gitignored (local-machine only).

---

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `logs/orchestrator/README.md` | CREATE | ~20 |
| `.gitignore` | EDIT | +2 |
| `.claude/hooks/session-logger.sh` | EDIT | +3 |
| `scripts/review/submit-to-codex.sh` | EDIT | +4 |
| `scripts/review/submit-to-gemini.sh` | EDIT | +4 |
| `AGENTS.md` | EDIT | +1 |
| `.claude/docs/orchestrator-pattern.md` | EDIT | +10 |

---

## What Is NOT Changing

- `.claude/state/sessions/` remains primary Claude session store (dual-write adds a copy)
- `.claude/work-queue/logs/` WRK-stage logs unchanged
- `scripts/review/results/` existing Codex/Gemini output paths unchanged (tee adds a copy)
- Comprehensive-learning pipeline reads from existing paths (no change)
- No pull collector script (not needed with wrapper capture)

---

## Acceptance Criteria

- [ ] `logs/orchestrator/README.md` committed and documents the structure
- [ ] Claude tool calls append to `logs/orchestrator/claude/session_YYYYMMDD.jsonl`
- [ ] Running `cross-review.sh <file> codex` also writes to `logs/orchestrator/codex/`
- [ ] Running `cross-review.sh <file> gemini` also writes to `logs/orchestrator/gemini/`
- [ ] Any agent can read peer logs from `logs/orchestrator/<agent>/` for cross-session context
- [ ] Raw content is gitignored; `README.md` is tracked

---

## Risk / Trade-offs

| Risk | Mitigation |
|------|-----------|
| session-logger.sh write failure blocks tool call | Wrap in subshell: `( mkdir -p ... && echo ... >> ... ) 2>/dev/null \|\| true` |
| WRK-NNN not available in submit scripts | Use filename from input file argument; fallback to timestamp-only name |
| Large Claude JSONL grows unbounded | gitignored; same as existing `.claude/state/sessions/` (nightly cron truncates) |
| submit scripts don't expose `wrk_id` var | Extract from input filename using basename; or use timestamp-only log name |

---

*Cross-review input: submit this file to `scripts/review/cross-review.sh` for Codex/Gemini verdict*
