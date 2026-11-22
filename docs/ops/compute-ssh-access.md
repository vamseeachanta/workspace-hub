# Private compute SSH access

The selected design is **Tailscale transport with conventional OpenSSH keys**,
subject to installation-specific evidence. This follows the
[canonical remote access architecture](remote-linux-access.md#architecture).
It removes dependence on a manually maintained standalone WireGuard profile;
Tailscale itself uses WireGuard. It does not promise a direct peer connection:
Tailscale can use relays. Current reachability, authentication, transfer and
recovery are **NOT_EVALUATED**. Keep the existing private access route until a
replacement passes the complete verification matrix. No service or route is
changed by this procedure's offline tool.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Define a private access decision and offline evidence assessment to avoid treating historical reachability as current proof. |

## Scope and authority

Refs #3404.
The linked compute onboarding work remains independent of this access decision.
The issue's access history establishes an intermittent private route, not the
current availability of another transport. This document extends the canonical
runbook to compute access; it does not replace registry identity, change routing,
or authorize installation, firewall changes or credential management.

The implementation covers three slices: an offline selector, strict evidence
validation, and this operator procedure with a worked example. Live rollout and
reconnect automation require separate authorized execution and measured evidence.

## Option decisions

| Candidate | Decision and reason | Additional proof required |
|---|---|---|
| `tailscale_openssh` | Preferred design; private naming and transport with existing key authentication. | Device approval, identity controls, least-privilege grants and an explicit device-expiry policy. |
| `tailscale_subnet_openssh` | Alternative when the server cannot run the overlay client; introduces a router dependency. | Device controls plus route approval, both directions of connectivity and router restart recovery. |
| `lan_openssh` | Alternative only with a proven private routed path from the intended client network. Physical proximity or a static route declaration alone is insufficient. | End-to-end private routing, firewall policy and return route. |
| `cloudflare_openssh` | Deferred unless existing policy permits unattended SSH. The documented client-side authentication flow opens a browser, so headless use cannot be assumed. | Reviewed unattended policy and actual provisioning, persistence and transfer proofs. |
| `managed_wireguard` | Interim fallback when no independent alternative qualifies; it retains the original dependency. No reconnect service is installed here. | Authorized bounded reconnect procedure, failure detection and recovery proven without disrupting active work. |
| Tailscale SSH | Not selected: a separate authentication and authorization model requiring an explicit exception under the canonical architecture. | Separate grants and recovery review before use. |
| Public or router-forwarded SSH | Prohibited by the canonical access policy. | Not an eligible fallback. |

The selector considers the eligible candidates in table order. This is a design
preference, not a latency or reliability ranking. Prefer a proven alternative to
an unverified preferred option. A selected `managed_wireguard` result explicitly
reports `manual_profile_independent: false`. No eligible option means no migration.

## Evidence method

Use a private JSON object keyed by the eligible candidate identifiers above.
Each value is an object of the following propositions. Only JSON `true`, `false`
or `null` is allowed; absent keys mean unknown. Unknown candidates, unknown
fields, duplicate keys, strings and numbers are rejected. No endpoints, identity
values, credentials, raw logs or evidence locators belong in this input.

| Required field for every candidate | Meaning of `true` |
|---|---|
| `private_only` | Private transport and effective firewall policy verified; no public SSH exposure. |
| `key_only` | Effective server authentication requires `publickey`; intended non-root key login succeeds without fallback. |
| `password_disabled` | Effective server policy and password-only rejection verified. |
| `interactive_disabled` | Effective keyboard-interactive policy and rejection verified. |
| `root_disabled` | Effective direct-root policy and rejection verified. |
| `host_key_verified` | Host key pinned after an out-of-band fingerprint check. |
| `least_privilege` | Intended source identity can access the target; an excluded identity cannot. |
| `recovery_verified` | Independent console or preserved recovery channel can restore prior access. |
| `headless_provisioning` | Intended non-interactive provisioning command succeeds over this path. |
| `job_survives_disconnect` | A harmless detached job survives connection loss and can be reattached. |
| `ssh_data_transfer` | Required rsync and/or rclone SFTP workflow succeeds with independent content comparison. |
| `post_reboot` | Private transport and key login recover after an authorized restart test. |

Additional fields are `device_controls` for both Tailscale candidates,
`subnet_route_verified` for subnet routing, `routed_private_path` for LAN,
`unattended_policy` for Cloudflare, and `reconnect_verified` for managed WireGuard.
Their meanings are the additional proofs in the option table. Unused fields are
invalid, which helps detect evidence copied to the wrong transport.

Every alternative except managed WireGuard also requires
`manual_profile_independent`: prove access with the old manually maintained
profile inactive, from the intended client network, during an authorized test
with independent recovery available. A transport name alone cannot establish
that its underlying route is independent. This field concerns the old profile,
not the cryptographic protocol used by Tailscale.

The decision rule is a conjunction: all required fields true gives `PASS`; any
false gives `FAIL`; otherwise `NOT_EVALUATED`. The first passing candidate is
selected. Overall `NOT_EVALUATED` means there is no qualified selection, even if
individual candidates failed. Failed and missing fields are always retained.
There are no equations, numerical scores, timeouts or acceptance constants.

An operator must retain dated evidence privately, including the tested source
network, authorized identity context, local software versions, method, observed
result and recovery proof. Reassess after expiry, access-policy changes, route
changes or failed recovery. Boolean declarations are not authenticated evidence
and the selector cannot detect stale or fabricated declarations. A `PASS` is an
offline policy result, not confirmation of access or permission to migrate.

## Operator commands and verification

Populate `SSH_TARGET` privately with the local SSH alias for the intended
non-root identity and private endpoint. Pin its host key through the canonical
runbook before use. Configure the alias for the chosen transport and identity
file; do not put its real value in shared documentation. Inspect effective
configuration locally and confirm no unintended proxy or address overrides.

The exact shell access command, after those prerequisites, is:

```sh
: "${SSH_TARGET:?Set the private SSH alias locally}"
ssh -o BatchMode=yes -o PreferredAuthentications=publickey \
  -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no \
  -o StrictHostKeyChecking=yes "$SSH_TARGET"
```

The options follow OpenSSH `ssh_config(5)` below: batch mode prevents prompts,
public-key preference excludes other user authentication methods, and strict
host-key checking requires prior trusted enrollment. They do not establish
server-side hardening. Follow the canonical ordered setup, context-aware
`sshd -T -C` inspection and rejection tests before declaring the server secure.
The tool never executes these commands or reads SSH configuration.

| Use | Confirmation procedure | Current outcome |
|---|---|---|
| Headless provisioning | Run a harmless non-interactive command through the selected alias, then the authorized provisioning smoke check. Verify that credentials do not require browser or terminal interaction. | NOT_EVALUATED |
| Long benchmarks | Use a remote terminal multiplexer or service with durable output. Disconnect the client deliberately during a harmless job, reconnect and confirm the job and output survived. A bare SSH shell does not guarantee job survival. | NOT_EVALUATED |
| Data movement | Test rsync over the same strict SSH options. For rclone use its SFTP backend, explicit key authentication and a trusted known-hosts file; rclone does not automatically inherit SSH alias configuration. Compare a disposable test payload independently and exercise restart/resume if required. | NOT_EVALUATED |
| Restart and recovery | During an authorized window, repeat login and required rejection cases after restart; prove console recovery without relaxing authentication or exposing SSH. | NOT_EVALUATED |

Set duration, payload size and throughput acceptance criteria from the actual
workload before testing. No benchmark or transfer performance is inferred here.
Keep private raw command output out of the public repository.

## Offline worked example

Synthetic inputs below describe a successful key-only check and a failed restart
check. They are not observations of a real installation. Save this JSON as a
private local file:

```json
{
  "tailscale_openssh": {
    "key_only": true,
    "post_reboot": false
  }
}
```

Run from the repository root, using the evidence file's local location:

```sh
uv run --no-project python scripts/operations/connection/ssh_access_plan.py "$EVIDENCE_FILE"
```

Hand calculation: `post_reboot` is false, so this candidate is `FAIL` regardless
of its missing fields. All other candidates have missing evidence and are
`NOT_EVALUATED`. Therefore `selected` and `manual_profile_independent` are `null` and
the overall status is `NOT_EVALUATED`. The safe answer is to preserve the existing
private route and investigate recovery before migration. The tests independently
apply this Boolean calculation and also cover fully proven synthetic candidates.

The process exits successfully for a valid assessment, including unknown or
failed evidence. Automation must read `status`, `selected` and
`manual_profile_independent`; exit status alone is not an access check. Malformed or
unreadable input returns a nonzero exit status without echoing input or paths.

## Recovery and later execution

If the replacement fails, keep running work on its existing private route. Use
the preserved console or recovery channel to inspect transport service state,
route selection, device expiry, grants and SSH effective policy. Restore the
recorded prior state, validate syntax, reload only when valid, and prove a fresh
key-authenticated connection. Never turn a host-key failure into an automatic
trust update or enable public/password access for recovery.

For the interim WireGuard route, recover the existing connection profile from
its private operational record; perform any restart from the recovery channel
only after accounting for active work. Do not schedule blind profile bounces.
Later automation needs an authorized probe, workload-specific timeout/backoff
inputs, bounded retries, concurrency protection and a demonstrated failure test.
None is inferred from the old successful recovery.

Later execution must inventory installed transports, attest the selected route
from the intended client network, complete the canonical matrix and the workload
checks above, then update private connection records. Live qualification and
independent review remain outstanding; this document makes no installation claim.

## Sources

- [Canonical remote access policy](remote-linux-access.md), Architecture,
  Security controls, Setup sequence and Verification matrix: repository policy
  basis for selection, authentication hardening and recovery.
- [OpenSSH client manual](https://man.openbsd.org/ssh_config), `BatchMode`,
  `PreferredAuthentications`, `PasswordAuthentication`,
  `KbdInteractiveAuthentication`, `StrictHostKeyChecking`; current online manual
  retrieved 2026-10-22. Confirm support against the installed version.
- [OpenSSH server manual](https://man.openbsd.org/sshd_config),
  `AuthenticationMethods`, `PasswordAuthentication`,
  `KbdInteractiveAuthentication`, `PermitRootLogin` and `Match`; current online
  manual retrieved 2026-10-22. Effective policy must be inspected per context.
- [Tailscale connection types](https://tailscale.com/kb/1257/connection-types),
  current online documentation retrieved 2026-10-22: private connectivity may be
  direct or relayed; the design is not a direct-path or performance guarantee.
- [Cloudflare client-side SSH](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/use-cases/ssh/ssh-cloudflared-authentication/),
  Connect as a user; current online documentation retrieved 2026-10-22: browser
  authentication in that flow requires separate consideration for headless work.
- [Tailscale subnet routers](https://tailscale.com/kb/1019/subnets), current
  online documentation retrieved 2026-10-22: routing and access controls must be
  configured for devices that do not run the client.
- [rclone SFTP](https://rclone.org/sftp/), SSH Authentication and Host key
  validation, current online documentation retrieved 2026-10-22: configure
  authentication and host-key validation explicitly for this backend.
