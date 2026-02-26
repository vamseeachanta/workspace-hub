# Plan: Weekly Engineering Suite Update Script + Cron Job

## Context

ace-linux-2 now has a full engineering + GIS suite installed (Blender 5.0.1 snap, QGIS 3.40.15, Google Earth Pro, Gmsh, ParaView, OpenFOAM, FreeCAD, meshio, PyFoam). The user wants a weekly cron job that keeps all these programs updated to their latest stable versions automatically.

## Approach

Create two files following the existing `setup_maintenance_cron.sh` pattern:

### File 1: `scripts/setup/weekly-engineering-update.sh`

Update script that handles all installed programs by update method:

| Category | Programs | Update Method |
|----------|----------|---------------|
| **apt** | Gmsh, ParaView, FreeCAD, OpenFOAM, QGIS, Google Earth Pro | `apt update && apt upgrade -y <packages>` |
| **snap** | Blender | `snap refresh blender` |
| **pip** | meshio, PyFoam, pyvista, gmsh (python) | `pip3 install --user --upgrade` |

Script features:
- Runs as root (for apt/snap), pip upgrades run as `$SUDO_USER`
- Logs everything to `/var/log/engineering-suite-update-YYYYMMDD.log`
- Before/after version capture for each program
- Only reports changes (skip noise when nothing updated)
- Summary report appended to `.claude/reports/maintenance/engineering-updates.log`
- Exit codes: 0 = all OK, 1 = partial failure (logged but non-fatal)
- `--dry-run` mode to preview without applying
- `--status` mode to show current versions

### File 2: `scripts/setup/setup-engineering-update-cron.sh`

Cron installer following exact pattern of `scripts/operations/maintenance/setup_maintenance_cron.sh`:
- Commands: `install | remove | status | run`
- Schedule: **Weekly Sunday 03:00** (`0 3 * * 0`)
- Installs as **root cron** (needs sudo for apt/snap)
- Marker comment: `# weekly-engineering-update`

### Cron Installation

After creating both scripts, install the cron job on ace-linux-2 (user runs `sudo` commands).

## Critical Files

| File | Action |
|------|--------|
| `scripts/setup/weekly-engineering-update.sh` | **Create** |
| `scripts/setup/setup-engineering-update-cron.sh` | **Create** |
| `scripts/setup/engineering-suite-install.sh` | **Update** — add QGIS + Google Earth Pro sections |
| `.claude/work-queue/working/WRK-290.md` | **Update** — log cron setup |

## Verification

1. Run `sudo bash scripts/setup/weekly-engineering-update.sh --dry-run` — should list all programs with current versions, no changes applied
2. Run `sudo bash scripts/setup/weekly-engineering-update.sh --status` — version table
3. Run `sudo bash scripts/setup/setup-engineering-update-cron.sh install` — installs root cron
4. Verify with `sudo crontab -l` — should show weekly entry
