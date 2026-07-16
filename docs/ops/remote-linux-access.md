# Remote Linux access

> **Status:** Canonical operational authority
> **Scope:** Secure remote shell access to `ace-linux-1` and `ace-linux-2`
> **Audience:** Operators preparing, validating, or recovering remote access
> **Runtime changes:** None. Live rollout belongs to issues linked in the drift ledger.

This runbook defines the architecture and evidence contract. It deliberately does
not publish machine addresses, user identities, keys, tailnet configuration, or
router details.

## Authority

Use these sources in order. A lower source must not override a higher one:

1. [Workstation registry](../../config/workstations/registry.yaml) — canonical
   machine identity and non-secret capability declarations.
2. [This remote access runbook](remote-linux-access.md) — canonical architecture,
   security sequence, verification, and recovery policy.
3. [Connection helpers](../../scripts/operations/connection/) — executable
   convenience only; a conflicting helper is drift, not authority.
4. Machine-local secret storage — private keys, credentials, recovery material,
   and observed device state. Never commit these values.

When declared and observed state differ, record the difference and route it to the
owning issue. Do not copy a point-in-time value into this runbook.

## Architecture

The canonical design separates two layers:

- **Tailscale transport** supplies encrypted, private reachability and MagicDNS.
- **Conventional OpenSSH keys** provide host authentication and user
  authentication through the machine's normal `sshd` service.

Tailscale SSH is optional. It is not the default authentication layer and must not
be enabled as an undocumented substitute for conventional OpenSSH keys.

```text
travel client ── outbound Tailscale ── tailnet ── outbound Tailscale ── Linux host
                     │                                      │
               OpenSSH client                         OpenSSH sshd

home router: no inbound SSH rule
```

Never configure router port forwarding for SSH or port 22. <!-- ssh-no-forward-policy -->

| Approach | Decision | Reason |
|---|---|---|
| Tailscale transport + conventional OpenSSH keys | Canonical | Separates private reachability from familiar, auditable host authentication. |
| Tailscale SSH | Optional exception | Useful for identity-managed access only after its grants and recovery model are explicitly reviewed. |
| Self-hosted WireGuard | Not selected | Adds public coordination, dynamic-address, and recovery operations without improving this two-host use case. |
| Direct public SSH | Prohibited | Exposes the host authentication surface and couples recovery to router and ISP state. |

Use stable registry hostnames through MagicDNS. Do not encode observed addresses in
documents, aliases, shell history intended for sharing, or helper defaults.

## Security controls

### Tailnet identity and device controls

- Require multi-factor authentication on the identity provider used by the
  tailnet.
- Enable device approval so an authenticated account alone cannot add an
  unreviewed client.
- Express access as least-privilege grants: only approved operator identities and
  devices may reach the Linux SSH service.
- Enable MagicDNS and use registry hostnames rather than copied addresses.
- Make an explicit Tailscale server device key expiry decision. Server devices
  that disable expiry need a documented ownership and removal process.
- Make an explicit Tailscale client device key expiry decision. Travel clients
  should normally expire and be re-authenticated rather than remain trusted
  indefinitely.
- Review devices and grants before travel and remove lost, replaced, or unused
  clients promptly.

