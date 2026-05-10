# Cron + Daily Report Closeout Evidence Pattern

Use this reference when closing out a session whose scope is "fix all cron jobs" and "ensure the daily report is up to date".

## Evidence bundle to collect

Run or capture these in the same closeout window:

```bash
cd /mnt/local-analysis/workspace-hub
export WORKSPACE_HUB=/mnt/local-analysis/workspace-hub

# Render/install parity: live crontab must match canonical dry-run render.
bash scripts/cron/setup-cron.sh --dry-run > /tmp/workspace-hub-cron-dry.txt
crontab -l > /tmp/workspace-hub-cron-live.txt
python - <<'PY'
from pathlib import Path
live = Path('/tmp/workspace-hub-cron-live.txt').read_text().splitlines()
dry = Path('/tmp/workspace-hub-cron-dry.txt').read_text().splitlines()
# Ignore comments/blank lines if local headers differ; compare executable entries.
def entries(lines):
    return [ln for ln in lines if ln.strip() and not ln.lstrip().startswith('#')]
print({
    'live_entries': len(entries(live)),
    'dry_entries': len(entries(dry)),
    'parity': entries(live) == entries(dry),
    'duplicates': len(entries(live)) - len(set(entries(live))),
})
PY

# Cron health artifact.
bash scripts/monitoring/cron-health-check.sh --workspace "$WORKSPACE_HUB"
ls -lt .claude/state/cron-health/*.json | head

# Daily report freshness.
today=$(date +%F)
stat "logs/daily/$today.md"
tail -n 40 "logs/daily/$today.md"
```

## Closeout rule

Do not claim cron is fixed from `cron-health` alone. A complete closeout needs:

1. canonical dry-run vs live crontab parity;
2. duplicate count of zero for executable cron entries;
3. cron-health JSON with healthy task count and problem count;
4. current-day `logs/daily/YYYY-MM-DD.md` existence, size, and mtime;
5. explicit statement whether any external delivery/send action was performed;
6. committed and pushed handoff if the user asked to document/prepare to exit;
7. dirty-state disclosure, separating preserved unrelated generated artifacts from files in the cron/daily scope.

## Pitfall

Repo cleanliness can be blocked by unrelated generated provider/session artifacts. Do not bundle unrelated dirty files into a cron closeout just to force a clean tree. Preserve and disclose them explicitly while still proving the cron/daily scoped artifacts are committed and pushed.
