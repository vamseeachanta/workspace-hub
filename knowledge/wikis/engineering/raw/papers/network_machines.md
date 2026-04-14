> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/network_machines.md

---
name: network-machines
description: LAN machines — IPs, SSH access, credentials, and data sync status for ace-linux-1/2, home-win, macbook-portable, licensed-win-1
type: reference
---

## Network Machines (192.168.1.0/24)

| Machine | IP | OS | SSH User | SSH Auth | Notes |
|---------|-----|-----|----------|----------|-------|
| ace-linux-1 (dev-primary) | .100 | Linux | vamsee | — | Primary workstation (us); hostname: ace-linux-1 |
| ace-linux-2 (dev-secondary) | .103 | Linux | vamsee | key | Tailscale: 10.1.0.2; hostname: ace-linux-2. "dev-secondary" is a legacy alias — does NOT resolve as hostname. Cross-machine scripts use ace-linux-2 (updated 2026-03-25). Config/routing/WRK items still use dev-secondary as a label. |
| home-win | .148 | Windows | devuser | SMB only (port 22 blocked) | SMB share: `\\10.0.0.3\GitHub` → C:\GitHub; repos: aceengineer-admin, achantas-data |
| macbook-portable | .166 | macOS (ARM64 M1) | krishna | key (passwordless) | Hostname: Vamsees-MacBook-Air.local; `~/workspace-hub/` has aceengineer-admin, achantas-data, sabithaandkrishnaestates; AirPlay ports 5000/7000 also open |
| licensed-win-1 | — | Windows | — | no SSH | OrcaFlex license machine; not on local LAN |
| ACMA-WS014 | .132 | Windows | — | unknown | Windows workstation |

## Access Patterns

- **ace-linux-2**: `ssh vamsee@ace-linux-2`, `ssh vamsee@10.0.0.2` (LAN), or `ssh vamsee@10.1.0.2` (Tailscale)
- **home-win**: SMB via `smbprotocol` Python lib; `register_session("10.0.0.3", username="devuser", password="rose109Gud")`; GitHub share must be manually shared (right-click → Share)
- **macbook-portable**: `ssh krishna@10.0.0.4` (key auth installed 2026-03-15); password: 12082016; Remote Login + File Sharing enabled manually
- **Mac repos**: aceengineer-admin diverged (only .DS_Store diff, local is 20+ commits ahead); achantas-data in sync; sabithaandkrishnaestates in sync

## Data Sync Status (2026-03-15)

- home-win → dev-primary: synced (75 files aceengineer-admin, 549 files achantas-data); revenue forecast reverted (laptop was stale)
- macbook-portable → dev-primary: synced; only new file was .numbers spreadsheet in sabithaandkrishnaestates
- home-win CLAUDE.md was agent-os format — discarded; automation package reorganized to src/aceengineer_admin/automation/

## Other Devices on LAN

.1=router, .107=old Debian(SSH), .149=LG TV, .160=Linksys RE6500, .169=Epson printer, .185=AirPlay device, .189=Chromecast