See Tailscale's official guidance for [device approval](https://tailscale.com/kb/1099/device-approval),
[grants](https://tailscale.com/kb/1324/grants), [MagicDNS](https://tailscale.com/kb/1081/magicdns),
and [key expiry](https://tailscale.com/kb/1028/key-expiry).

### Host authentication controls

- Use conventional OpenSSH keys with a passphrase or hardware-backed key on each
  approved client. Keep private keys in machine-local secret storage.
- Install only the required public key for the intended non-root account.
- Disable password and keyboard-interactive authentication only after the ordered
  proof in the setup sequence succeeds.
- Prohibit direct root login. Use an individually attributable account and elevate
  only when required.
- Keep Tailscale SSH optional. If a later issue enables it, document grants,
  check-mode behavior, logging, and a conventional recovery path first.
- Apply host firewall rules consistently with tailnet-only access; do not create a
  public exposure path as a fallback.

The option semantics are defined by OpenBSD's authoritative
[`sshd_config(5)`](https://man.openbsd.org/sshd_config) manual. Confirm the local
OpenSSH version supports every selected directive before rollout.

## Setup sequence

Live execution will use `ace-linux-2` as the canary before `ace-linux-1`. Perform
the following sequence independently on each server; do not assume one machine's
observed state proves the other's.

1. **Preserve recovery access.** Establish a local console or an already-proven,
   privileged recovery session. Record who can restore the prior SSH configuration.
   Before changing it, **capture the prior drop-in state**: whether the planned
   path exists, its exact content, owner, group, and mode. Keep that snapshot in a
   root-readable machine-local recovery location and record whether rollback must
   restore a prior file or remove a newly created file.
2. Install Tailscale from the official [Linux installation
   guide](https://tailscale.com/kb/1031/install-linux), authenticate the device,
   approve it if required, and confirm the expected registry hostname in MagicDNS.
3. From the local console, obtain the server's SSH host-key fingerprint through an
   out-of-band channel. On the client, **verify the SSH host key fingerprint** before
   accepting the first session. A changed host key blocks access until the local
   console proves an authorized rotation; never bypass the warning reflexively.
4. Install the intended public key for `<operator-user>`, then **prove key authentication**
   in batch mode over the Tailscale transport. Do not harden on
   the basis of an interactive password fallback.
5. **Apply the hardening drop-in** under the local OpenSSH configuration directory.
   The intended effective policy includes `PasswordAuthentication no`,
   `KbdInteractiveAuthentication no`, and `PermitRootLogin no`, plus an operator
   allowlist where operationally appropriate.
6. Validate syntax with `sudo sshd -t`. Then inspect the effective configuration
   for a representative connection context with
   `sudo sshd -T -C user=<operator-user>,host=<client-resolved-hostname>,addr=<client-address>`.
   Here `host` and `addr` describe the connecting client, not the server. Repeat
   the check for every authorized client context that could select a different
   `Match` block. Confirm every intended directive resolves to its hardened value.
   A syntax or effective-policy mismatch blocks reload and triggers rollback.
7. **Reload, do not restart** the SSH service. A reload preserves the established
   recovery session while applying the validated configuration.
8. From a separate terminal, **prove a second session** using batch-mode key login
   over the Tailscale hostname. Then prove the required rejection cases.
9. Only after all evidence is captured may the operator **close recovery access**.
10. Reboot during the scheduled validation window and repeat transport,
   authentication, rejection, and recovery checks.

Do not paste private key material, authentication URLs, device credentials, peer
configuration, or observed addresses into issues or evidence comments.

## Verification matrix

Record command, timestamp, source network class, target hostname, exit status, and
redacted result for every required proof.

| Layer | Required proof | Pass condition |
|---|---|---|
| Identity | MFA and device approval | Tailnet administration shows both controls active for the tested identities and devices. |
| Authorization | Least-privilege grants | Intended client can reach the intended servers; an out-of-scope identity or device cannot. |
| Naming | MagicDNS | Registry hostname resolves and connects without an address literal. |
| Transport | External network | Connection succeeds from a network outside the home router. |
| Authentication | Batch-mode key login | Non-interactive OpenSSH login succeeds for the intended non-root account. |
| Host identity | Pinned host-key fingerprint | The accepted fingerprint matches evidence obtained out-of-band from the local console. |
| Effective policy | Context-aware server configuration | `sshd -T -C` resolves the intended authentication and root-login directives to hardened values. |
| Rejection | Password authentication rejected | A password-only attempt cannot authenticate. |
| Rejection | Keyboard-interactive authentication rejected | A keyboard-interactive-only attempt cannot authenticate. |
| Rejection | Root login rejected | Direct root authentication cannot succeed. |
| Persistence | Post-reboot | Tailscale, MagicDNS, and batch-mode key login recover after a scheduled reboot. |
| Perimeter | Router no-forward evidence | Router configuration review shows no inbound mapping or equivalent exposure. |
| Recovery | Rollback path | Operator can restore the prior validated drop-in from the preserved recovery channel. |

Run the complete matrix first for `ace-linux-2`. [Issue
#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550) must record a
successful canary before [issue
#3551](https://github.com/vamseeachanta/workspace-hub/issues/3551) begins the
`ace-linux-1` rollout.

## Rollback and recovery

The rollback path is the preserved local console or privileged recovery session
plus a known prior SSH configuration.

1. Keep the failing new session and the recovery session distinct.
2. From the pre-change record, **restore the prior file or remove the newly created
   file**. Restore the recorded owner, group, and mode; do not guess which state
   existed.
3. Run `sudo sshd -t`, then repeat the representative `sshd -T -C` effective-policy
   inspection. Do not reload a syntactically invalid or unintended configuration.
4. Reload the SSH service without restarting it.
5. Prove a fresh conventional key-authenticated session and its trusted host key
   before ending recovery.
6. If transport is the failure, use the local console to restore Tailscale service
   health; do not weaken OpenSSH or create a public route.
7. Record the failure and redacted evidence on the applicable rollout issue.

A lost travel client is an identity incident: revoke or expire the device, remove
its authorization, and rotate affected user keys. It is not a reason to relax the
server policy.

## Troubleshooting

| Symptom | Check | Safe response |
|---|---|---|
| Hostname does not resolve | MagicDNS enabled, device authenticated, registry hostname current | Correct declared or observed drift in its owning issue; do not paste an address into the runbook. |
| Device is present but unreachable | Device approval, grants, service state, and Tailscale connection type | Restore the private transport from local recovery; a relayed connection may be slower but remains valid. |
| Client authentication expired | Client device expiry and identity-provider session | Re-authenticate and re-approve according to policy. |
| Tailscale server device authentication expired | Tailscale server device key expiry decision and administrative ownership | Restore through the documented recovery channel; do not create an unmanaged permanent credential. |
| Key login fails | Intended user, public-key installation, file permissions, client key selection, server logs | Fix key placement or selection while recovery remains open. Do not enable a public password fallback. |
| Changed host key warning | Compare the presented fingerprint with fresh local-console evidence and the recorded rotation | Stop on any mismatch; replace the pinned key only after authorized out-of-band verification. |
| Hardened configuration fails validation | Drop-in syntax and local OpenSSH version | Restore the prior drop-in, rerun `sshd -t`, and leave the service unchanged until valid. |
| Works at home but not while travelling | External-network test, grants, device state, connection diagnostics | Correct the private-overlay problem before departure; do not alter router exposure. |

For transport diagnosis, use Tailscale's official documentation for
[connection types](https://tailscale.com/kb/1257/connection-types) and
[Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh).

## Drift ledger

This table records unverified conflicts; it does not reconcile them.

| Drift class | Status | Owner and required evidence |
|---|---|---|
| Endpoint and alias exposure | Unverified; helpers and historical docs contain competing connection claims. | [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549) will remove address-coupled behavior and prove registry-driven helpers without publishing live endpoints. |
| ace-linux-2 capability and VNC divergence | Unverified; registry, inventory, and handoff guidance disagree. | [#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550) will attest the canary's capabilities and record the separate VNC disposition. |
| ace-linux-1 historical address and installed-state claims | Unverified; closed issues and legacy notes are not live evidence. | [#3551](https://github.com/vamseeachanta/workspace-hub/issues/3551) will attest current transport and authentication state after the canary succeeds. |

Changes to identity/capability declarations belong in the registry. Changes to
connection helpers belong to #3549. Machine observations and redacted verification
evidence belong to #3550 or #3551; secrets remain machine-local.
