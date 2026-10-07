---
name: feedback_classify_failure_layer_before_reporting
description: "Before declaring a host/tool/service down, classify which layer failed (DNS / network / node-offline / auth / app) and re-probe stale alarms — a wrong label sends the next session chasing the wrong fix; anchor identity to stable keys, not churning addresses"
metadata:
  type: feedback
---

A reachability or tool failure is not one thing. It fails at a specific layer, and
the layer decides both the fix and who owns it. Reporting "X is down" without the
layer is a defect: it reads as settled, propagates into the next session, and sends
that session chasing the wrong thing.

The five layers, and how they look from a prompt that all say roughly "can't
connect":

| Signature | Layer | Means | Fix owner |
|---|---|---|---|
| `Could not resolve hostname` | name-resolution | the local VPN/DNS is down | local — bring the tunnel up |
| `ping` times out, node marked offline | node-offline | the box is off or its VPN is down | the box's operator |
| TCP/22 timeout, node online | network path | route never established (e.g. relay-only) | networking, not auth |
| `Permission denied (publickey,password)` + banner | auth/credential | wrong key/user/ACL | credentials |
| connects, command errors | application | the service, not the transport | the app |

**The incident (2026-10-05).** A morning dashboard reported two machines "down for
a second day." A fresh probe showed the first was the machine running the probe
itself (it was never down), and the second had already recovered hours earlier. The
stale alarm was the defect, not the machines. Separately, a shared-in GPU node read
as an auth failure for a whole session of username-guessing — it was simply the
wrong SSH key being offered (auth layer, specific sub-cause), discoverable in one
read of a peer's `~/.ssh/config`.

**How to act on it**

- **Classify before you label.** Name the layer in the report. "NODE_OFFLINE (TCP
  timeout, Tailscale marks it offline)" is actionable; "unreachable" is not.
- **Re-probe stale state.** A failure from an earlier run, a dashboard, or another
  session is a hypothesis until reproduced now. Confirm it still reproduces before
  acting on it or escalating. Yesterday's "down" is today's "already recovered"
  often enough that skipping the re-probe wastes the next session.
- **Prefer a classifier over a bare pass/fail.** A probe that returns the layer
  (`AUTH_OK / AUTH_FAIL / NODE_OFFLINE / DNS_DOWN`) stops the same failure being
  re-raised as a mystery. Reference: `aceengineer-admin/admin/fleet-ssh-probe.sh`.
- **Anchor identity to stable keys, not addresses.** VPN/overlay IPs churn across
  node re-registration; the SSH host-key fingerprint does not. Pin trust to the
  fingerprint (`HostKeyAlias`) so a path/IP change is not misread as an identity or
  auth failure. Never store bare overlay IPs in configs/scripts — they rot silently
  and mimic auth failures.

**Related:** `feedback_absence_of_signal_reads_as_success` (a missing signal reads
greener than a failing one — this is its reachability sibling); the "Verify coverage
assumptions empirically" must-fire rule (enumerate the live set before a coverage
claim).
