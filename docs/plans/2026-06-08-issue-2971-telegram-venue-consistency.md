# Plan for #2971 (F4): Telegram-as-venue consistency

> **Status:** draft → plan-review
> **Complexity:** T3 (cross-repo: workspace-hub contract + deckhand implementation; live client venue)
> **Date:** 2026-06-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2971
> **Parent epic:** https://github.com/vamseeachanta/workspace-hub/issues/2967
> **Depends on:** F1 #2968 (comms-dispatch role), F3 #2970 (versioned-CAS lease + fencing)
> **Coordinates:** #2720 (control-plane lease), #2742 (Win/macOS telegram parity)
> **Client:** N/A (governs client venues; no client data in code)

---

## Resource Intelligence Summary

### Existing substrate (mature — F4 closes consistency/failover gaps, not greenfield)
- **deckhand repo** (`/mnt/local-analysis/deckhand`, runs on ace-linux-2) has a rich, git-tracked venue config: `config/deckhand/{scopes.yml, policy.yml, platforms.yml, capability-cards.yml, chat-charter.md, voice-client-channels.md, routing/{audiences,escalation,paths,taxonomy,voice}.yaml}` + `validate_routing.py`.
- **Escalation already has an idempotency mechanism**: `routing/escalation.yaml` — filing sets `needs-mirror`; the host-cron sweep swaps it to `mirrored` (re-running the sweep does NOT re-mirror). SLA clock = original `createdAt`.
- Venue automation = 3 crons on ace-linux-2 (member-audit, escalation-sweep every 15 min, patch-health) — now classified `preserved_external` by F2.
- registry `telegram_hermes.{telegram_mode: coordinator|worker, dispatch_enabled}` per machine; Hermes gateway + WhatsApp bridge live on a2.

### Gaps identified (the F4 work; Codex epic-review #3)
1. **No single-active-venue guarantee.** If a failover/second host started the bot or the escalation sweep, clients would get **duplicate messages / double SLA mirrors**. Nothing today enforces "exactly one host runs the venue."
2. **No explicit retry/dead-letter** for outbound sends (a failed Telegram/WhatsApp send is not durably queued/alerted).
3. **No unified audit trail** ("same user saw same result regardless of serving host").
4. Venue behavior is host-bound by convention, not by the comms-dispatch role overlay → a failover host wouldn't reproduce it deterministically.

### Evidence
- deckhand config tree + escalation.yaml read (idempotency via label-swap confirmed). policy.yml grep (no retry/dead-letter/single-active). No bot single-instance guard found. registry telegram_hermes. Source count: 6. ✔

---

## Deliverable
A venue-consistency **contract** (in workspace-hub) guaranteeing exactly-one-active venue host with deterministic failover, plus durable delivery (retry/dead-letter) and a unified audit trail — so a client's Telegram experience is identical regardless of which host serves it; with the deckhand-side implementation tracked as a cross-repo handoff.

## Scope boundary (cross-repo)
- **workspace-hub (this issue):** the venue contract + the single-active-venue lease integration (reuse F3) + a parity/consistency verifier + the comms-dispatch role binding. 
- **deckhand (cross-repo follow-up issue, filed by this plan):** wire the bot/sweep send-path to honor the lease token (fencing), the retry/dead-letter queue, and the audit emitter. deckhand owns its runtime; workspace-hub owns the contract it must satisfy.

## Design (Codex MAJOR folded)

