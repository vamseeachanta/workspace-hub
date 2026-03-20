# Extending the Permission Model

> Context: WRK-1119 replaced `--dangerouslySkipPermissions` with a declarative
> allow/deny list in `.claude/settings.json`.  This doc explains how to maintain it.

## Where permissions live

| File | Scope | Purpose |
|------|-------|---------|
| `.claude/settings.json` `.permissions.allow` | Project (repo-level, version-controlled) | Patterns that are pre-approved and need no prompt |
| `.claude/settings.json` `.permissions.deny` | Project | Patterns that are always blocked |
| `~/.claude/settings.json` | User (per machine) | Model choice, status line — **no bypass flags** |

Do **not** add `"skipDangerousModePermissionPrompt": true` back to `~/.claude/settings.json`.
That flag defeats the entire model.

## Pattern syntax

Patterns follow the `Bash(<prefix>:*)` format:

```
Bash(ls:*)           — matches any ls command
Bash(git diff:*)     — matches "git diff ..." but NOT "git status"
Bash(./scripts/*:*)  — matches any script under ./scripts/
```

Wildcards (`*`) are suffix-only. The colon before `*` is literal.

## How to add a new allow pattern

1. Confirm the command is genuinely needed and safe for unattended execution.
2. Pick the narrowest prefix that covers the use case.
3. Add it to the `"allow"` array in `.claude/settings.json`.
4. Run the TDD suite to catch duplicates or structural errors:

```bash
uv run --no-project python -m pytest tests/unit/test_permissions_model.py -v
```

5. Commit the change with a `chore(permissions):` commit message.

## How to add a new deny pattern

1. Identify the dangerous prefix (e.g., `rm -rf /`).
2. Add it to the `"deny"` array **before** any matching allow pattern (deny wins on conflict).
3. Run the TDD suite.
4. Commit with `fix(permissions):` or `security(permissions):`.

## Deny takes precedence

When a command matches both allow and deny, **deny wins**.
Example: `Bash(rm:*)` is allowed, but `Bash(rm -rf /)` is denied — the denied pattern
is more specific and will block that exact command.

## Audit-driven updates

To derive missing patterns from session history:

```bash
uv run --no-project python scripts/work-queue/audit-session-permissions.py --threshold 5
```

This produces a candidate list of patterns seen in session JSONLs with frequency above
the threshold.  Review `merged-audit.yaml` in the WRK-1119 assets for the initial run.

## Known limitations

- The bypass flag (`skipDangerousModePermissionPrompt`) in user settings overrides the
  entire deny list.  **Never set this on production workstations.**
- `licensed-win-1` (Windows) needs a separate validation pass; see WRK-1119 AC6.
- Tool calls other than `Bash` (e.g., `Write`, `Edit`) are governed by hook matchers,
  not the `allow`/`deny` lists.
