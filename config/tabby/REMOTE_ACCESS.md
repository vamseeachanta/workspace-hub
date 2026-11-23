# Tabby remote access client notes

> **Legacy client note:** The [canonical remote Linux access
> runbook](../../docs/ops/remote-linux-access.md) is the canonical authority for
> architecture, setup, security, verification, recovery, and troubleshooting.
> This file covers Tabby client ergonomics only.

Never configure router port forwarding for SSH or port 22. <!-- ssh-no-forward-policy -->

## Create a Tabby profile

1. In Tabby, choose **Settings → Profiles & connections → New profile → SSH connection**.
2. Enter the registry hostname exposed through MagicDNS.
3. Enter the intended non-root username.
4. Select the private key from local machine-local secret storage. Never copy a
   private key into this repository or a shared configuration export.
5. Save the profile with a machine-specific display name and test it only after
   the canonical runbook's transport and key proofs pass.

Tabby tabs, split panes, keepalive, and SFTP are client conveniences; they do not
change the access architecture or authentication policy. For long-running work,
prefer a server-side `tmux` session so client disconnects do not end the job.

Profile synchronization is optional. Review any exported profile for usernames,
hostnames, key paths, or credentials before sharing it; keep machine-specific
values local.

## Scope boundary

- Use the canonical runbook for Tailscale installation, OpenSSH hardening,
  external-network testing, reboot testing, and rollback.
- Use the workstation registry for machine identity and non-secret declarations.
- Treat connection helpers as convenience only; report conflicts to the drift
  owner named in the canonical runbook.
