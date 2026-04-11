# Windows Claude Code Parity Hardening — Packages 1–3 Completion Pass

## Context

This is a narrow completion pass for the Windows Claude Code parity hardening work (Packages 1–3 only). The prior session hardened several hooks for cross-platform portability (`uv python find` fallback chains, `#!/usr/bin/env bash`, etc.) but left three loose ends:

1. **Package 3 incomplete**: `session-logger.sh` is wired for PostToolUse but missing the PreToolUse wiring
2. **Grep hits remain**: `python3|uv run` matches in `session-governor-check.sh` and `cross-review-gate.sh` need disposition
3. **Managed template review**: `config/agents/claude/settings.json` may contain settings too aggressive for a shared baseline

## Changes

### 1. Complete Package 3 — Wire session-logger pre hook

**File**: `.claude/settings.json`

Add a PreToolUse entry for `session-logger.sh pre` with the same matcher used by the existing PostToolUse entry (`Bash|Read|Write|Edit|MultiEdit|Glob|Grep|Agent|Task`). Place it as the **last** PreToolUse entry to preserve existing hook ordering.

```json
{
  "matcher": "Bash|Read|Write|Edit|MultiEdit|Glob|Grep|Agent|Task",
  "hooks": [
    {
      "type": "command",
      "command": "bash .claude/hooks/session-logger.sh pre",
      "timeout": 5
    }
  ]
}
```

**Rationale**: `session-logger.sh` already accepts `$1` as `pre`/`post` (line 14: `HOOK_TYPE="${1:-pre}"`). The pre hook captures intent (what the agent is about to do), while the post hook captures completion. The pre hook also ensures the first-write session-params emission (lines 56–66) fires early in the session rather than only after the first tool completes.

### 2. Resolve remaining grep hits — ALL BENIGN

**session-governor-check.sh**:
- Line 28: `_UV_PY=$(uv python find 2>/dev/null) || _UV_PY=""` — This IS the portable pattern. `uv python find` returns an absolute Python path without launching `uv run`. Correct.
- Line 29: `command -v python3` — Fallback chain: `uv python find` → `python3` → `python`. On Windows without `python3` in PATH, it gracefully falls through. Correct.
- Lines 79, 83: `uv run scripts/workflow/session_governor.py` — These are inside `printf` format strings that produce **user-facing diagnostic messages**. They tell the human operator what manual command to run. They are NOT execution paths. Correct, leave as-is.

**cross-review-gate.sh**:
- Line 12: `_UV_PY=$(uv python find 2>/dev/null) || _UV_PY=""` — Same portable pattern. Correct.
- Line 13: `command -v python3` — Same fallback chain. Correct.

**Verdict**: No changes needed. All matches are either the portable `uv python find` resolution pattern, fallback chains, or user-facing messages.

### 3. Trim managed template

**File**: `config/agents/claude/settings.json`

**Remove** `"skipDangerousModePermissionPrompt": true` (line 3). This is a per-user safety override that disables the dangerous-mode confirmation prompt. It should not be in a shared repo baseline — each user/machine should opt into this individually.

Everything else in the template is appropriate for a shared baseline:
- `cleanupPeriodDays`, `env`, `permissions`, `plansDirectory` — repo policy
- `worktree`, `spinnerVerbs` — ergonomics
- `deny` list — safety baseline
- `statusLine` — provides a default; users override locally

## Files Modified (allowed set only)

| File | Change |
|------|--------|
| `.claude/settings.json` | Add PreToolUse session-logger.sh pre entry |
| `config/agents/claude/settings.json` | Remove `skipDangerousModePermissionPrompt` |

No changes to: `session-logger.sh`, `session-review.sh`, `skill-content-pretooluse.sh`, `session-governor-check.sh`, `cross-review-gate.sh`

## Verification

Run all of these and report pass/fail:

```bash
jq empty config/agents/claude/settings.json
bash -n .claude/hooks/skill-content-pretooluse.sh
bash -n .claude/hooks/session-governor-check.sh
bash -n .claude/hooks/cross-review-gate.sh
bash -n .claude/hooks/session-logger.sh
bash -n .claude/hooks/session-review.sh
grep -nE 'python3|uv run' .claude/hooks/skill-content-pretooluse.sh .claude/hooks/session-governor-check.sh .claude/hooks/cross-review-gate.sh || true
python3 - <<'PY'
import json, pathlib
cfg=json.loads(pathlib.Path('.claude/settings.json').read_text())
cmds=[]
for blocks in cfg.get('hooks', {}).values():
    for block in blocks:
        for hook in block.get('hooks', []):
            cmds.append(hook.get('command',''))
print('session-logger pre:', any('session-logger.sh pre' in c for c in cmds))
print('session-logger post:', any('session-logger.sh post' in c for c in cmds))
print('session-review:', any('session-review.sh' in c for c in cmds))
PY
git diff -- config/agents/claude/settings.json .claude/settings.json
git status --short -- config/agents/claude/settings.json .claude/settings.json .claude/hooks/*.sh
```

Expected post-edit results:
- All `jq empty` / `bash -n` pass
- `session-logger pre: True`
- `session-logger post: True`
- `session-review: True`
- grep hits are all benign (comments, fallbacks, user messages)
- No files outside allowed set modified
