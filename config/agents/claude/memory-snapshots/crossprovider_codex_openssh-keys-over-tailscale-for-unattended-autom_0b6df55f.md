---
name: crossprovider codex openssh-keys-over-tailscale-for-unattended-autom
description: OpenSSH keys over Tailscale for unattended automation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [infrastructure, security, ssh, tailscale, automation]
---

For headless pipelines and long-running automation (e.g., claude -p overnight tasks), use conventional OpenSSH keys carried over a Tailscale VPN overlay—not Tailscale SSH (`--ssh`). Tailscale SSH delegates all identity decisions to the account/tailnet policy layer; if account credentials are compromised, SSH access is lost. OpenSSH keys on the VPN provide an independent authentication boundary. Machines holding API credentials and automation secrets must not be internet-exposed; Tailscale VPN eliminates port-forwarding risk, survives ISP IP changes, and falls back to relays through CGNAT.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
