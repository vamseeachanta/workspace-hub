# Telegram/Hermes Gateway VS Code Command Sheet

Purpose: copy/paste-ready commands for enabling and verifying the Hermes Gateway coordinator on `ace-linux-1`, then checking Telegram/Hermes readiness across available machines.

Assumptions:

- Run these from the VS Code integrated terminal on `ace-linux-1`.
- Workspace root is `/mnt/local-analysis/workspace-hub`.
- Hermes environment file is `/home/vamsee/.hermes/.env`.
- Some commands require sudo because they update systemd service configuration.

## 1. Open workspace in VS Code

```bash
cd /mnt/local-analysis/workspace-hub
code .
```

## 2. Verify current repo and gateway state before sudo changes

```bash
cd /mnt/local-analysis/workspace-hub

git status --short
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD

scripts/operations/verify-hermes-gateway-coordinator.sh || true
```

## 3. Install systemd override for Hermes Gateway

```bash
sudo mkdir -p /etc/systemd/system/hermes-gateway.service.d

sudo tee /etc/systemd/system/hermes-gateway.service.d/10-env-and-timeout.conf >/dev/null <<'EOF'
[Service]
EnvironmentFile=/home/vamsee/.hermes/.env
TimeoutStopSec=210
EOF
```

## 4. Reload and restart Hermes Gateway

```bash
sudo systemctl daemon-reload
sudo systemctl restart hermes-gateway.service
sudo systemctl status hermes-gateway.service --no-pager
```

## 5. Re-run coordinator verifier

```bash
cd /mnt/local-analysis/workspace-hub

scripts/operations/verify-hermes-gateway-coordinator.sh
```

Expected target:

```text
summary: all checks passed
```

At minimum, there should be no failures for:

- `EnvironmentFile=/home/vamsee/.hermes/.env`
- `TimeoutStopSec >= 210`

## 6. Run full Telegram/Hermes machine readiness

```bash
cd /mnt/local-analysis/workspace-hub

set -a
source /home/vamsee/.hermes/.env
set +a

scripts/readiness/telegram-hermes-readiness.sh
```

## 7. If `dev-primary` still fails because workspace is dirty

Inspect first:

```bash
cd /mnt/local-analysis/workspace-hub
git status --short
```

If files are intentional, commit/push:

```bash
git add -A
git commit -m "chore: reconcile telegram hermes readiness state"
git push origin main
```

If files are temporary/generated and safe to discard, review before running:

```bash
git diff --stat
git diff
```

Then discard tracked changes only if safe:

```bash
git restore .
```

Remove untracked files only if safe:

```bash
git clean -fd
```

Then rerun:

```bash
scripts/readiness/telegram-hermes-readiness.sh
```

## 8. Generate host-local evidence on `ace-linux-2`

From `ace-linux-1`:

```bash
ssh ace-linux-2 'cd /mnt/local-analysis/workspace-hub && hostname && git status --short && git rev-parse HEAD && hermes --version || true'
```

Then run the local readiness script on `ace-linux-2` if present:

```bash
ssh ace-linux-2 'cd /mnt/local-analysis/workspace-hub && set -a && source /home/vamsee/.hermes/.env && set +a && scripts/readiness/telegram-hermes-readiness.sh || true'
```

Final check back on `ace-linux-1`:

```bash
cd /mnt/local-analysis/workspace-hub
set -a
source /home/vamsee/.hermes/.env
set +a
scripts/readiness/telegram-hermes-readiness.sh
```

## Notes

- `licensed-win-1`, `licensed-win-2`, and `macbook-portable` are currently status-only unless explicitly onboarded for dispatch.
- `gali-linux-compute-1` / `shoerack` is currently not onboarded: no workspace root and Telegram mode disabled.
- Do not paste secrets into chat. Keep `.env` values local and redacted in reports.
