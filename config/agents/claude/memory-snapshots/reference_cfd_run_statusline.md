---
name: cfd-run-statusline
description: Where the CFD run status line lives — gpu-claw cron writes ~/cfd/b1552/status/latest.txt every 15 min (+ status.log history); both Claude Code status bars read it; ace-linux-1 self-refreshes the mirror (crontab edits are denied there)
metadata: 
  node_type: memory
  type: reference
  originSessionId: d40540de-bdf2-4f0d-a52f-ec7d12a1f029
  modified: 2026-09-04T10:43:48.514Z
---

Set up 2026-09-04 at the owner's request ("statusline for the interFoam run / session, updated
every 15 min"). Scripts are tracked in `llm-wiki-mkt-a/projects/B1552-.../analysis/scripts/`:

| Piece | Where it runs | What |
|---|---|---|
| `cfd_status.sh` (`~/cfd/b1552/cfd-status.sh`, alias `cfd-status`) | gpu-claw | full table / `--watch` / `--line`; reads markers + `log.interFoam` only, never process names |
| `cfd_status_cron.sh` | gpu-claw crontab `*/15` | writes `~/cfd/b1552/status/latest.txt` + appends `status.log` (durable 15-min history) |
| `cfd_statusline.sh` | both Claude Code status bars | prints the cached line + age (`<<STALE` past 40 min) + model; on the control surface it self-refreshes the mirror in the background when > 15 min old (replaces cron — `crontab -` is permission-denied on ace-linux-1) |
| `cfd_status_pull.sh` | ace-linux-1 (called by the above) | `ssh gpu-claw cat latest.txt` → `~/cfd/b1552/status/latest.txt` |
| `cfd_statusline_combined.sh` | `statusLine` on ace-linux-1, gpu-claw, ace-linux-2 | hub `.claude/statusline-command.sh` line + ` │ ` + CFD line (hub found at /mnt/ace/ws or ~/ws) |
| `cfd_status_deploy.sh <host> [--source host\|/path]` | ace-linux-1 | one-command install: scripts → `~/cfd/b1552/status-tools/`, alias, `status/source`, cron (run owner only), settings.json statusLine (backed up) |

Per-host: gpu-claw = run owner (cron writer, source=gpu-claw); ace-linux-1 mirrors by ssh pull and
also writes the shared NFS copy `/mnt/ace/cfd-status/latest.txt`; **ace-linux-2 has no key to
gpu-claw** so its source is that NFS path (it mounts ace-linux-1's disk). settings.json backups
`settings.json.bak-<stamp>` on each host. Health flags in the line: `<<PSEUDO-DT COLLAPSE` (smoothed max
< 1e-2 s — the r2 failure signature) and `<<MASS` (water volume drift > 0.5 %).

Caveat learned: the first `statusline-setup` pass REPLACED the owner's existing hub status
line; always compose with the existing command, never overwrite it.
