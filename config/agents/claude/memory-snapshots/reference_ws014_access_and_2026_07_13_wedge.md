---
name: reference_ws014_access_and_2026_07_13_wedge
description: ACMA-WS014 (licensed-win-2) remote-access path + the 2026-07-13 userland wedge that needs a hardware power-cycle
metadata: 
  node_type: memory
  type: reference
  originSessionId: b4acb616-1fe3-48e4-b425-8735dc8728db
  modified: 2026-08-01T08:15:55.496Z
---

ACMA-WS014 = `licensed-win-2` (`ace-win-2` in heartbeats), OrcaFlex/ANSYS licensed
workstation. LAN `192.168.1.132`, MAC `38:7C:76:D2:24:F8`. **Reachable only from
ace-linux-1** (same LAN segment). Tailscale `100.97.133.34`. Standalone in workgroup
**`mkt-a-INC`** (NOT domain-joined; local SAM).

**Access path (fills the `unknown` in network_machines.md:19):** SMB/RPC over `net`
(samba). Auth file for `-A`: `username=vamseea`, **`domain=mkt-a-INC`** (NOT `WORKGROUP`
— that fails with LOGON_FAILURE), password = local-admin pw. Discover the workgroup
anonymously with `nmblookup -A 192.168.1.132`. `vamseea` is a local Administrator.

**Remote access for humans = ScreenConnect** (SecureConnect branding) via
`rockitconsulting.hostedrmm.com:8041`, MSP = Rockit Consulting, instance `1a5d6cc5d5f07e3e`.

**2026-07-13T21:37Z: systemic userland wedge (still unresolved 2026-08-01).** Kernel/NIC
healthy (ICMP 0.37ms) but sshd, tailscaled, RDP, ScreenConnect agent all non-serving;
`TermService`/`SessionEnv` frozen in `stop pending`. **Cannot be rebooted remotely** —
`shutdown.exe` (any variant, incl. via `net rpc service create`→start) launches but
stalls walking the frozen service list and never resets. `net rpc shutdown` blocked
(RemoteRegistry Disabled); no Intel AMT. **Needs a hardware power-cycle** — best remote
shot is asking Rockit Consulting for an out-of-band power-cycle. Anchor: heartbeat
`deckhand-licensed-runs-queue/queue/heartbeat/ace-win-2.json` frozen since that time.

Classifier blocks `net rpc service create/start` + `net rpc shutdown` from the agent
(remote-exec/persistence shape) — user must run them. Full incident record:
scratchpad `ws014-incident-2026-08-01.md`. Poller restart tracked by wh#2757.
Related: [[project_fleet_reachability_and_solver_access_2026_07_31]].
