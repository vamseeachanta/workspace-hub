# Dev Environment Setup Guide

Source: WRK-050 Phase 4 — Dev Environment Readiness

## Overview

`dev-env-check.sh` reads a per-machine YAML manifest and reports on agent
CLIs, repos, and domain tools at terminal startup. It is informational only
(always exits 0) and targets under 2 seconds using parallel version probes.

---

## 1. Install the Check Script in .bashrc (Linux)

Add the following one-liner to `~/.bashrc` or `~/.zshrc`:

```bash
[ -f /mnt/local-analysis/workspace-hub/scripts/operations/system/dev-env-check.sh ] \
  && bash /mnt/local-analysis/workspace-hub/scripts/operations/system/dev-env-check.sh
```

Adjust the path to match `workspace_root` on the target machine. After saving,
reload with `source ~/.bashrc` or open a new terminal.

To set the default start directory to workspace-hub, append:

```bash
cd /mnt/local-analysis/workspace-hub
```

---

## 2. Add a Machine Manifest

Manifests live at:

```
specs/modules/hardware-inventory/manifests/<hostname>.yml
```

The script resolves the manifest by running `$(hostname)` at startup. Create
a file named exactly after the machine's hostname.

### Manifest Schema

```yaml
hostname: <output of hostname command>
alias: <short role-based name, e.g. eng-primary>
os: ubuntu | windows
os_version: "24.04"
role: primary-dev | sim-node | data-server
workspace_root: /path/to/workspace-hub

repos:
  - repo-name-1
  - repo-name-2

agent_clis:
  claude: ">=1.0"
  gemini: ">=0.1"

domain_tools:
  python3: ">=3.10"
  git: ">=2.30"
  uv: ">=0.1"

notes: "Free-text description of machine role."
```

All version specs use `>=X.Y` format. The script extracts the first numeric
token from `<tool> --version` output for comparison.

---

## 3. Machine Manifests in This Workspace

| File | Hostname | Alias | Role |
|------|----------|-------|------|
| `manifests/vamsee-linux1.yml` | vamsee-linux1 | eng-primary | primary-dev |
| `manifests/ace-linux-1.yml` | ace-linux-1 | eng-primary | primary-dev |
| `manifests/ace-linux-2.yml` | ace-linux-2 | eng-secondary | sim-node |

`vamsee-linux1` and `ace-linux-1` both refer to AceEngineer-01. The duplicate
entries ensure the check works regardless of which hostname the machine reports.

---

## 4. OS Notes

### Ubuntu / Debian Linux

- Tested on Ubuntu 24.04. Requires bash 4+, `sort -V`, `timeout`, `awk`, `sed`.
- All standard on Ubuntu 20.04+.
- Make the script executable: `chmod +x dev-env-check.sh`

### Windows (future)

- A `dev-env-check.ps1` counterpart is planned (WRK-050 Phase 4 Step 4b).
- Add to PowerShell `$PROFILE`:
  ```powershell
  $script = "C:\path\to\workspace-hub\scripts\operations\system\dev-env-check.ps1"
  if (Test-Path $script) { & $script }
  ```
- Set default start directory in Windows Terminal `settings.json`:
  ```json
  "startingDirectory": "C:\\path\\to\\workspace-hub"
  ```

---

## 5. Log File

Verbose output is written to `~/.dev-env-check.log`. Each run appends a
timestamped block. Review with:

```bash
tail -50 ~/.dev-env-check.log
```

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "No manifest found" | Hostname mismatch | Run `hostname` and create matching `.yml` |
| Tool shows WARN / version unreadable | CLI hangs on `--version` | Expected for some tools (e.g. gemini); no action needed |
| Script takes >2s | One probe hanging | Reduce `VERSION_TIMEOUT` in script if needed |
| Colors missing | Non-ANSI terminal | Redirect: `bash dev-env-check.sh 2>&1 \| cat` |
