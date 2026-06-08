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

## Design
1. **Single-active-venue lease** (reuse F3 #2970 versioned-CAS + fencing). A `refs/heads/dispatch/leases/venue-telegram` lease names the one active venue host. The member-audit + escalation-sweep + bot only run when the local host holds the venue lease (the cron wrapper checks the lease token first; non-holder = no-op). Failover = lease handoff (TTL + liveness, same semantics as F3). **Fencing**: every outbound side effect (Telegram send, GitHub mirror) re-verifies the venue token → a partitioned-but-alive old host cannot double-send.
2. **Delivery contract** (`config/deckhand/`-referenced spec, authored in workspace-hub `docs/ops/telegram-venue-contract.md`):
   - **Idempotency keys**: extend the existing `needs-mirror→mirrored` pattern to a generalized per-message idempotency key (client-ref + content-hash) so a retried send never duplicates.
   - **Retry/dead-letter**: failed sends go to a durable queue with bounded retries; terminal failures land in a dead-letter list + operator alert (JSONL notification surface, per the F5/#2967 decision).
   - **Audit trail**: every client-facing send appended to an audit log (who/when/scope/idempotency-key/result) so cross-host continuity is provable.
3. **Role binding**: the comms-dispatch role overlay (F1) declares the venue lease + the 3 venue crons as role-managed-but-external-owned (preserved_external from F2) so a failover comms-dispatch host reproduces identical venue behavior.

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
| test_audit_records_each_send | a send | audit row with key/scope/result |
| test_parity_verifier_flags_missing_contract_field | deckhand config missing a field | verifier reports gap |

## Acceptance Criteria
- [ ] Exactly one host runs the venue (lease-gated); a second host no-ops (test-proven).
- [ ] Failover handoff via the F3 versioned-CAS lease; fencing prevents a partitioned old host from double-sending (test-proven).
- [ ] Idempotency-key dedup + retry/dead-letter + audit trail specified in the contract and verifiable.
- [ ] Parity verifier checks deckhand venue config against the contract; cross-repo deckhand issue filed for the send-path implementation.
- [ ] `uv run pytest tests/operations/test_venue_lease.py -v` passes; no regression.
- [ ] Cross-review (T3): Claude + Codex (+ Gemini if available).

## Risks and Open Questions
- **Risk:** the venue lease must NOT fight the deckhand sweep's existing `needs-mirror→mirrored` idempotency — build on it, don't duplicate. The lease gates *who runs*, the label-swap dedups *what's mirrored*.
- **Risk:** cross-repo drift — the contract in workspace-hub and the implementation in deckhand can diverge; the parity verifier is the guard (run in deckhand CI).
- **Open (user):** should F4 actually move the venue crons behind the lease now (touches live a2 client automation), or ship the contract + lease + verifier and gate the live cutover behind a separate approved step? Recommendation: **contract + lease + verifier this slice; live cutover is a separate operator-approved step** (a2 runs live client SLA — highest-stakes host in the fleet).
- **Open (user):** is a second comms-dispatch host actually planned (failover), or is single-active enough for now? If no failover host exists yet, F4 still delivers the single-active *guarantee* (prevents accidental double-run) even without a standby.

## Complexity: T3
Cross-repo, live client venue, reuses F3 lease/fencing; full TDD; 3-agent review.
