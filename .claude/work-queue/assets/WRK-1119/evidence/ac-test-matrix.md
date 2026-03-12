# AC Test Matrix — WRK-1119

| AC | Description | Status | Evidence |
|----|-------------|--------|---------|
| AC1 | Audit script derives allow list from session JSONLs | PASS | `merged-audit.yaml` (193 suggested patterns, 17 already covered) |
| AC2 | `.claude/settings.json` committed with allow/deny | PASS | commit `cf0a4b33`; 118 allow, 13 deny |
| AC3 | `--dangerouslySkipPermissions` removed on ace-linux-1 | PENDING | Requires fresh session without bypass; see validation plan below |
| AC4 | Deny list covers minimum dangerous patterns | PASS | `test_required_deny_pattern_present` (6 parametrized PASS) |
| AC5 | Docs explain how to extend allow list | PASS | `.claude/docs/permissions-extend.md` |
| AC6 | Validated: ace-linux-1 ✓ + acma-ansys05 ✓ | PENDING | Requires user action (see below) |
| AC7 | ≥3 TDD tests for deny-list and allow-list | PASS | 23 tests PASS — `tests/unit/test_permissions_model.py` |

## AC3/AC6 Validation Plan

Before WRK-1119 can close, the user must:

1. **Remove bypass from user settings:**
   ```bash
   # Edit ~/.claude/settings.json and remove:
   #   "skipDangerousModePermissionPrompt": true
   ```

2. **Start a fresh Claude Code session** on ace-linux-1 (no `--dangerouslySkipPermissions` flag).

3. **Confirm normal operations work** without permission prompts (git, uv, bash scripts).

4. **Repeat on acma-ansys05** (Windows): validate that the repo's `.claude/settings.json`
   allow list covers the commands used there.

5. **Report back** to complete Stage 17 (user-review-close.yaml).

## Test Run

```
tests/unit/test_permissions_model.py — 23 passed in 0.19s
```
