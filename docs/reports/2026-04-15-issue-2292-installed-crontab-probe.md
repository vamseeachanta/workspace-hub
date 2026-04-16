# Queue refresh installed-crontab probe — #2292

Date: 2026-04-15
Host: ace-linux-1

Observed live crontab entry on this host:

```cron
30 22 * * 0  PATH=$HOME/.local/bin:$PATH; cd /mnt/local-analysis/workspace-hub && bash scripts/cron/queue-refresh-weekly.sh >> /mnt/local-analysis/workspace-hub/logs/queue-refresh/$(date +\%Y-\%m-\%d).log 2>&1
```

Interpretation:
- `queue-refresh-weekly` is currently installed in the live crontab on `ace-linux-1`.
- So the live failure is **not** the `not-installed` branch on this host.
- Remaining branches are narrowed to:
  1. installed-but-not-firing / not-yet-fired in practice, or
  2. installed-and-failing after cron launch (including pre-wrapper bootstrap failure under real cron semantics).
