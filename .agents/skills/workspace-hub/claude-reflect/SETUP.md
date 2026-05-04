# Claude-Reflect Setup Guide

## Quick Setup

### 1. Verify Hook Installation

Check that correction hooks are deployed to your repos:

```bash
cd D:/workspace-hub
for repo in */; do
  if grep -q "capture-corrections.sh" "$repo/.claude/settings.json" 2>/dev/null; then
    echo "✓ $repo"
  else
    echo "✗ $repo - run install-hooks.sh"
  fi
done
```

### 2. Install Hooks (if missing)

```bash
cd D:/workspace-hub/.claude/skills/workspace-hub/claude-reflect
./install-hooks.sh /d/workspace-hub/YOUR_REPO
```

### 3. Test Manual Reflection

```bash
cd D:/workspace-hub/.claude/skills/workspace-hub/claude-reflect/scripts
./run-reflection.sh --days 7 --dry-run
```

## Scheduled Execution

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task:
   - Name: "Claude Reflect Daily"
   - Trigger: Daily at 5:00 AM
   - Action: Start a program
   - Program: `D:\workspace-hub\.claude\skills\workspace-hub\claude-reflect\scripts\run-reflection.bat`
3. In task properties, enable "Run whether user is logged on or not"

### Linux/WSL (Cron)

```bash
# Edit crontab
crontab -e

# Add line (runs daily at 5 AM):
0 5 * * * /d/workspace-hub/.claude/skills/workspace-hub/claude-reflect/scripts/run-reflection.sh --days 30
```

## File Locations

| File | Purpose |
|------|---------|
| `.claude/state/corrections/` | Captured correction data |
| `.claude/state/reflect-history/` | Git history analysis |
| `.claude/state/patterns/` | Extracted patterns |
| `.claude/state/reflect-state.yaml` | Current RAGS state |

## Troubleshooting

### Hooks Not Capturing

1. Restart Claude Code session after installing hooks
2. Verify settings.json has PostToolUse > Write|Edit|MultiEdit matcher
3. Check hook script is executable: `chmod +x .claude/hooks/capture-corrections.sh`

### No Corrections Detected

Corrections are only logged when the same file is edited twice within 10 minutes.
Check `.claude/state/corrections/.recent_edits` to see tracked edits.

### RAGS Loop Errors

Check log file: `.claude/state/reflect-history/reflect.log`
