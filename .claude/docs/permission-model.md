# Permission Model

> Claude Code uses `.claude/settings.json` to define which shell commands are
> auto-approved and which are always blocked — enforcing least-privilege by default.

## 1. Overview

Claude Code can execute Bash commands on the host machine. Without any configuration
every Bash invocation requires explicit human approval. The permission model in
`.claude/settings.json` lets the team pre-approve the commands that are routine
workflow tools (git, uv, pytest, scripts/) while hard-blocking commands that should
never run autonomously (sudo, curl, force-push).

Key properties:

- The file is **checked into git** — every workstation clone gets the same allow/deny
  list automatically, without per-machine setup.
- **Deny takes absolute precedence** — a pattern in `deny` blocks a command even if
  the same command matches an `allow` pattern.
- Anything not matched by `allow` requires **interactive human approval** unless the
  user has enabled bypass mode in their personal `~/.claude/settings.json`.

## 2. How It Works

### Allow patterns

A command is auto-approved when it matches any entry in `permissions.allow`. Patterns
follow Claude Code's syntax:

| Pattern form | Matches |
|---|---|
| `Bash(cmd:*)` | `cmd` with any arguments |
| `Bash(cmd subcommand:*)` | multi-word prefix, e.g. `git push` |
| `Bash(./scripts/*:*)` | any script path matching the glob |
| `Bash(cmd)` | exact match — no arguments |

### Deny patterns

A command is unconditionally blocked when it matches any entry in `permissions.deny`.
Order within the list is irrelevant — deny always wins.

### Decision order

```
command issued
  ↓
matches deny?  → YES → blocked (no prompt)
  ↓ NO
matches allow? → YES → auto-approved
  ↓ NO
interactive prompt (user must approve in the terminal)
```

## 3. Where the Allow List Lives

| File | Scope | Committed? |
|---|---|---|
| `.claude/settings.json` | Whole workspace-hub | Yes — travels with the repo |
| `~/.claude/settings.json` | Per-user, per-machine | No — machine-local override |

**Bypass mode warning.** If `skipDangerousModePermissionPrompt: true` appears in
`~/.claude/settings.json`, Claude Code skips the interactive prompt for unmatched
commands. Remove that key to restore least-privilege behaviour:

```json
// ~/.claude/settings.json — remove this key to re-enable prompts
"skipDangerousModePermissionPrompt": true   // ← delete this line
```

## 4. Adding a New Allowed Command

1. Edit `.claude/settings.json` in the repo root.
2. Add the pattern to `permissions.allow`:

   ```json
   "Bash(your-command:*)"
   ```

3. Validate the JSON before committing:

   ```bash
   uv run --no-project python -c \
     "import json; json.load(open('.claude/settings.json')); print('valid')"
   ```

4. Commit the change so all machines pick it up on next `git pull`.

### Pattern reference

```
Bash(cmd:*)              — any invocation of cmd with any arguments
Bash(cmd subcommand:*)   — multi-word prefix (e.g. git push)
Bash(./scripts/*:*)      — any script under scripts/
Bash(cmd)                — exact match, no arguments allowed
```

## 5. Adding a New Deny Pattern

1. Edit `permissions.deny` in `.claude/settings.json`.
2. Deny takes precedence over allow, so position within the list is irrelevant.
3. Common deny patterns to consider:

   - Exact dangerous flags: `Bash(git push --force:*)`
   - Network exfiltration tools: `Bash(curl:*)`, `Bash(wget:*)`
   - Privilege escalation: `Bash(sudo:*)`
   - Eval-style execution: `Bash(eval:*)`, `Bash(python -c:*)`
   - Broad permission grants: `Bash(chmod 777:*)`

## 6. How the Allow List Was Built

The 118 allow patterns in `.claude/settings.json` were derived empirically, not by
guesswork:

1. `scripts/permissions/audit-bash-commands.py` scanned 603 session JSONL files from
   `~/.claude/projects/` — 511 from dev-primary, 92 from dev-secondary.
2. `scripts/permissions/merge-audit-results.py` merged both outputs and applied a
   threshold of **5 combined uses** — any command used fewer than 5 times across both
   machines was excluded.
3. The resulting 118 patterns cover every command that appears in normal workflow:
   git operations, uv/Python runners, test harnesses, shell utilities, and
   `./scripts/*` globs for repo-local tooling.

This evidence-based approach means the allow list reflects actual behaviour rather
than theoretical needs, and avoids granting permissions for commands that were never
used.

## 7. Cross-Machine Propagation

Because `.claude/settings.json` is version-controlled, updates propagate via normal
git operations:

- **dev-primary / dev-secondary (Linux)**: `git pull` in workspace-hub root.
- **licensed-win-1 (Windows)**: `git pull` in Git Bash; user settings live at
  `%APPDATA%\Claude\settings.json` — remove `skipDangerousModePermissionPrompt`
  there if bypass mode was enabled.
- **New workstation**: `git clone` the repo, then remove
  `skipDangerousModePermissionPrompt` from `~/.claude/settings.json` (or
  `%APPDATA%\Claude\settings.json` on Windows).

No per-machine allow-list maintenance is required as long as the repo-level file is
kept current.

## 8. Running the Audit Again

If commands are routinely being blocked in normal workflow, re-run the audit to
identify candidates for the allow list:

```bash
uv run --no-project python scripts/permissions/audit-bash-commands.py \
  --sessions-dir ~/.claude/projects/-mnt-local-analysis-workspace-hub \
  --output /tmp/new-audit.yaml
```

Review `/tmp/new-audit.yaml`, apply the merge script to combine with the existing
baseline, then add any commands that exceed the threshold to `permissions.allow`.
Commit the updated `.claude/settings.json` so all machines benefit.
