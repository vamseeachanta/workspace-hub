# Tabby with Tailscale

> **Legacy client note:** The [canonical remote Linux access
> runbook](../../docs/ops/remote-linux-access.md) is the canonical authority for
> Tailscale transport, OpenSSH authentication, security controls, verification,
> recovery, and troubleshooting. This file is not a Tailscale setup guide.

Never configure router port forwarding for SSH or port 22. <!-- ssh-no-forward-policy -->

## Tabby-specific use

After the canonical runbook's transport and authentication proofs pass:

1. Create an SSH profile in Tabby.
2. Use the workstation registry hostname resolved by MagicDNS.
3. Select the intended non-root username and a private key kept in machine-local
   secret storage.
4. Confirm the profile uses conventional OpenSSH authentication. Tailscale SSH
   remains an optional architecture choice, not a Tabby prerequisite.

Do not store observed addresses, authentication URLs, peer configuration, keys,
or credentials in this file or an exported Tabby profile. Tabby profile behavior
does not override tailnet grants, device approval, host policy, or rollback rules.
