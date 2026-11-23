# Windows Claude Code Parity Hardening — Packages 1–3 Completion Pass

## Context

A prior session began cross-platform hardening for Claude Code hook scripts and settings to ensure they work on both Linux and Windows (Git Bash/MSYS2). Three packages were partially completed:

- **Package 1**: Managed template (`config/agents/claude/settings.json`) — populated with shared baseline settings
- **Package 2**: Hook scripts — replaced `python3` / `uv run` in executable code with portable `uv python find → python3 → python` fallback chain
- **Package 3**: Session lifecycle hooks — wired `session-logger.sh post` and `session-review.sh` in settings

This pass does narrow completion and cleanup only. No new files, no scope expansion.

## Changes Required

### Package 3 — Wire `session-logger.sh pre` (1 edit)

**Problem**: `session-logger.sh` accepts `$1` (defaults to `"pre"` on line 14) and is designed to log both pre- and post-tool events. Only `post` is wired (PostToolUse, line 146-154). The `pre` variant is not wired in PreToolUse.

**Fix**: Add a new entry at the END of the PreToolUse array in `.claude/settings.json` (after the `gsd-validate-commit.sh` block ending at line 102):

```json
,
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

**Rationale**: Same broad matcher and timeout as the `post` counterpart. Placed last in PreToolUse so all enforcement hooks (governor, guards, gates) run first — the logger is telemetry, not enforcement.

### Package 2 — No changes needed (assessment only)

Remaining `python3|uv run` grep hits in the 3 hook scripts:

| File | Line | Content | Classification |
|------|------|---------|---------------|
| `session-governor-check.sh` | 27 | Comment: `# Resolve Python interpreter portably (uv python find → python3 → python)` | **Benign** — documents the pattern |
| `session-governor-check.sh` | 29 | `command -v python3 2>/dev/null` in fallback chain | **Correct** — this IS the portable pattern |
| `session-governor-check.sh` | 79 | `"Run: uv run scripts/workflow/session_governor.py ..."` in JSON error output | **Benign** — user-facing diagnostic hint, not executable |
| `session-governor-check.sh` | 83 | Same pattern as line 79 | **Benign** — user-facing diagnostic hint |
| `cross-review-gate.sh` | 11 | Comment: same portable pattern documentation | **Benign** |
| `cross-review-gate.sh` | 13 | `command -v python3 2>/dev/null` in fallback chain | **Correct** |
| `skill-content-pretooluse.sh` | — | No matches | **Clean** — all `python3` calls already replaced with `jq` |

**Verdict**: All remaining hits are either (a) the correct cross-platform fallback chain that was the *goal* of Package 2, or (b) human-readable diagnostic messages. No changes required.

### Package 1 — No changes needed (assessment only)

The managed template (`config/agents/claude/settings.json`) now contains:

| Setting | Safe for shared template? | Notes |
|---------|--------------------------|-------|
| `$schema` | Yes | Standard |
| `skipDangerousModePermissionPrompt: true` | Pre-existing | Was already in file before this diff |
| `cleanupPeriodDays: 90` | Yes | Reasonable default |
| `env` (MAX_TEAMMATES, REVIEW_GATE_STRICT) | Yes | Governance defaults |
| `permissions.defaultMode: auto` | Yes | Can be locally overridden |
| `plansDirectory: .planning` | Yes | Repo convention |
| `showThinkingSummaries: true` | Yes | Harmless preference |
| `outputStyle: Explanatory` | Yes | Locally overridable preference |
| `effortLevel: high` | Yes | Locally overridable preference |
| `worktree` config | Yes | Standard symlink targets |
| `spinnerVerbs` | Yes | Cosmetic, append mode |
| `deny` list (28 patterns) | Yes | Security hardening — core shared value |
| `statusLine` | Yes | Uses `${WORKSPACE_HUB}` relative path |

**Verdict**: Template is conservative. Key observations:
- **No hooks** — correct, hooks are repo-local and machine-specific
- **No plugins** — correct, plugin selection is a local choice
- **No spinnerTipsOverride** — correct, tips reference local scripts
- The `deny` list is the most important shared element (security baseline)
- `skipDangerousModePermissionPrompt` was pre-existing, not introduced by this parity work

## Files Modified

Only **1 file** needs editing:
- `.claude/settings.json` — add `session-logger.sh pre` to PreToolUse

All other 6 files are confirmed correct as-is.

## Verification Plan

After the edit, run:

```bash
# 1. JSON validity
jq empty config/agents/claude/settings.json
jq empty .claude/settings.json

# 2. Shell syntax checks
bash -n .claude/hooks/skill-content-pretooluse.sh
bash -n .claude/hooks/session-governor-check.sh
bash -n .claude/hooks/cross-review-gate.sh
bash -n .claude/hooks/session-logger.sh
bash -n .claude/hooks/session-review.sh

# 3. Confirm no remaining executable python3/uv run in code paths
grep -nE 'python3|uv run' .claude/hooks/skill-content-pretooluse.sh \
  .claude/hooks/session-governor-check.sh .claude/hooks/cross-review-gate.sh || true

# 4. Confirm session hooks are wired correctly
python3 - <<'PY'
import json, pathlib
cfg = json.loads(pathlib.Path('.claude/settings.json').read_text())
cmds = []
for blocks in cfg.get('hooks', {}).values():
    for block in blocks:
        for hook in block.get('hooks', []):
            cmds.append(hook.get('command', ''))
print('session-logger pre:', any('session-logger.sh pre' in c for c in cmds))
print('session-logger post:', any('session-logger.sh post' in c for c in cmds))
print('session-review:', any('session-review.sh' in c for c in cmds))
PY

# 5. Confirm no files outside allowed set were modified
git diff --name-only
git status --short -- config/agents/claude/settings.json .claude/settings.json \
  .claude/hooks/skill-content-pretooluse.sh .claude/hooks/session-governor-check.sh \
  .claude/hooks/cross-review-gate.sh .claude/hooks/session-logger.sh .claude/hooks/session-review.sh
```

Expected results:
- All `jq empty` / `bash -n` pass silently
- `session-logger pre: True`, `session-logger post: True`, `session-review: True`
- No new files in diff outside the 7 allowed files
- Do NOT commit