### 1. Lease per CAPABILITY, not one gate for all (Codex #4)
Venue functions are split by side-effect risk — NOT a single blanket lease:
| Function | Side-effect | Lease/fencing? |
|---|---|---|
| escalation-sweep (mirrors → client repos) | **write** (client-visible) | single-active + fenced |
| bot outbound replies/sends | **write** (client-visible) | single-active + fenced |
| member-audit (roster-diff alert) | low/read-mostly | safe multi-host OR single, NOT fenced |
| parity verifier | read-only | multi-host fine |
Only the write-side-effect functions go behind `holds_venue()`; read-only functions are not gated (so they can't be silently stopped by lease trouble).

### 2. Independent "no-active-venue / stale-SLA" detector (Codex #1 — the load-bearing safety add)
Gating a cron behind `holds_venue()` introduces a fleet-wide **silent-stop** risk (CAS fails / clock skew / all hosts no-op → `needs-mirror` ages forever). So an **absence detector runs DECOUPLED from the venue lease** (e.g. on the control-plane host's own schedule): alert if EITHER no valid venue holder exists OR any `needs-mirror`/last-sweep-success heartbeat is older than a threshold (< SLA). The detector never depends on the lease it monitors. JSONL + escalation alert.

### 3. Ordered delivery state machine (Codex #2 — reconcile the two idempotency layers)
The existing GitHub `needs-mirror→mirrored` label-swap (mirror state) and a new per-message delivery key must not disagree. Define ONE ordered, recoverable state machine:
`reserve(idempotency_key) → send → record audit → swap label`, with each step checking the prior. Recovery rules cover every partial-failure crack: sent-but-label-not-swapped (audit/dedup record is the source of truth → do NOT re-send, retry only the label swap), label-swapped-before-send (forbidden ordering — send precedes swap), etc. The label-swap remains the durable mirror-state marker; the delivery key guards the outbound send; the audit record reconciles them.

### 4. Delivery guarantees
- **Idempotency key** = `client-ref + message-type + monotonic-seq` (NOT raw content-hash — see PII below). Retried send with same key → single delivery.
- **Retry/dead-letter**: bounded retries; terminal failure → dead-letter + operator alert (JSONL, per #2967 decision).

### 5. PII-safe audit (Codex #5)
Audit rows store `who(host)/when/scope/idempotency-key/result` ONLY — **never chat content, and no reversible client identifier or content-hash** that could correlate sensitive text. Specify redaction, retention window, and access control in the contract. The audit proves cross-host continuity without storing what was said.

### 6. Cross-repo version pinning (Codex #3)
The contract carries a `contract_version` + hash; deckhand pins the version it implements; the parity verifier (run in deckhand CI) **fails closed** when deckhand's schema is older/unknown vs the pinned contract. Defines a compat window.

### 7. Role binding
The comms-dispatch role overlay (F1) declares the venue lease + the write-side venue crons as preserved_external (F2) so a failover comms-dispatch host reproduces identical venue behavior; secrets via env.

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | `docs/ops/telegram-venue-contract.md` | the canonical venue-consistency contract |
| Create | `scripts/operations/venue_lease.py` | single-active-venue lease (wraps F3 lease core) + `holds_venue()` check + CLI |
| Create | `scripts/operations/venue_audit.py` | verify deckhand venue config + live crons satisfy the contract (parity check) |
| Create | `tests/operations/test_venue_lease.py` | TDD |
| Modify | `config/workstations/registry.yaml` | venue lease ownership + comms-dispatch venue binding |
| (cross-repo) | deckhand issue | wire send-path to lease token + retry/dead-letter + audit |

## TDD Test List
| Test | Verifies | Expected |
|---|---|---|
| test_only_lease_holder_runs_venue | non-holder host | `holds_venue()` False → cron no-ops |
| test_venue_failover_handoff | holder fails liveness past TTL | lease reclaimable via CAS (reuse F3) |
| test_fencing_superseded_host_no_send | old host token superseded | send aborts (no double-message) |
| test_idempotency_key_dedups_retry | same message retried | single delivery |
| test_dead_letter_on_terminal_failure | send fails past retries | dead-letter + notification |
| test_audit_records_each_send | a send | audit row with key/scope/result, NO content/reversible-id |
| test_parity_verifier_flags_missing_contract_field | deckhand config missing a field | verifier reports gap |
| test_read_only_functions_not_lease_gated | member-audit/parity | run regardless of venue lease (no silent stop) |
| test_absence_detector_alerts_no_holder | no valid venue holder | alert fires (decoupled from lease) |
| test_absence_detector_alerts_stale_mirror | needs-mirror older than threshold | alert fires |
| test_delivery_sm_sent_but_label_unswapped_no_resend | partial failure | retries label swap, does NOT re-send |
| test_contract_version_mismatch_fails_ci | deckhand pins old/unknown schema | parity verifier fails closed |

## Acceptance Criteria
- [ ] Exactly one host runs the venue (lease-gated); a second host no-ops (test-proven).
- [ ] Failover handoff via the F3 versioned-CAS lease; fencing prevents a partitioned old host from double-sending (test-proven).
- [ ] Idempotency-key dedup + retry/dead-letter + audit trail specified in the contract and verifiable.
- [ ] Parity verifier checks deckhand venue config against the contract; cross-repo deckhand issue filed for the send-path implementation.
- [ ] `uv run pytest tests/operations/test_venue_lease.py -v` passes; no regression.
- [ ] Only write-side functions (escalation-sweep, bot send) are lease-gated; read-only (member-audit, parity) are NOT gated (no silent-stop).
- [ ] Independent absence detector (decoupled from the venue lease) alerts on no-holder OR stale-mirror before SLA breach.
- [ ] Ordered delivery state machine with recovery rules reconciles the label-swap + delivery-key layers (test-proven for the sent-but-unswapped crack).
- [ ] Audit stores NO chat content / no reversible client id / no content-hash; redaction + retention + access specified.
- [ ] Contract carries a version+hash; deckhand parity CI fails closed on schema mismatch.
- [ ] Cross-review (T3): Claude + Codex (+ Gemini if available). **Codex r1 = MAJOR; folded.**

## Risks and Open Questions
- **Risk:** the venue lease must NOT fight the deckhand sweep's existing `needs-mirror→mirrored` idempotency — build on it, don't duplicate. The lease gates *who runs*, the label-swap dedups *what's mirrored*.
- **Risk:** cross-repo drift — the contract in workspace-hub and the implementation in deckhand can diverge; the parity verifier is the guard (run in deckhand CI).
- **Open (user):** should F4 actually move the venue crons behind the lease now (touches live a2 client automation), or ship the contract + lease + verifier and gate the live cutover behind a separate approved step? Recommendation: **contract + lease + verifier this slice; live cutover is a separate operator-approved step** (a2 runs live client SLA — highest-stakes host in the fleet).
- **Open (user):** is a second comms-dispatch host actually planned (failover), or is single-active enough for now? If no failover host exists yet, F4 still delivers the single-active *guarantee* (prevents accidental double-run) even without a standby.

## Adversarial Review Summary
| Provider | Verdict | Key findings (folded) |
|---|---|---|
| Codex r1 | **MAJOR → resolved** | (1) lease-gating creates fleet-wide silent-stop → independent absence detector decoupled from the lease; (2) two idempotency layers can disagree → ordered delivery state machine + recovery rules; (3) cross-repo drift → contract version+hash pin, deckhand CI fails closed; (4) "single-active" too broad → split by side-effect risk (only write functions gated/fenced); (5) audit PII leak → no content/no reversible id/no content-hash, redaction+retention+access. |
| Gemini | pending/optional | dispatch if quota (T3 → 3-agent) |

**Overall:** MAJOR addressed in-plan; remaining gate = user approval.

## Complexity: T3
Cross-repo, live client venue, reuses F3 lease/fencing; full TDD; 3-agent review.
