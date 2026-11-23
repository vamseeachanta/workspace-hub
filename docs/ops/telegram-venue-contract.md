# Telegram Venue Consistency Contract (F4)

> Issue: [#2971](https://github.com/vamseeachanta/workspace-hub/issues/2971) (F4) · Parent: [#2967](https://github.com/vamseeachanta/workspace-hub/issues/2967)
> Depends on: F1 role overlay (`comms-dispatch`), F3 dispatch lease ([#2970](https://github.com/vamseeachanta/workspace-hub/issues/2970), `scripts/operations/dispatch_lease.py`), F3 provider-routing policy.
> Conformance verifier: [`scripts/operations/venue_audit.py`](../../scripts/operations/venue_audit.py).

## Purpose

Telegram is a **client delivery venue**, not just a control plane. The deckhand bots
(member-audit, escalation sweep, scope routing, onboarding, WhatsApp bridge) currently
live on `ace-linux-2`. Client experience must not depend on which host runs the bot.

This document is the **cross-repo contract** the deckhand venue must satisfy for
**machine-independent, exactly-once delivery**. The contract lives here (workspace-hub);
deckhand *implements* the send-path against it. The parity verifier
(`venue_audit.py`) checks a deckhand config for conformance and **fails closed**.

---

## `contract_version: 1`

- This contract is versioned. The current version is **1**.
- Deckhand **pins** the contract version it implements in its venue config
  (`config/deckhand/policy.yml` → `venue_contract.contract_version`).
- The parity verifier **fails closed** on a deckhand config that declares an
  **older or unknown** contract version (`declared < current` ⇒ gap). A config that
  declares no version at all is also a gap. Forward declarations (`declared > current`)
  are *not* a conformance gap for this verifier — this verifier only knows version 1 —
  but the operator should upgrade the contract doc + verifier in lockstep.
- Bump the version whenever a normative ("MUST") clause below changes in a way that an
  older deckhand implementation would silently violate.

---

## 1. Single-active venue (write-side gating)

Exactly one host may run **write-side** venue functions at a time. Write-side functions
are those that produce externally-visible side effects in the client's view:

- the escalation sweep (mirrors `needs-mirror` issues to Telegram),
- bot outbound sends (any message the venue emits to a client channel),
- onboarding let-through actions, scope→channel routing emits.

These run **only on the host that currently holds the `venue-telegram` lease** (F3,
`scripts/operations/dispatch_lease.py`, ref `refs/heads/dispatch/leases/venue-telegram`).
A host MUST call `verify_token` (fencing) **immediately before** each externally-visible
send, and abort if it has been fenced out. This is what guarantees no double-send across
a failover window even under clock skew or partition.

**Read-only** functions are **not** lease-gated and may run anywhere, anytime:

- member-audit (read membership, report drift),
- this parity verifier (`venue_audit.py`),
- any reporting/dashboard read.

Rationale: read-only work has no client-visible side effect, so gating it would only
reduce availability with no exactly-once benefit.

---

## 2. Ordered delivery state machine

Every client-visible delivery follows this canonical order. **Never** reorder it.

```
reserve(idempotency_key)  ->  send  ->  record audit  ->  swap label
```

1. **reserve(idempotency_key)** — claim the per-message idempotency key in a durable
   dedup store *before* sending. If the key is already in a terminal `sent` state, this
   message was already delivered: **do not re-send** (skip to step 4 if the label still
   needs reconciling).
2. **send** — emit to the client channel. This is the externally-visible side effect;
   `verify_token` (lease fencing) MUST pass immediately before it.
3. **record audit** — write the PII-safe audit row (see §5) recording that the send
   succeeded. The audit/dedup record is the **source of truth** for "was this sent?".
4. **swap label** — flip the durable mirror-state marker (`needs-mirror -> mirrored`).

### Recovery rules for partial-failure cracks

The dangerous window is *between* steps. Recovery is asymmetric on purpose:

| Crack | State | Recovery |
|---|---|---|
| Reserved but not sent | key reserved, no `sent` audit row | retry the **send** (still idempotent — the key is held); the reservation prevents a second concurrent worker from also sending. |
| **Sent but label not swapped** | `sent` audit/dedup row exists, label still `needs-mirror` | the audit/dedup record is the **source of truth**: the message **was delivered**. **Do NOT re-send.** Retry **only the label swap**. |
| Audit recorded, label not swapped | same as above | same: retry only the label swap. |

**Invariants:**

- **Never swap the label before the send completes.** A premature swap would mark the
  message mirrored while it is still un-sent, and the idempotent re-run would then skip
  it forever (silent drop).
- **The per-message idempotency key guards the outbound send.** Two workers (or a retry)
  cannot both pass `reserve` for the same key, so the send happens at most once.
- **The label remains the durable mirror-state marker.** It is the coarse-grained,
  GitHub-visible "this issue has been mirrored" signal that makes the sweep re-runnable.

### Reconciliation with deckhand's existing label swap

Deckhand's escalation sweep already has an idempotency mechanism: a GitHub label swap
`needs-mirror -> mirrored`, so re-running the sweep does not re-mirror. The SLA clock is
the issue `createdAt`; `sla_hours: 24`.

This contract **keeps that label swap** as the durable, coarse-grained mirror-state
marker (step 4). It **adds** the finer per-message idempotency key (step 1) that guards
the actual outbound send. The two are complementary:

- The **label** answers "has this issue been mirrored?" at the issue granularity and
  survives process restarts because it lives on GitHub.
- The **key** answers "has this exact message been sent?" at the message granularity and
  closes the sent-but-label-not-swapped crack that the label alone cannot (a crash
  between send and swap would, with the label alone, re-send on the next sweep).

A conformant deckhand declares **both**: the escalation label-swap config AND the
per-message idempotency scheme.

---

## 3. Idempotency key

The idempotency key is:

```
idempotency_key = client-ref + message-type + monotonic-seq
```

- **client-ref** — a *non-reversible* reference to the client/channel (an opaque id, not
  a phone number, handle, or any reversible identifier; see §5).
- **message-type** — the venue message class (e.g. `escalation`, `onboarding`,
  `scope-route`).
- **monotonic-seq** — a per-(client-ref, message-type) monotonically increasing sequence.

**It is NOT a raw content hash.** A content hash would (a) collide two legitimately
distinct messages that happen to have identical text, suppressing the second, and (b)
leak content into the key space (the key is logged in the audit row, which must be
PII-safe). The composite key is stable, content-independent, and safe to persist.

The deckhand config declares this scheme so the verifier can confirm it is
composite-key-based and not content-hash-based.

---

## 4. Retry and dead-letter

- Outbound sends use **bounded retries** (finite attempt count with backoff) — never an
  unbounded retry loop.
- On **terminal failure** (retries exhausted, or a non-retryable error), the message goes
  to a **dead-letter target** AND an **operator alert** fires.
- The operator alert is emitted as **JSONL via `scripts/notify.sh`** (the workspace-hub
  async-notification writer; appends one event to `logs/notifications/YYYY-MM-DD.jsonl`).
- A dead-lettered message is **not** silently dropped and is **not** auto-retried; it
  requires operator action. The label is **not** swapped for a dead-lettered message
  (it was not delivered), so the issue remains visibly `needs-mirror`.

The deckhand config declares a `dead_letter` target so the verifier can confirm one
exists.

---

## 5. PII-safe audit

Audit rows record **only** the operational fact of delivery, never the payload.

**Each audit row stores ONLY:**

- `host` — which host performed the send (the lease holder at send time),
- `when` — UTC timestamp of the send,
- `scope` — the venue scope/channel class (e.g. `escalation`, `onboarding`),
- `idempotency_key` — the composite key from §3,
- `result` — `sent` | `dead-letter` | `retry`.

**An audit row MUST NEVER contain:**

- **chat content** (no message body, no quoted text, no attachments metadata),
- a **reversible client identifier** (no phone number, no Telegram handle/user-id, no
  email — `client-ref` is opaque and non-reversible),
- a **content-hash** (a hash is a fingerprint of content and can confirm/guess payloads;
  it is also why the idempotency key is composite, not a hash — see §3).

**Retention:** audit rows are retained for a bounded window of **90 days**, then purged.
The window is long enough for delivery-dispute reconciliation and short enough to limit
exposure.

**Access control:** audit rows are operator-only. They live on the host / in the deckhand
operator store, are not world-readable, and are never mirrored into a client-visible
channel. The deckhand `audit` config declares `pii_safe: true` to assert it conforms to
this section; the verifier treats a missing or false `pii_safe` as a gap (fail closed).

---

## 6. Cross-repo boundary

| Lives here (workspace-hub) | Lives in deckhand |
|---|---|
| This contract (normative spec). | The venue config that declares conformance (`config/deckhand/{scopes.yml, policy.yml, routing/*.yaml}`). |
| The parity verifier (`venue_audit.py`). | The **send-path implementation**: lease-token **fencing** around each send, **retry/dead-letter** machinery, the **audit emitter**. |
| The `venue-telegram` lease primitive (F3). | The call sites that acquire/verify the lease before write-side work. |

**Deckhand follow-up (not in this repo):** deckhand must implement, in its own repo,
(a) lease-token fencing immediately before every outbound send, (b) bounded retry +
dead-letter + `scripts/notify.sh` operator alert, and (c) the PII-safe audit emitter
writing the row schema in §5. Track that as a deckhand issue referencing this contract
version. Until deckhand declares conformance in its config, `venue_audit.py` reports
gaps.

---

## Conformance summary (what `venue_audit.py` checks)

A conformant deckhand venue config declares, at minimum:

1. `venue_contract.contract_version` ≥ this document's `contract_version`.
2. An **idempotency scheme** that is composite (`client-ref + message-type + monotonic-seq`),
   not a content hash.
3. A **dead-letter** target.
4. An **audit** config with `pii_safe: true`.
5. The **escalation label-swap** (`needs-mirror -> mirrored`).

Any missing field, an older/unknown contract version, or `pii_safe` not true is a **gap**;
the verifier exits non-zero.
