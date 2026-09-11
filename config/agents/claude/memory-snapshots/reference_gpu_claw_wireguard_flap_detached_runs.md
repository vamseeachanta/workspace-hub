---
name: reference-gpu-claw-wireguard-flap-detached-runs
description: "ace-linux-1→gpu-claw WireGuard (NM connection \"Undi\") flaps; run work detached with GitHub as the progress channel"
metadata: 
  node_type: memory
  type: reference
  originSessionId: f9868b71-5856-4aaf-a608-198faeca149c
  modified: 2026-07-22T18:41:53.328Z
---

**UPDATE 2026-09-02: the tailnet IS the route. Use `ssh gpu-claw`.**
`~/.ssh/config` now points **both** `gpu-claw` and `gpu-claw-ts` at
100.101.237.123, user `undi`, **no ProxyCommand**; the flapping LAN/WireGuard
route is preserved as `gpu-claw-lan`. Two traps cost hours before this landed:

- **The old `gpu-claw-ts` ProxyCommand dialled the USERSPACE tailscaled**
  (`~/.local/state/tailscaled/tailscaled.sock`), which is **logged out**, so
  every attempt died as `Connection closed by UNKNOWN port 65535` with nothing
  pointing at auth. The proxy was never needed: the *system* tailscaled holds a
  kernel TUN, so `ip route get 100.101.237.123` goes straight out `tailscale0`.
  (The userspace daemon still being logged out breaks Taildrop/phone-media,
  which is a separate concern — it needs an interactive browser login.)
- **The user must be `undi`.** Tailscale SSH is on at gpu-claw and its ACL
  rejects `vamsee`: `tailnet policy does not permit you to SSH as user`.
  Omitting the user silently defaults to the local username and fails that way.

Also: **the `[b]racket` pgrep idiom does NOT survive Tailscale SSH.** The
tailscaled `be-child ssh` process and the `bash -c` both carry the full command
string, so `ps | grep -E "[k]cs_fine"` still self-matches. Poll a marker file
or check `/proc/<pid>/cwd`, per [[feedback-track-fleet-lanes-from-control-surface]].

**Prior note, 2026-07-22: no longer the only route** — gpu-claw joined the tailnet
(100.101.237.123, Tailscale SSH on; see [[project_external_ssh_tailscale_fleet]]).
WG remains until deckhand#557 retire test passes.

The legacy route ace-linux-1 → gpu-claw (192.168.184.142, user `undi`) is the
NetworkManager WireGuard connection **"Undi"** (local 10.200.253.11/32). It
flaps: handshakes go unanswered for 30+ min stretches while gpu-claw itself
stays healthy (verify via `deckhand-licensed-runs-queue` heartbeat/poll
commits — the box polls every ~20 min). `nmcli con down/up Undi` rarely fixes
it; the failure is far-side. No alternate route (ace-linux-2 has no tunnel).

**Working pattern (proven on llm-wiki-mkt-a #267):** never run long work over
the SSH session. Ship scripts during a tunnel window, launch with
`nohup ... > log 2>&1 &`, and have the job push its outputs/branch to GitHub;
watch completion from ace-linux-1 via `gh api .../branches/<branch>` polling.
Use retry-loop monitors (probe every 45–60 s) to fire the launch at the first
window. `pgrep -f <pattern>` over SSH self-matches the ssh command string —
use a bracketed pattern like `[i]nterFoam` when checking CFD load there.

Related: VPN retire / tunnel topology is deckhand#557 (fleet dispatch epic).
