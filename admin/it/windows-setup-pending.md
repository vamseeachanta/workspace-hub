# Windows Machine Setup — Pending (Manual On-Site)

> WRK-228 | IT reference | Created: 2026-02-24

## Status

Windows machines require **manual on-site setup** by the operator.
Remote deployment is not available (no SSH, no remote management).

---

## Affected Machines

| Machine | OS | Status | Notes |
|---|---|---|---|
| ACMA-ANSYS05 | Windows 11 | Pending — operator on-site required | ANSYS workstation |
| acma-ws014 | Windows 11 | Pending — operator on-site required | Dev workstation |

---

## ace-linux-2 Deployment — SSH Attempt Blocked

SSH deployment to ace-linux-2 was attempted on 2026-02-24 but failed:

```
ssh -o BatchMode=yes -o ConnectTimeout=5 ace2 hostname
# Result: SSH FAILED (connection refused / host unreachable)
```

ace-linux-2 deployment must be completed manually when SSH access is restored.
Target path on ace-linux-2: `/mnt/workspace-hub/`

Deployment commands (run when SSH is available):

```bash
ssh ace2 "mkdir -p ~/.claude && \
  cp /mnt/workspace-hub/config/claude/keybindings.json ~/.claude/keybindings.json && \
  echo 'Deployed keybindings'"

ssh ace2 "grep -q 'CLAUDE_SCREENSHOT_DIR' ~/.bashrc || \
  echo 'source /mnt/workspace-hub/config/shell/bashrc-snippets.sh' >> ~/.bashrc && \
  echo 'bashrc updated'"

ssh ace2 "cat ~/.claude/keybindings.json"
```

---

## Steps for Windows Manual Setup

All steps are scripted in `scripts/setup/new-machine-setup.sh`.
Run the relevant sections manually on each Windows machine via Git Bash.

### Step 1 — Keybindings

```bash
# In Git Bash on the Windows machine:
mkdir -p ~/.claude
cp /c/mnt/workspace-hub/config/claude/keybindings.json ~/.claude/keybindings.json
# Or if the workspace is on a network drive, adjust the source path accordingly.
cat ~/.claude/keybindings.json
# Expected: { "submitPrompt": "ctrl+enter" }
```

Windows Claude Code already defaults to `Ctrl+Enter` for submit, so this
ensures the config file is present and explicit for consistency.

### Step 2 — Screenshot folder env var

Add to `~/.bashrc` (Git Bash) or Windows environment variables:

```bash
# In ~/.bashrc (Git Bash):
export CLAUDE_SCREENSHOT_DIR="${USERPROFILE}/Pictures/Screenshots"
```

Or via Windows System Properties:

1. Open **System Properties** → **Advanced** → **Environment Variables**
2. Add a new User Variable: `CLAUDE_SCREENSHOT_DIR` = `%USERPROFILE%\Pictures\Screenshots`

### Step 3 — Task Scheduler (optional auto-start)

Task Scheduler setup is needed if you want Claude Code or Chrome to auto-start
on login. Steps:

1. Open **Task Scheduler** (`taskschd.msc`)
2. Create a new Basic Task
3. Trigger: **At log on** (current user)
4. Action: **Start a program**
   - For Chrome: `"C:\Program Files\Google\Chrome\Application\chrome.exe"` with
     argument `--no-startup-window`
5. Finish

This is optional — most users launch Chrome manually.

### Step 4 — Chrome Claude Extension

Follow `admin/it/chrome-claude-setup.md` → Windows Git Bash section.
Target: extension `fcoeoabgfenejglbffodgkkbkcdhcgfn` at version 1.0.55+.

### Step 5 — Verify setup

After completing the steps above, run:

```bash
bash /c/mnt/workspace-hub/scripts/setup/verify-setup.sh
```

Check that R-UX section (section 9b) reports all green.

---

## Related

- `admin/it/chrome-claude-setup.md` — Chrome extension install guide
- `scripts/setup/new-machine-setup.sh` — bootstrap script (run on Windows)
- `scripts/setup/verify-setup.sh` — verification script
- `config/claude/keybindings.json` — canonical keybindings template
- `config/shell/bashrc-snippets.sh` — screenshot dir env var
- WRK-228 — Cross-machine terminal UX consistency
