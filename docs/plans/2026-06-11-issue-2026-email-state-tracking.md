# Plan for #2026: Email state tracking system

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2026
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:claude
> **Review artifacts:** completed failed rounds are preserved at `scripts/review/results/2026-06-11-plan-2026-r1-*`, `scripts/review/results/2026-06-11-plan-2026-r2-*`, `scripts/review/results/2026-06-11-plan-2026-r3/`, `scripts/review/results/2026-06-11-plan-2026-r4/`, `scripts/review/results/2026-06-11-plan-2026-r5/`, `scripts/review/results/2026-06-11-plan-2026-r6/`, `scripts/review/results/2026-06-11-plan-2026-r7/`, `scripts/review/results/2026-06-11-plan-2026-r8/`, and `scripts/review/results/2026-06-11-plan-2026-r9/`. This draft has been patched after R9 and requires a fresh R10 adversarial review before any `status:plan-review` label.

---

## Resource Intelligence Summary

Planning execution mode: `parallel-readonly` for resource intel and plan review; implementation mode after approval should be `single-lane` because the state module, tests, and docs share one narrow write surface.

### Existing repo code

- Found: `docs/design/email-as-queue.md` defines #2017 as the contract source and assigns queue-state storage implementation to #2026. It explicitly says Gmail-side delete/archive automation belongs to #2423, and existing routing does not add new Gmail mutations.
- Found: `docs/design/email-queue-state-schema.yaml` defines the five states, JSONL entry shape, snapshot key format `{account_id}::{thread_id}`, writer identity, snapshot metadata, and learning-log events.
- Found: `tests/email/test_state_machine_contract.py` already encodes the missing #2026 storage module as xfailed contract tests for `transition`, `lookup`, `count_entries`, and `reactivate_reply`.
- Found: `scripts/email/gmail-archive-extract.py`, `scripts/email/gmail-digest.py`, `scripts/email/email-routing.yaml`, `scripts/email/spam-detection-rules.yaml`, and CRE schemas already exist. They are inputs/adjacent tools, not the queue-state implementation.
- Gap: `scripts/email/queue_state.py` and `scripts/email/state/` do not exist.
- Gap: no implemented state report currently expresses "mailbox empty" as "no pending work."

### Standards

Not applicable as an engineering standard. Security/legal rules still apply:

- Do not hardcode secrets or OAuth tokens.
- Do not commit runtime email state containing real thread metadata.
- Run `scripts/legal/legal-sanity-scan.sh` before any commit containing implementation artifacts.

### LLM Wiki pages consulted

No relevant LLM wiki pages. This is workspace-hub email automation infrastructure, not a client wiki or engineering-domain knowledge issue.

### Documents consulted

- Issue #2026 body and comments: current implementation target is state tracking; user clarified on 2026-06-11 that this automation pass covers only `vamsee.achanta@aceengineer.com` and `achantav@gmail.com`, and that "mailbox empty" means no pending work.
- Issue #2017: closed as done; #2017 design artifacts are the contract source.
- Issue #2024: open; extraction pipeline depends on #2026 state storage.
- Issue #2423: open; Gmail-side archive/delete automation is a follow-on and must not be folded into this issue.
- `docs/plans/2026-04-24-issue-2026-plan.md`: stale draft. It is useful for prior thinking but is superseded by this plan because it is ace-only, relies on unverified Gmail label mutation, lacks current template fields, and predates the two-account scope clarification.
- `docs/plans/2026-04-20-issue-2017-plan.md`: design history for R1/R2 defects around dedup and xfail/import behavior.
- `docs/design/email-as-queue-workflow.md`: older workflow design that still references three accounts, Gmail label source-of-truth behavior, and all-account cleanup rollout. This plan must update or explicitly supersede those stale sections.
- `docs/document-intelligence/data-intelligence-map.md`: consulted as the required intelligence entry point. It does not add email-specific requirements.
- `config/agents/codex/MEMORY.runtime.md`: loaded at session start; relevant durable memories include "Check parallel work", "Never offer self-label plan-approved", "Email cross-noise", "Codex needs pushed artifact", and "Pre-completion cleanup audit gate."

### Gaps identified

- Implement the queue-state storage module.
- Implement state transition validation and persistence.
- Implement snapshot rebuild and metadata freshness checks.
- Implement grace-period local purge sweep.
- Implement reactivation semantics, including missing extraction logging.
- Implement account allowlist/config so only `ace` and `personal` are in scope for this pass. `skestates` remains out of scope unless a future issue re-authorizes it.
- Extend the schema contract for `triggering_message_id` and decision-needed reporting metadata.
- Define the public path-first wrapper API required by the existing #2017 xfail tests.
- Define the account config and inbox snapshot contracts that let the state report evaluate unknown in-scope Gmail threads.
- Implement a pending-work report where "empty mailbox" means zero known pending work in local state plus zero in-scope unknowns when the caller supplies an inbox snapshot. Local state alone cannot prove that Gmail has no untracked threads.
- Implement Gmail label creation/mirroring for queue-state labels only; it must not archive or delete Gmail.
- Reconcile stale April plan language and design docs that say ace-only, 3 accounts, repo-tracked runtime state, or full-account Gmail mutation.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-11T20:21:48Z via `gh issue view`):

```
#2017 - CLOSED - design: Email-as-Queue workflow - extract data, delete when done, re-activate on reply
labels: enhancement, priority:high, cat:infrastructure, status:done, agent:codex

#2024 - OPEN - build: gmail-extract-and-act pipeline - rewrite gmail-archive-extract.py for extract-first, delete-later queue model
labels: enhancement, priority:medium, cat:data-pipeline, domain:automation, machine:dev-primary, dispatch:ready, gate:completeness, lane:claude

#2026 - OPEN - build: Email state tracking system - Gmail labels + local state log + grace period deletion
labels: enhancement, priority:medium, cat:infrastructure, domain:automation, machine:dev-primary, dispatch:ready, gate:completeness, lane:claude

#2423 - OPEN - feat: automated Gmail-side delete/archive for email-as-queue (follow-on to #2017)
labels: enhancement, priority:medium, cat:infrastructure, domain:automation, machine:dev-primary, dispatch:ready, gate:completeness, lane:claude
```

**File existence** (verified 2026-06-11):

```
EXISTS: docs/design/email-as-queue.md
EXISTS: docs/design/email-queue-state-schema.yaml
EXISTS: scripts/email/email-routing.yaml
EXISTS: scripts/email/gmail-archive-extract.py
EXISTS: scripts/email/gmail-digest.py
EXISTS: scripts/email/spam-detection-rules.yaml
EXISTS: tests/email/test_state_machine_contract.py
MISSING: scripts/email/queue_state.py
MISSING: scripts/email/state/
```

**Line excerpts**:

`docs/design/email-as-queue.md:16-18`

```
Pipeline orchestration belongs to #2024. Queue-state storage implementation belongs to #2026. New Gmail-side delete/archive automation belongs to #2423.

Existing `gmail-archive-extract.py` routing behavior is grandfathered production infrastructure. This design does not add new Gmail mutations.
```

`docs/design/email-as-queue.md:37-39`

```
`completed` threads are retained through a seven-day grace window. After the grace window, local queue state transitions to `purged`; Gmail content is not touched by this contract.
```

`docs/design/email-as-queue.md:24-29`

```
Queue state is local-only in v1:

- Append-only event log: `scripts/email/queue-state.jsonl`.
- Materialized read snapshot: `scripts/email/queue-state-snapshot.yaml`.
- Snapshot freshness metadata: `scripts/email/queue-state-snapshot.meta.yaml`.
- Learning/correction log: `scripts/email/queue-learning-log.jsonl`.
```

This excerpt conflicts with this plan's chosen runtime path under `~/.hermes/email-state/`; implementation must update the design doc to distinguish tracked schema files from private runtime state.

`docs/design/email-queue-state-schema.yaml:22-67`

```
queue_state_entry:
  required:
    - account_id
    - thread_id
    - from_state
    - to_state
    - ts_utc
    - writer_identity
  properties:
    completed_at:
      type: string
      format: iso8601-utc-z
dedup_key:
    - account_id
    - thread_id
    - from_state
    - to_state
```

This excerpt conflicts with D5 until the schema is updated to add `triggering_message_id` and revise dedup semantics.

`docs/design/email-as-queue-workflow.md` (stale-section summary, not a verbatim excerpt):

Older workflow text still references `~/.hermes/email-state.yaml`, `skestates`, and all-account deletion rollout language. This plan will update or mark those sections superseded so future agents do not revive the stale 3-account/delete-first behavior.

`tests/email/test_state_machine_contract.py:6-15`

```
def require_queue_state():
    try:
        return importlib.import_module("scripts.email.queue_state")
    except ModuleNotFoundError as exc:
        pytest.fail(f"pending #2026 storage module: {exc}")

@pytest.mark.xfail(reason="pending #2026 storage impl")
def test_transition_inbound_to_extracted_writes_log(tmp_path):
```

**Gap proofs**:

```
$ uv run python -c "import scripts.email.queue_state; print(scripts.email.queue_state)"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'scripts.email.queue_state'
```

**Reproduction proofs** (verify-against-repo-state):

```
$ uv run pytest tests/email/test_state_machine_contract.py -q --runxfail
FFF                                                                      [100%]
=================================== FAILURES ===================================
_______________ test_transition_inbound_to_extracted_writes_log ________________
ModuleNotFoundError: No module named 'scripts.email.queue_state'
...
E           Failed: pending #2026 storage module: No module named 'scripts.email.queue_state'
...
_____________ test_transition_retry_preserves_dedup_under_fresh_ts _____________
ModuleNotFoundError: No module named 'scripts.email.queue_state'
...
____________ test_purged_reactivates_on_reply_with_extraction_link _____________
ModuleNotFoundError: No module named 'scripts.email.queue_state'
```

- Reproduced at: 2026-06-11T20:21:48Z.
- Failure mode observed matches issue claim: YES. The storage module is absent; contract tests fail under `--runxfail`.

Source count: 9 distinct sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-11-issue-2026-email-state-tracking.md` |
| Superseded draft marker | `docs/plans/2026-04-24-issue-2026-plan.md` |
| Plan index | `docs/plans/README.md` |
| Existing contract docs | `docs/design/email-as-queue.md`, `docs/design/email-as-queue-workflow.md`, `docs/design/email-queue-state-schema.yaml` |
| Tests | `tests/email/test_state_machine_contract.py`, `tests/email/test_email_queue_state.py` |
| Implementation | `scripts/email/queue_state.py`, `scripts/email/email-queue-state.py`, `scripts/email/state/*.py` |
| Runtime state directory | `~/.hermes/email-state/` by default, overrideable via `EMAIL_QUEUE_STATE_DIR` |
| Optional local runtime config | `~/.hermes/email-state/accounts.yaml` |
| Implementation notes requested by user | `docs/reports/2026-06-11-issue-2026-implementation-notes.html` |
| Failed review rounds | `scripts/review/results/2026-06-11-plan-2026-r1-*`, `scripts/review/results/2026-06-11-plan-2026-r2-*`, `scripts/review/results/2026-06-11-plan-2026-r3/`, `scripts/review/results/2026-06-11-plan-2026-r4/`, `scripts/review/results/2026-06-11-plan-2026-r5/`, `scripts/review/results/2026-06-11-plan-2026-r6/`, `scripts/review/results/2026-06-11-plan-2026-r7/`, `scripts/review/results/2026-06-11-plan-2026-r8/`, `scripts/review/results/2026-06-11-plan-2026-r9/` |

---

## Deliverable

A local queue-state storage and reporting module for the two authorized Gmail accounts that can tell whether mailbox work is pending, while keeping Gmail archive/delete automation out of scope.

---

## Design Decisions

### D1 - Runtime State Location

Runtime email state will default to `~/.hermes/email-state/`, not a tracked repo path, because it may contain real thread IDs, sender-derived metadata, and extraction paths. The repo owns schemas, tests, and code; the local runtime owns private state.

Tests will use temp directories through path-first log paths. Higher-level helper tests may also cover `EMAIL_QUEUE_STATE_DIR`.

Implementation must update `docs/design/email-as-queue.md` and `docs/design/email-as-queue-workflow.md` to clarify that the repo-tracked files are schemas/design artifacts, while the live JSONL/snapshot/log files are private runtime artifacts under the configured state directory.

### D2 - Account Scope and Config

This pass supports only two account aliases:

- `ace` for `vamsee.achanta@aceengineer.com`
- `personal` for `achantav@gmail.com`

Tracked code should not need to hardcode the literal email addresses in tests. Production account email mapping should come from local config/credentials at `~/.hermes/email-state/accounts.yaml` by default, overrideable via `EMAIL_QUEUE_ACCOUNTS_CONFIG`.

Config schema:

```yaml
accounts:
  ace:
    email: vamsee.achanta@aceengineer.com
    enabled: true
  personal:
    email: achantav@gmail.com
    enabled: true
  skestates:
    email: skestatesinc@gmail.com
    enabled: false
```

If the local config is absent, the default scope enables aliases `ace` and `personal` only; literal email normalization is unavailable until a local config supplies the email mapping. Tests that normalize literal emails must use a temp config file and set `EMAIL_QUEUE_ACCOUNTS_CONFIG`.

The config may include disabled aliases solely so the report can distinguish "known but out of scope" from "literal email cannot be mapped." Active processing remains limited to enabled `ace` and `personal`. The low-level state store may persist any `account_id` string so existing contract tests using `user@example.com` keep working; account-scope enforcement belongs to the report/ingest/label boundary, not the raw `transition()` primitive. The account-scope layer must reject or report disabled `skestates` and `skestatesinc@gmail.com` as out of scope unless a future issue changes the allowlist. Report counts must normalize local snapshot records through the same account scope: enabled records contribute to pending/tracked counts, disabled or unknown local records are reported in separate warning buckets and cannot make `mailbox_empty` false for #2026.

### D3 - Pending Work Semantics

"Mailbox empty" means there is no pending work for any known in-scope thread and, when an inbox snapshot is supplied, no unknown in-scope Gmail thread. Non-pending tracked threads may be in these durable buckets:

- `awaiting-reply`
- `completed`
- `purged`
- `extracted` with no action pending

Pending work classes are:

- `inbound`
- any existing contract state carrying `needs_user_decision: true`
- any existing contract state carrying `needs_schema: true`
- unknown in-scope Gmail threads present in a supplied inbox snapshot but absent from local state

`needs_user_decision` is not a sixth state. It will be added to the schema as a boolean metadata field on queue entries and snapshots. `needs_schema` already exists in the schema and must count as pending work. Snapshot materialization is last-event-wins: absent boolean metadata on a later state event clears previous `needs_user_decision` and `needs_schema` values unless the event explicitly carries `true`. Completion materialization is also explicit: every `to_state="completed"` transition stamps `completed_at` from an explicit `completed_at` argument when supplied, otherwise from `ts_utc`; non-completed transitions clear `completed_at`. Message-baseline materialization is explicit: when a state event carries `triggering_message_id`, it updates `last_seen_message_id`; when it carries `received_at_utc`, it updates `last_seen_received_at_utc`; if `received_at_utc` is absent but `triggering_message_id` is present, the baseline timestamp falls back to `ts_utc`. Events with no message id leave the prior baseline unchanged and may therefore produce `baseline_missing` in reports/checkers. Cycle materialization is explicit: reactivation events stamp `cycle_started_at = ts_utc`; non-reactivation events must have `ts_utc >= current.cycle_started_at` when the current snapshot has a cycle start. `pending_work_report()` counts from the snapshot, not from historical log rows. The report must return a structured object with per-account counts, `tracked_empty`, `mailbox_empty`, `unknown_status`, and `unknown_count`.

Local state alone can only prove "no pending work among tracked threads." To prove "no unknown/unclassified in-scope threads", `pending_work_report()` must accept an optional caller-supplied inbox snapshot, such as records from #2024's Gmail read path. Unknown means "present in the supplied in-scope inbox snapshot but absent from local state." If no snapshot is supplied, the report must label the unknown-thread check `not_evaluated` rather than claiming an empty mailbox.

### D4 - Gmail Label Creation and Mirror

Gmail labels are visualization, not source of truth, but #2026 explicitly asks for label creation. This plan keeps queue state local as authoritative and includes one-time Gmail label setup for the two authorized accounts.

Implementation must provide:

- a pure label-operation planner used by tests
- an `ensure_labels(..., apply=True)` path that creates missing labels from the exact #2026 taxonomy for `ace` and `personal` when Gmail client/credential surfaces are available for both accounts
- default CLI behavior that prints planned operations unless an explicit `--apply-labels` flag is supplied

The #2026 label taxonomy is:

- `wh-email/extracted`
- `wh-email/awaiting-reply`
- `wh-email/completed`
- `wh-email/noise`

No `inbound` or `purged` Gmail label is created in #2026. `noise` remains a routing/labeling class, not a queue-state enum.

Live label creation is in scope after plan approval. The implementation must select a separate authenticated Gmail client per enabled account, for example through `gmail_client_factory(account_alias)` or an explicit `clients_by_account` map; a single ambient Gmail client is not sufficient evidence that both mailboxes were mutated. The Gmail adapter should reuse or wrap the existing per-account credential/REST prior art in `scripts/email/gmail-archive-extract.py` and `scripts/email/gmail-digest.py` rather than adding a third unrelated OAuth layout. `accounts.yaml` remains the queue-state normalization config; credential discovery remains owned by the existing Gmail helper pattern unless implementation documents a user-approved split. Gmail archive/delete remains out of scope and belongs to #2423.

### D5 - Dedup Key Correction

The implementation must correct the #2017 v9 dedup over-correction by adding `cycle_id` plus a computed `dedup_event_id` to the dedup contract.

Rules:

- Every snapshot record carries a `cycle_id` and `cycle_started_at`.
- Initial records default to `cycle_id = "initial"` unless the caller supplies one.
- Reactivation transitions are exactly `awaiting-reply|completed|purged -> extracted|inbound`. They start a new cycle. `cycle_id` is `msg:<triggering_message_id>` when present, otherwise `reactivation:<reactivation_id>` when the caller supplies a stable fallback id from an inbox snapshot. The reactivation checker must map inbox `latest_message_id` to the public `triggering_message_id` argument on every planned/applied `reactivate_reply()` call; if `latest_message_id` is absent it must supply a stable `reactivation_id` derived from the snapshot record. The cold-start compatibility wrapper may fall back to `bootstrap:<linked_extraction_or_reason>` only for the existing single-call #2017 contract test when no snapshot record exists; production reactivation checkers must pass `triggering_message_id` or a stable `reactivation_id`, otherwise the transition fails with `MissingReactivationId`.
- Non-reactivation transitions inherit the current snapshot `cycle_id` and must not have `ts_utc` earlier than the current snapshot `cycle_started_at`; this prevents delayed no-trigger events from a previous lifecycle from being applied to a new lifecycle when the state names happen to match.
- If `triggering_message_id` is supplied, `dedup_event_id = "msg:" + triggering_message_id`.
- If no `triggering_message_id` is supplied, `dedup_event_id = "legacy:no-trigger"` within the current cycle so existing retry tests without a message id still dedup across fresh timestamps, while later cycles do not collapse.
- Missing-trigger reactivation events must set `warning_no_triggering_message_id: true` on the state entry and any paired learning event.
- Mixed no-id/id events do not dedup against each other because they have different `cycle_id`, different `dedup_event_id`, or both.
- Historical retry detection must not rely only on the current snapshot cycle. If the caller supplies `cycle_id`, require an exact six-field historical key match. If the caller lacks `cycle_id` and current state differs from `from_state`, search historical keys with the same `(account_id, thread_id, from_state, to_state, dedup_event_id)` and then filter candidates to the current snapshot `cycle_id`. Treat the event as an idempotent retry only when exactly one current-cycle candidate remains; otherwise raise `StaleStateError`. This keeps delayed duplicates in the active lifecycle idempotent even when older lifecycles contain the same no-trigger transition, without silently skipping stale no-trigger events from a previous lifecycle.

`docs/design/email-queue-state-schema.yaml` must be updated so `cycle_id`, `triggering_message_id`, `dedup_event_id`, `needs_user_decision`, `warning_no_triggering_message_id`, and the corrected dedup-key semantics are explicit.

### D6 - Public API Compatibility

`scripts/email/queue_state.py` must keep the path-first API used by `tests/email/test_state_machine_contract.py`:

```python
transition(log_path, *, account_id, thread_id, from_state, to_state, ts_utc, ...)
lookup(log_path, account_id, thread_id)
count_entries(log_path)
reactivate_reply(log_path, *, account_id, thread_id, prior_state, linked_extraction, ts_utc, ...)
```

This plan also adds a new path-first helper for the report CLI:

```python
list_threads(log_path, account_scope=None, include_out_of_scope=False)
```

When a caller supplies `log_path`, sibling runtime files are derived from that path:

- `queue-state-snapshot.yaml`
- `queue-state-snapshot.meta.yaml`
- `queue-learning-log.jsonl`

For the standard log filename `queue-state.jsonl`, the sibling names above are used. For any non-standard log filename, sibling names must derive from the log stem, for example `custom.jsonl` -> `custom-snapshot.yaml`, `custom-snapshot.meta.yaml`, and `custom-learning-log.jsonl`, so two stores in one temp directory cannot collide.

Higher-level helpers and CLI commands may construct the same store from `EMAIL_QUEUE_STATE_DIR`, but they must not replace the path-first public wrapper.

### D7 - Inbox Snapshot Contract

`pending_work_report()` must accept an optional `inbox_snapshot` list with this minimal schema:

```yaml
- account_id: ace            # canonical alias, or email that maps to one
  thread_id: string          # Gmail thread id
  latest_message_id: string  # optional but preferred
  labels: [string]           # optional
  received_at_utc: string    # ISO-8601 UTC Z, optional
  source: gmail              # optional
```

The report must normalize literal account emails through the account config. Unknown-thread detection only considers enabled aliases in the two-account scope. If an inbox snapshot contains literal email accounts but no config supplies an email-to-alias mapping, the report must fail closed with `unknown_status: "config_missing"` and `mailbox_empty: null`; it must not classify those records as harmless out-of-scope. Records explicitly mapped by config to disabled aliases are counted separately and never make `mailbox_empty` false for this issue.

Snapshot records with `wh-email/noise` are excluded from unknown-thread counts and counted as `noise_excluded`, because noise is intentionally routed outside queue state.

When an inbox snapshot record matches an existing local state record, `pending_work_report()` must still compare `latest_message_id`/`received_at_utc` against `last_seen_message_id`/`last_seen_received_at_utc`. A newer message on a tracked `completed`, `awaiting-reply`, or `purged` thread is counted as `reactivation_pending` and makes `mailbox_empty: false`. If the tracked local state lacks both baseline fields for a matched in-scope snapshot record, the report increments `baseline_missing_count`, sets `unknown_status: "baseline_missing"` or a paired warning field, and makes `mailbox_empty: false`; it must never report an empty mailbox when a tracked thread cannot be compared against the supplied inbox snapshot.

The report must enumerate the enabled in-scope local records it counted, so the CLI can show all tracked threads plus aggregate counts. Disabled/unknown local records may appear only in a warning section when explicitly requested; they do not contribute to `tracked_empty`.

### D8 - State Machine Reactivation Edge

The implementation must reconcile `docs/design/email-as-queue.md` prose with its transition table. Missing-extraction reactivation will be represented as a real transition:

- `awaiting-reply -> inbound` with `reason="missing-extraction"`
- `completed -> inbound` with `reason="missing-extraction"`
- `purged -> inbound` with `reason="missing-extraction"`

Existing reactivation edges to `extracted` must remain valid and be covered by tests:

- `awaiting-reply -> extracted`
- `completed -> extracted`
- `purged -> extracted`

The inbound edges are only valid for the missing-extraction path. The design doc and transition tests must be updated so `reactivate_reply()` does not rely on an edge the validator rejects.

### D9 - Grace Sweep Semantics

`sweep_grace()` must expose `dry_run=True` by default. In apply mode it must append purge events through the same locked store path as `transition()` and rebuild snapshot/meta before returning. It must not append directly to JSONL without snapshot materialization.

The batch implementation should use a batch-aware locked helper that takes up to `batch_size` events, appends non-deduped rows under one `fcntl` lock, and rebuilds snapshot/meta once per batch. It should not call the one-event helper 100 times while claiming one batch.

Apply mode must be ordered after reactivation detection. `sweep_grace(..., dry_run=False)` must either receive the same inbox snapshot used for the reactivation check or a non-forgeable `ReactivationPrecheck` object returned by `reactivation_candidates()` for the same log path, account set, and snapshot hash. A bare boolean is not acceptable. The precheck object includes `state_log_offset`, `snapshot_hash`, `pending_thread_ids`, and `baseline_missing_thread_ids`. Sweep validates the precheck once under the store lock before its first batch; if the log offset/hash has changed before sweep starts, it fails closed. Subsequent batches in the same sweep transaction do not revalidate against their own appended purge rows. When an inbox snapshot or precheck object shows a newer reply or missing baseline for a completed thread, sweep apply skips that thread and reports it as `reactivation_pending` or `baseline_missing` instead of appending `completed -> purged`. The scheduled #2026 job remains dry-run/report-only, but this ordering guard prevents future #2423 wiring from deleting a replied-to thread.

### D10 - Issue Task Disposition

Every implementation task in #2026 has an explicit disposition:

| #2026 task | Disposition in this plan |
|---|---|
| 1. Create Gmail labels via API | In scope via `ensure_labels()` and CLI `labels --apply-labels`; archive/delete excluded. |
| 2. Build state log reader/writer | In scope via `queue_state.py` and `scripts/email/state/store.py`. |
| 3. Build state transition functions | In scope via `state/machine.py`, path-first wrappers, and transition tests. |
| 4. Grace period checker runs in daily cron | Checker, report command, and a non-destructive daily dry-run scheduled-task entry are in scope for #2026. Destructive deletion scheduling and pipeline orchestration remain #2024/#2423. |
| 5. Re-activation checker scans for new replies on completed threads | In scope as a snapshot-driven checker that consumes the D7 inbox snapshot contract and calls or plans `reactivate_reply`; live Gmail read orchestration remains #2024. |
| 6. State report command | In scope via `scripts/email/email-queue-state.py report`, showing all tracked threads plus counts by state/account/pending class. |
| 7. Migration scans existing inbox and labels current emails | In scope as `scripts/email/email-queue-state.py migrate-labels` consuming an inbox snapshot and planning/applying label operations for current in-scope threads; live Gmail inbox enumeration remains #2024 unless credentials are available in the implementation session. |

### D11 - Ordering, Dedup, and Integration Boundaries

State transitions are guarded by both a static edge table and a dynamic current-state check under the same file lock:

- If no current snapshot record exists, raw `transition()` accepts only initial `from_state="inbound"` transitions.
- `reactivate_reply()` has a narrow cold-start compatibility path for the existing #2017 contract test: the wrapper first rejects any `prior_state` outside `{"awaiting-reply", "completed", "purged"}`, then passes `allow_bootstrap_reactivation=True`, and the locked append path accepts a missing snapshot record only for that bounded wrapper path. The append path stamps `bootstrap_reactivation: true` under the lock and records the assumption in the implementation notes/report. Production reactivation checkers must not depend on cold-start bootstrap; tests must prove they report `baseline_missing` instead of invoking `reactivate_reply()` for threads absent from local state.
- If a current snapshot record exists and its `state` differs from `event.from_state`, the append is rejected as `StaleStateError` unless the event qualifies as an unambiguous historical dedup retry under D5. Batch sweep may use a `stale_policy="skip"` helper only for preselected candidates, and skipped candidates must be reported; ordinary `transition()` and `reactivate_reply()` stay fail-closed.
- Dedup keys are checked against a historical dedup index rebuilt from the append-only log under lock, not against the latest snapshot only.

The implementation must store reactivation baselines in snapshots:

- `last_seen_message_id`
- `last_seen_received_at_utc`

The reactivation checker compares inbox snapshot `latest_message_id`/`received_at_utc` against these stored baselines. If no baseline exists, the checker reports `baseline_missing` rather than claiming a newer reply or planning `reactivate_reply()`.

State/learning paired writes must be recoverable across process crashes. The state log is authoritative: each state event may carry a single attached `paired_learning_event`; paired state and learning rows carry deterministic `transaction_id` and `learning_event_id` fields, the state event is appended first with the paired learning id, and the learning log append follows. `docs/design/email-queue-state-schema.yaml` must add both fields to state and learning schemas so the linkage is durable. Snapshot rebuild/recovery scans state events for paired learning ids missing from the learning log and backfills them idempotently. This avoids a durable learning row with no state transition, avoids positional pairing across separate lists, and makes a crash after state append repairable.

Snapshot freshness is part of the read contract. `queue-state-snapshot.meta.yaml` must include enough material to detect missing meta, corrupt meta, stale log size/mtime or offset, and stale/corrupt content hash. `lookup()` and `list_threads()` must return from snapshot only when meta validates; otherwise they acquire the store lock and rebuild snapshot/meta before reading.

The Gmail label API path is in scope. Implementation must provide a real adapter around the available Gmail API/client surface for `users.labels.list` and `users.labels.create` or equivalent; fake-client tests are necessary but not sufficient for closeout. #2026 task 1 is not complete until live labels are verified for `ace` and `personal` through per-account clients. If credentials are unavailable, implementation may land behind tests, but #2026 must remain open with a blocked label-setup comment or a user-approved split.

The scheduled task is in scope as a dry-run safety job: `config/scheduled-tasks/schedule-tasks.yaml` must add a daily dry-run `email-queue-state.py sweep --dry-run`/report entry. Destructive Gmail deletion remains #2423 and live Gmail read orchestration remains #2024.

Tests must not commit real or production-like email addresses under `tests/fixtures/email/`, because `scripts/email/fixture-redaction-check.py` rejects those fixtures. Snapshot tests should build inline records with reserved placeholder domains plus temp account config mapping.

The CLI should have an importable seam: `scripts/email/state/cli.py` exposes `main(argv, gmail_client_factory=None)`, and `scripts/email/email-queue-state.py` is a thin executable wrapper. Unit tests inject fake Gmail clients through `state.cli.main`; subprocess tests only verify the wrapper can dispatch and parse arguments.

---

## Pseudocode

```python
def resolve_state_dir(env=None):
    env = env or os.environ
    return Path(env.get("EMAIL_QUEUE_STATE_DIR", "~/.hermes/email-state")).expanduser()

def default_log_path(env=None):
    return resolve_state_dir(env) / "queue-state.jsonl"

def store_from_log_path(log_path=None, env=None):
    log_path = Path(log_path) if log_path is not None else default_log_path(env)
    if log_path.name == "queue-state.jsonl":
        snapshot_name = "queue-state-snapshot.yaml"
        meta_name = "queue-state-snapshot.meta.yaml"
        learning_name = "queue-learning-log.jsonl"
    else:
        snapshot_name = f"{log_path.stem}-snapshot.yaml"
        meta_name = f"{log_path.stem}-snapshot.meta.yaml"
        learning_name = f"{log_path.stem}-learning-log.jsonl"
    return Store(
        log_path=log_path,
        snapshot_path=log_path.with_name(snapshot_name),
        meta_path=log_path.with_name(meta_name),
        learning_log_path=log_path.with_name(learning_name),
    )

def load_account_scope(config_path=None, env=None):
    env = env or os.environ
    path = config_path or env.get("EMAIL_QUEUE_ACCOUNTS_CONFIG") or "~/.hermes/email-state/accounts.yaml"
    config = read account config from path if it exists, else alias-only default {"ace", "personal"}
    build alias/email mapping for enabled accounts only; email mapping is empty without config
    reject or mark out-of-scope aliases/emails outside {"ace", "personal"}
    return AccountScope(mapping)

def transition(log_path=None, *, account_id, thread_id, from_state, to_state, ts_utc, **optional_fields):
    store = store_from_log_path(log_path)
    event = QueueStateEvent(account_id, thread_id, from_state, to_state, ts_utc, **optional_fields)
    return _append_events_locked(store, [event])

def prepare_event(store, event, snapshot_before, historical_dedup_index, stale_policy="raise"):
    validate event.from_state -> event.to_state transition is allowed
    validate missing-extraction inbound edges include reason="missing-extraction"
    validate event.ts_utc ends with Z
    build writer_identity
    current = snapshot_before.get(event.key)
    reactivation = event.from_state in {"awaiting-reply", "completed", "purged"} and event.to_state in {"extracted", "inbound"}
    if current is None:
        if event.from_state == "inbound":
            pass
        elif event.allow_bootstrap_reactivation and reactivation and event.from_state in {"awaiting-reply", "completed", "purged"}:
            event.bootstrap_reactivation = True
        else:
            raise StaleStateError
    if current is not None and current.state != event.from_state:
        compute dedup_event_id from event.triggering_message_id or "legacy:no-trigger"
        if event.cycle_id:
            duplicate = exact 6-field dedup key exists in historical_dedup_index
        else:
            candidates = historical keys matching account_id/thread_id/from_state/to_state/dedup_event_id
            current_cycle_candidates = candidates whose cycle_id == current.cycle_id
            duplicate = exactly one current_cycle_candidate exists
        if duplicate:
            mark event as duplicate retry
            return event
        if stale_policy == "skip":
            mark event as stale skipped
            return event
        raise StaleStateError
    if reactivation:
        if event.triggering_message_id:
            event.cycle_id = "msg:" + event.triggering_message_id
        elif event.reactivation_id:
            event.cycle_id = "reactivation:" + event.reactivation_id
        elif event.bootstrap_reactivation:
            event.cycle_id = "bootstrap:" + stable hash of linked_extraction_or_reason
        else:
            raise MissingReactivationId
        if not event.triggering_message_id:
            event.warning_no_triggering_message_id = True
    else:
        event.cycle_id = event.cycle_id or snapshot_before.get(event.key, {}).get("cycle_id", "initial")
    if event.triggering_message_id:
        event.dedup_event_id = "msg:" + event.triggering_message_id
    else:
        event.dedup_event_id = "legacy:no-trigger"
    if event.to_state == "completed":
        event.completed_at = event.completed_at or event.ts_utc
    elif event.to_state != "completed":
        event.completed_at = None
    if event.triggering_message_id:
        event.last_seen_message_id = event.triggering_message_id
        event.last_seen_received_at_utc = event.received_at_utc or event.ts_utc
    event.dedup_key = event.account_id, event.thread_id, event.from_state, event.to_state, event.cycle_id, event.dedup_event_id
    return event

def _append_events_locked(store, state_events, stale_policy="raise"):
    acquire fcntl LOCK_EX on store.log_path
    snapshot_before = load current snapshot under lock
    historical_dedup_index = rebuild/read dedup keys from append-only log under lock
    recover missing paired learning events from prior state rows before appending new rows
    prepared = [prepare_event(store, event, snapshot_before, historical_dedup_index, stale_policy=stale_policy) for event in state_events]
    batch_dedup_keys = set()
    for event in prepared:
        if event marked stale skipped:
            record skip in append report
        elif event marked duplicate retry or event.dedup_key exists in historical_dedup_index or event.dedup_key in batch_dedup_keys:
            skip event and any paired learning row
        else:
            if event.paired_learning_event exists:
                assign deterministic transaction_id/learning_event_id to state row and attached learning row
            append state event first
            append event.paired_learning_event after state event when supplied
            add event.dedup_key to batch_dedup_keys and historical_dedup_index
    rebuild snapshot and meta via tmpfile + fsync + os.replace
    return append/rebuild report plus current snapshot records

def lookup(log_path, account_id, thread_id):
    store = store_from_log_path(log_path)
    read snapshot only if meta freshness checks pass
    otherwise acquire lock and rebuild snapshot/meta
    return snapshot.get(f"{account_id}::{thread_id}")

def list_threads(log_path, account_scope=None, include_out_of_scope=False):
    store = store_from_log_path(log_path)
    read snapshot only if meta freshness checks pass, otherwise rebuild under lock
    normalize records through account_scope when supplied
    return enabled in-scope records plus optional warning buckets for disabled/unknown local records

def count_entries(log_path):
    return count persisted JSONL state entries for log_path

def reactivate_reply(log_path=None, *, account_id, thread_id, prior_state, linked_extraction, ts_utc, triggering_message_id=None, reactivation_id=None):
    store = store_from_log_path(log_path)
    if prior_state not in {"awaiting-reply", "completed", "purged"}:
        raise InvalidPriorState
    if linked_extraction exists:
        return _append_events_locked(
            store,
            [QueueStateEvent(
                account_id=account_id,
                thread_id=thread_id,
                from_state=prior_state,
                to_state="extracted",
                linked_extraction=linked_extraction,
                triggering_message_id=triggering_message_id,
                reactivation_id=reactivation_id,
                allow_bootstrap_reactivation=True,
                ts_utc=ts_utc,
            )],
        )
    learning_event = QueueLearningEvent(
        account_id=account_id,
        thread_id=thread_id,
        triggering_event="extraction_missing_on_reactivation",
        ts_utc=ts_utc,
        warning_no_triggering_message_id=triggering_message_id is None,
    )
    return _append_events_locked(
        store,
        [QueueStateEvent(
            account_id=account_id,
            thread_id=thread_id,
            from_state=prior_state,
            to_state="inbound",
            reason="missing-extraction",
            triggering_message_id=triggering_message_id,
            reactivation_id=reactivation_id,
            allow_bootstrap_reactivation=True,
            paired_learning_event=learning_event,
            ts_utc=ts_utc,
        )],
    )

def sweep_grace(log_path, now_utc, grace_days=7, batch_size=100, dry_run=True, inbox_snapshot=None, reactivation_precheck=None):
    store = store_from_log_path(log_path)
    acquire sweep lockfile
    if not dry_run and not (inbox_snapshot or valid ReactivationPrecheck for this store/account set/snapshot hash):
        raise UnsafeSweepOrderError
    if dry_run:
        acquire store.log_path lock and read completed snapshot records where now - completed_at > grace_days
        return planned completed -> purged transitions without appending
    while eligible completed records remain:
        under one store.log_path lock, select up to batch_size still-completed records
        if reactivation_precheck is supplied, skip selected records present in reactivation_precheck.pending_thread_ids
        if inbox_snapshot is supplied, skip selected records with newer snapshot messages
        append completed -> purged events with stale_policy="skip" and rebuild snapshot/meta once
        dynamic current-state validation reports records reactivated before the batch lock as skipped
    return dry-run/apply report

def pending_work_report(log_path=None, account_scope=None, inbox_snapshot=None):
    store = store_from_log_path(log_path)
    account_scope = account_scope or load_account_scope()
    validate/normalize account scope only at this report/ingest boundary
    local_records = list_threads(log_path, account_scope=account_scope, include_out_of_scope=True)
    counted_records = enabled in-scope local records only
    inbound_count = count state == "inbound" by account from counted_records
    decision_count = count needs_user_decision metadata by account from counted_records
    needs_schema_count = count needs_schema metadata by account from counted_records
    per_account_counts = group state, needs_user_decision, needs_schema by account from counted_records
    out_of_scope_local_count = count disabled/unknown local_records warning bucket
    tracked_empty = inbound_count == 0 and decision_count == 0 and needs_schema_count == 0
    if inbox_snapshot is supplied:
        normalize snapshot records using account_scope
        if literal-email records cannot be mapped because config is missing:
            return {
                "tracked_empty": tracked_empty,
                "mailbox_empty": None,
                "unknown_status": "config_missing",
                "unknown_count": None,
                "out_of_scope_count": None,
                "noise_excluded": None,
                "reactivation_pending_count": None,
                "baseline_missing_count": None,
                "out_of_scope_local_count": out_of_scope_local_count,
                "per_account_counts": per_account_counts,
                "threads": counted_records,
            }
        exclude records labeled wh-email/noise from unknown_count and count as noise_excluded
        unknown_count = count enabled in-scope snapshot threads missing from local state
        reactivation_pending_count = count enabled in-scope snapshot threads present in local state but newer than stored message baseline
        baseline_missing_count = count enabled in-scope snapshot threads present in local state but missing comparable baseline fields
        out_of_scope_count = count disabled/out-of-scope snapshot records
        unknown_status = "baseline_missing" if baseline_missing_count else "evaluated"
        mailbox_empty = tracked_empty and unknown_count == 0 and reactivation_pending_count == 0 and baseline_missing_count == 0
    else:
        unknown_count = None
        out_of_scope_count = None
        reactivation_pending_count = None
        baseline_missing_count = None
        unknown_status = "not_evaluated"
        mailbox_empty = False if not tracked_empty else None
        noise_excluded = None
    return {
        "tracked_empty": tracked_empty,
        "mailbox_empty": mailbox_empty,
        "unknown_status": unknown_status,
        "unknown_count": unknown_count,
        "out_of_scope_count": out_of_scope_count,
        "noise_excluded": noise_excluded,
        "reactivation_pending_count": reactivation_pending_count,
        "baseline_missing_count": baseline_missing_count,
        "out_of_scope_local_count": out_of_scope_local_count,
        "per_account_counts": per_account_counts,
        "threads": counted_records,
    }

def ensure_labels(account_scope, gmail_client_factory=None, clients_by_account=None, apply=False):
    ops = planned create/update operations for wh-email/extracted, awaiting-reply, completed, noise per enabled account
    if apply:
        for each enabled account alias:
            client = clients_by_account[alias] or gmail_client_factory(alias)
            require client for that alias
            list/create missing labels only in that mailbox; never archive/delete messages
    return ops/apply report

def reactivation_candidates(log_path=None, inbox_snapshot=None, apply=False):
    compare current snapshot with normalized inbox snapshot
    for each completed/awaiting-reply/purged tracked thread present in snapshot:
        if stored baseline is missing:
            report baseline_missing and do not plan reactivate_reply
        elif snapshot is newer than stored baseline:
            map snapshot latest_message_id to reactivate_reply(triggering_message_id=latest_message_id)
            if latest_message_id missing, derive stable reactivation_id from account/thread/received_at/source record
    return ReactivationPrecheck plus planned reactivate_reply calls including triggering_message_id or reactivation_id, or apply them when explicitly requested

def migrate_labels(log_path=None, inbox_snapshot=None, gmail_client_factory=None, clients_by_account=None, apply_labels=False):
    normalize current inbox snapshot through account scope
    map each in-scope thread to wh-email label operations from current state/report
    if apply_labels:
        require per-account Gmail clients and apply labels only; never archive/delete
    return migration plan/apply report

def cli_main(argv, gmail_client_factory=None):
    subcommands: report, labels, sweep, reactivations, migrate-labels
    --state-dir resolves default log path under EMAIL_QUEUE_STATE_DIR
    --inbox-snapshot accepts the D7 snapshot file
    --apply-labels gates live Gmail label creation/application
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/email/queue_state.py` | Public API wrapper expected by existing contract tests |
| Create | `scripts/email/email-queue-state.py` | Operator CLI for report, labels, sweep, reactivation check, and migration-label pass |
| Create | `scripts/email/state/__init__.py` | Re-export state package API |
| Create | `scripts/email/state/accounts.py` | Account allowlist and runtime alias validation |
| Create | `scripts/email/state/machine.py` | State transition table and validation |
| Create | `scripts/email/state/store.py` | JSONL append, fcntl locking, snapshot rebuild |
| Create | `scripts/email/state/meta.py` | Snapshot metadata freshness checks |
| Create | `scripts/email/state/dedup.py` | Cycle-aware dedup key logic with `cycle_id`, `triggering_message_id`, and computed `dedup_event_id` |
| Create | `scripts/email/state/grace.py` | Seven-day local purge sweep |
| Create | `scripts/email/state/labels.py` | Gmail label operation planner plus explicit apply path for one-time label creation |
| Create | `scripts/email/state/gmail_labels_api.py` | Real Gmail label list/create adapter for #2026 label setup |
| Create | `scripts/email/state/cli.py` | Importable CLI command implementation used by the hyphenated wrapper and unit tests |
| Create | `scripts/email/state/report.py` | Pending-work report and mailbox-empty semantics |
| Create | `scripts/email/state/reactivation.py` | Inbox-snapshot-driven reactivation checker for completed/awaiting/purged replies |
| Create | `scripts/email/state/migration.py` | Inbox-snapshot-driven current-label migration planner/apply helper |
| Modify | `docs/design/email-queue-state-schema.yaml` | Add `cycle_id`, `triggering_message_id`, `dedup_event_id`, `needs_user_decision`, warning metadata, message-baseline fields, and corrected dedup semantics |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Add daily dry-run email queue grace/report job; no Gmail delete/archive |
| Modify | `tests/email/test_state_machine_contract.py` | Expand contract tests and remove xfail markers once implementation lands |
| Create | `tests/email/test_email_queue_state.py` | TDD coverage for account scope, store, grace, reports, label planning |
| Modify | `docs/design/email-as-queue.md` | Reconcile runtime state path, two-account scope, pending-work semantics, and missing-extraction transition table |
| Modify | `docs/design/email-as-queue-workflow.md` | Update or mark stale three-account/Gmail-mutation sections superseded |
| Create | `docs/reports/2026-06-11-issue-2026-implementation-notes.html` | User-requested implementation notes and deviations log |
| Already applied | `docs/plans/README.md` | This planning session added the draft row |
| Already applied | `docs/plans/2026-04-24-issue-2026-plan.md` | This planning session marked the stale April draft superseded |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_import_queue_state_module` | public module exists | import `scripts.email.queue_state` | import succeeds |
| `test_account_config_defaults_to_aliases_only` | default scope is two aliases without embedding literal email defaults | missing local config with isolated env | aliases `ace`, `personal` enabled; email mapping empty |
| `test_rejects_out_of_scope_account_alias_at_report_boundary` | disabled aliases are known out of scope | inline snapshot with placeholder email mapped to disabled `skestates` in temp config | out-of-scope count increments; no mailbox-empty failure |
| `test_transition_accepts_placeholder_account_for_low_level_store` | low-level state store does not enforce production account allowlist | `account_id="user@example.com"` | transition accepted |
| `test_path_first_api_derives_snapshot_and_learning_paths` | existing contract API remains stable | `transition(tmp/queue-state.jsonl, ...)` | sibling snapshot/meta/log files used |
| `test_nonstandard_log_path_derives_noncolliding_siblings` | arbitrary path-first logs do not share snapshot files | `a.jsonl` and `b.jsonl` in one dir | distinct sibling files |
| `test_transition_inbound_to_extracted_writes_log` | existing contract | inbound -> extracted | lookup state is extracted |
| `test_transition_retry_preserves_dedup_under_same_triggering_message` | retry idempotency | same triggering message twice | one JSONL row |
| `test_transition_retry_preserves_legacy_dedup_without_triggering_message` | existing contract compatibility | same transition, no triggering id, different timestamps | one JSONL row |
| `test_stale_from_state_rejected_unless_historical_dedup_key_exists` | stale caller views cannot regress snapshot state | completed thread receives inbound -> extracted event | `StaleStateError` unless duplicate key exists |
| `test_dedup_uses_historical_index_not_latest_snapshot_only` | delayed duplicate of earlier transition still dedups | duplicate inbound -> extracted after awaiting state | no appended row |
| `test_cross_cycle_no_trigger_stale_replay_raises` | no-trigger dedup does not silently skip stale previous lifecycle events | cycle 1 no-id event replayed after cycle 2 reactivation | `StaleStateError` |
| `test_second_cycle_no_trigger_retry_dedups_with_current_cycle_candidate` | current-cycle no-trigger retry stays idempotent even with older lifecycle history | no-id completed retry in cycle 2 after same transition in cycle 1 | one cycle-2 completion row |
| `test_batch_dedup_skips_duplicate_events_in_same_batch` | batch helper updates dedup index as it appends | two identical events in one batch | one state row and one skipped duplicate |
| `test_dedup_preserves_reactivation_cycle` | real repeated replies do not collapse | two triggering message IDs | two JSONL rows with distinct `cycle_id` |
| `test_multicycle_without_trigger_can_extract_complete_and_purge_twice` | cycle-aware fallback does not swallow second lifecycle | complete/purge/reactivate/extract/complete/purge without message IDs | both purge events persist |
| `test_no_trigger_reactivation_retry_dedups_with_stable_reactivation_id` | no-id reactivation retry has stable fallback | same `reactivation_id`, fresh timestamps | one row |
| `test_no_trigger_distinct_reactivation_cycles_require_distinct_reactivation_id` | no-id cycles remain distinguishable | two distinct `reactivation_id` values | two rows |
| `test_mixed_trigger_and_no_trigger_events_do_not_dedup` | mixed dedup semantics are explicit | one no-id event and one message-id event | two JSONL rows plus warning metadata |
| `test_snapshot_uses_account_thread_composite_key` | no account collision | same thread ID under ace/personal | two snapshot records |
| `test_non_utc_timestamp_rejected` | UTC contract | missing `Z` suffix | validation error |
| `test_invalid_transition_rejected` | state machine guard | inbound -> purged | validation error |
| `test_missing_extraction_transition_to_inbound_is_allowed_only_with_reason` | D8 state-machine reconciliation | purged -> inbound with/without reason | allowed only for `reason="missing-extraction"` |
| `test_existing_reactivation_edges_to_extracted_remain_allowed` | D8 does not remove existing valid edges | awaiting/completed/purged -> extracted | allowed |
| `test_transition_to_completed_stamps_completed_at` | grace sweep has reliable completion timestamp | extracted -> completed without explicit `completed_at` | snapshot has `completed_at == ts_utc` |
| `test_transition_with_triggering_message_stamps_baseline` | report/checker can compare tracked threads | transition carrying `triggering_message_id` and `received_at_utc` | snapshot stores last-seen message and received timestamp |
| `test_transition_with_message_id_without_received_at_uses_ts_baseline` | message baseline has deterministic timestamp fallback | transition with `triggering_message_id` only | snapshot `last_seen_received_at_utc == ts_utc` |
| `test_lookup_unknown_thread_returns_none` | absence checks do not crash | lookup missing account/thread | `None` |
| `test_list_threads_enumerates_in_scope_records` | report CLI has an enumeration API | mixed in-scope and disabled local records | returns in-scope threads plus warning bucket |
| `test_completed_grace_7d_exact_boundary_not_purged` | grace boundary | completed at now-7d | remains completed |
| `test_completed_grace_7d_plus_one_second_purged` | grace purge | completed at now-7d-1s | purged |
| `test_sweep_chunks_at_batch_cap` | bounded lock hold | 101 eligible records | two batches |
| `test_sweep_dry_run_does_not_append_or_rebuild` | dry run safety | eligible completed records, dry_run true | report only, entry count unchanged |
| `test_sweep_apply_requires_reactivation_precheck` | apply cannot purge before reply check | eligible completed record, dry_run false, no snapshot/precheck | `UnsafeSweepOrderError` |
| `test_sweep_apply_rejects_forgeable_boolean_precheck` | sweep proof is not a caller-supplied boolean | `reactivation_precheck=True` | validation error |
| `test_sweep_apply_accepts_matching_reactivation_precheck_object` | checked sweep can run without rereading snapshot | valid precheck object for same log/account/snapshot hash | eligible records processed |
| `test_sweep_apply_skips_completed_thread_with_new_reply` | new reply during grace is not purged | completed record plus newer inbox snapshot | skipped as `reactivation_pending` |
| `test_sweep_batch_reports_stale_skips_without_crashing` | batch stale candidates do not crash whole sweep | candidate reactivated before batch append | skip reported; other eligible records append |
| `test_sweep_apply_rebuilds_snapshot_meta` | sweep apply keeps snapshot materialized | eligible completed record, dry_run false | lookup returns purged |
| `test_purged_reactivates_on_reply_with_extraction_link` | existing contract | purged + extraction path | extracted + linked path |
| `test_cold_start_reactivate_reply_bootstrap_preserves_contract` | dynamic validation keeps #2017 xfail contract viable | empty log + `reactivate_reply(prior_state="purged")` | extracted with `bootstrap_reactivation: true` |
| `test_bootstrap_reactivate_rejects_unbounded_prior_state` | cold-start wrapper only accepts authorized prior states | empty log + `prior_state="inbound"` | `StaleStateError` or validation error |
| `test_reactivation_checker_never_bootstraps_absent_state` | production checker does not use cold-start compatibility | inbox snapshot thread absent from local state | reports unknown/baseline_missing; no `reactivate_reply` call |
| `test_missing_extraction_logs_learning_event_and_returns_inbound` | missing extraction recovery | purged + missing path | learning event emitted; state becomes inbound |
| `test_learning_recovery_backfills_missing_paired_event` | state/learning paired writes are crash-recoverable | state row with paired learning id but missing learning row | rebuild/backfill writes one learning row |
| `test_no_orphan_learning_row_without_state_transition` | learning log cannot claim transition absent from state log | simulated crash before state append | no durable learning row |
| `test_paired_learning_event_attaches_to_state_event` | transaction id cannot be assigned by positional list matching | missing-extraction state event with attached learning event | same deterministic id in both rows |
| `test_pending_work_report_tracked_empty_when_no_inbound_or_decision_needed` | tracked-state emptiness without overclaiming full Gmail state | completed/purged/awaiting only | `tracked_empty: true` |
| `test_pending_work_report_excludes_disabled_local_rows_from_tracked_counts` | disabled local state does not block two-account mailbox-empty | disabled local inbound row plus empty in-scope state | warning count increments; `tracked_empty: true` |
| `test_pending_work_report_unknown_not_evaluated_without_snapshot` | local state does not overclaim Gmail emptiness | no inbox snapshot | unknown check is `not_evaluated`; `mailbox_empty: null` |
| `test_pending_work_report_normalizes_literal_email_snapshot` | #2024/Gmail input can use literal addresses without committing real data | inline placeholder literal email plus temp account config | account normalized to `ace` |
| `test_pending_work_report_literal_email_without_config_fails_closed` | missing config cannot make mailbox falsely empty | literal-email snapshot, no account config | `unknown_status: config_missing`, `mailbox_empty: null` |
| `test_pending_work_report_config_missing_uses_unknown_noise_sentinel` | config-missing branch does not claim noise was evaluated | literal-email snapshot, no config | `noise_excluded: null` |
| `test_pending_work_report_not_empty_for_snapshot_unknown` | untracked Gmail thread is surfaced when snapshot supplied | snapshot thread missing from state | `mailbox_empty: false`, unknown count 1 |
| `test_pending_work_report_excludes_noise_label_from_unknown` | routed noise does not block mailbox-empty | inbox snapshot labeled `wh-email/noise` and absent from state | `noise_excluded: 1`, unknown unchanged |
| `test_pending_work_report_counts_new_reply_on_tracked_thread` | tracked completed thread with newer inbox message is pending | completed state + inbox snapshot newer than baseline | `reactivation_pending_count: 1`, `mailbox_empty: false` |
| `test_pending_work_report_blocks_empty_on_tracked_baseline_missing` | tracked thread with supplied inbox snapshot and no baseline cannot be declared empty | completed state lacking baseline plus matching inbox snapshot | `baseline_missing_count: 1`, `mailbox_empty: false` |
| `test_pending_work_report_not_empty_for_needs_user_decision_flag` | pending work surfaced via metadata, not state | existing state with `needs_user_decision: true` | `tracked_empty: false`, `mailbox_empty: false` |
| `test_pending_work_report_not_empty_for_needs_schema_flag` | schema gaps are pending work | existing state with `needs_schema: true` | `tracked_empty: false`, `mailbox_empty: false` |
| `test_pending_flags_clear_on_later_event_without_flags` | last-event-wins pending metadata clears correctly | flagged record then completed event without flags | `tracked_empty: true` |
| `test_label_taxonomy_is_exact_issue_set` | label creation uses issue taxonomy | account scope | extracted/awaiting-reply/completed/noise only |
| `test_label_operations_planned_not_applied_by_default` | Gmail label mutation is off by default in CLI/helper mode | account scope | planned create ops only |
| `test_ensure_labels_creates_missing_labels_with_apply_flag` | issue-required one-time label creation path exists | fake Gmail client and apply true | missing labels created; no archive/delete calls |
| `test_ensure_labels_uses_one_client_per_enabled_account` | two-account setup cannot mutate only one mailbox | fake client factory for `ace` and `personal` | list/create called once per account |
| `test_gmail_label_api_adapter_uses_label_list_and_create_only` | real integration surface exists without delete/archive | fake Google API surface | list/create called; delete/archive never called |
| `test_cli_report_shows_threads_and_counts` | issue task 6 command exists | temp state log | table/list of threads plus counts by account/state |
| `test_cli_labels_requires_apply_flag_for_live_create` | D4 CLI safety | fake Gmail client, no flag | no create calls |
| `test_cli_wrapper_dispatches_to_importable_main` | hyphenated script remains executable while tests use importable seam | subprocess `email-queue-state.py --help` | zero exit and command help |
| `test_reactivation_checker_plans_completed_thread_reply` | issue task 5 checker exists | completed state + newer inbox snapshot | planned `reactivate_reply` |
| `test_reactivation_checker_maps_latest_message_to_triggering_message_id` | production checker passes executable reactivation id | completed state + newer inbox snapshot with `latest_message_id` | planned call includes `triggering_message_id` |
| `test_reactivation_checker_derives_stable_reactivation_id_without_message_id` | no-message snapshots still have stable cycles | newer snapshot without `latest_message_id` | planned call includes deterministic `reactivation_id` |
| `test_reactivation_checker_requires_message_baseline` | checker does not guess newer replies | no stored baseline | reports `baseline_missing` and plans no `reactivate_reply` |
| `test_migrate_labels_plans_current_inbox_labels` | issue task 7 migration exists | inbox snapshot and current states | planned label operations |
| `test_schedule_adds_daily_email_queue_dry_run` | issue task 4 scheduling is represented safely | schedule config | daily dry-run sweep/report entry |
| `test_runtime_state_dir_env_override` | private state does not need repo write | temp `EMAIL_QUEUE_STATE_DIR` | files created under temp dir |
| `test_snapshot_missing_meta_rebuilds_under_lock` | missing metadata cannot serve stale snapshot | snapshot exists, meta missing | lookup rebuilds meta before returning |
| `test_snapshot_bad_hash_rebuilds_under_lock` | corrupt snapshot is not trusted | mismatched meta hash | lookup rebuilds from JSONL |
| `test_snapshot_log_size_or_mtime_change_rebuilds` | appended log invalidates snapshot | log changed after snapshot | lookup/list rebuilds |
| `test_snapshot_corrupt_meta_rebuilds_or_fails_closed` | corrupt meta cannot produce false state | unparsable meta file | rebuilds under lock or raises explicit corruption error |

TDD order:

1. Add/expand failing tests first.
2. Implement the minimal module to turn import failure into functional failures.
3. Implement store/machine/dedup.
4. Implement report/grace/label planning.
5. Remove `xfail` markers only when the storage module is real and tests pass.

---

## Acceptance Criteria

- [ ] `scripts/email/queue_state.py` imports and exposes `transition`, `lookup`, `list_threads`, `count_entries`, `reactivate_reply`, `sweep_grace`, and `pending_work_report`.
- [ ] Public `queue_state` functions preserve the path-first signatures used by the existing #2017 contract tests.
- [ ] Runtime state defaults to `~/.hermes/email-state/` or `EMAIL_QUEUE_STATE_DIR`; no real runtime state is committed.
- [ ] Account allowlist covers only `ace` and `personal` at report/ingest boundaries; low-level state store remains testable with placeholder account IDs.
- [ ] Account config and inbox snapshot schemas are documented and covered by tests.
- [ ] "Mailbox empty" report uses no-pending-work semantics, includes per-account counts plus enumerated in-scope threads, and distinguishes tracked-state emptiness from inbox-snapshot unknown-thread evaluation.
- [ ] Disabled/unknown local state rows are warning buckets; they do not affect `tracked_empty` or `mailbox_empty` for the two-account #2026 scope.
- [ ] Literal-email inbox snapshots without a usable account config fail closed and cannot report `mailbox_empty: true`.
- [ ] Inbox snapshot records labeled `wh-email/noise` are counted as noise-excluded, not unknown pending work.
- [ ] `docs/design/email-queue-state-schema.yaml` includes `cycle_id`, `triggering_message_id`, `dedup_event_id`, `needs_user_decision`, warning metadata, message-baseline fields, and the corrected dedup key.
- [ ] Transitions validate current snapshot state under lock and reject stale `from_state` regressions unless the event is an unambiguous same-cycle historical dedup retry.
- [ ] `docs/design/email-as-queue.md` transition table includes missing-extraction inbound edges gated by `reason="missing-extraction"`.
- [ ] Seven-day grace purge transitions only local state to `purged`; it requires reactivation precheck/snapshot before apply and does not archive/delete Gmail.
- [ ] Gmail label setup can create exactly `wh-email/extracted`, `wh-email/awaiting-reply`, `wh-email/completed`, and `wh-email/noise` for `ace` and `personal` with explicit apply and per-account clients; archive/delete calls are impossible in this module.
- [ ] Real Gmail label API adapter exists for label list/create; fake-client tests alone are not enough for closeout.
- [ ] #2026 task 1 closeout verifies live Gmail labels exist for `ace` and `personal`, or the issue remains open/blocked with a user-approved split.
- [ ] Daily dry-run sweep/report entry is declared in `config/scheduled-tasks/schedule-tasks.yaml`; live Gmail deletion remains #2423.
- [ ] `scripts/email/email-queue-state.py report` shows all tracked threads and counts by state/account/pending class.
- [ ] Snapshot-driven reactivation checker identifies completed/awaiting/purged threads with newer messages; live Gmail read orchestration remains #2024.
- [ ] Reactivation checker maps `latest_message_id` to `triggering_message_id`, derives stable `reactivation_id` when needed, and never uses cold-start bootstrap for absent local state.
- [ ] Snapshot-driven migration label pass can plan/apply current-thread labels; live Gmail inbox enumeration remains #2024 unless credentials are available in the implementation session.
- [ ] Snapshot freshness checks cover missing meta, corrupt meta, bad hash, and changed log offset/size before lookup/list reads.
- [ ] Paired state/learning events use deterministic transaction ids and recover missing learning rows from authoritative state rows.
- [ ] Existing #2017 contract tests pass without xfail markers.
- [ ] New state tests pass: `uv run pytest tests/email/test_state_machine_contract.py tests/email/test_email_queue_state.py -v`.
- [ ] Email contract artifact tests still pass: `uv run pytest tests/email/test_email_queue_contract_artifacts.py tests/email/test_spam_rules.py tests/email/test_fixture_redaction_hook.py -v`.
- [ ] Legal/security scan passes: `scripts/legal/legal-sanity-scan.sh`.
- [ ] Implementation notes HTML exists and records interpretations/deviations/tradeoffs/open questions.
- [ ] Issue comment summarizes implementation, tests, and sources consumed.
- [ ] Completeness gate is satisfied before close per #2798.

---

## Adversarial Review Summary

| Round | Verdict | Key findings |
|---|---|---|
| R1 Claude/Codex/Gemini | MAJOR | Found `needs-user-decision` as undefined state, schema/dedup mismatch, uncomputable unknown-thread report, allowlist conflict with contract tests, unaddressed workflow-doc contradictions, missing-extraction reactivation contradiction, and silent label-scope reduction. |
| R2 Claude/Codex/Gemini | MAJOR | Found unresolved missing-extraction transition-table edge, path-first API ambiguity, missing inbox snapshot/account config contracts, label creation scope mismatch with issue body, dedup fallback ambiguity, direct log append/sweep snapshot hazards, and dry-run omission. Gemini also repeated sandbox-blind missing-file findings from `/tmp`; those are marked false-positive by local `ls`/`rg` evidence. |
| R3 Claude/Codex/Gemini | MAJOR | Found cycle-insensitive no-trigger dedup still swallowed second lifecycle purges, #2026 tasks 5/6/7 lacked artifacts, CLI behavior had no file/test, account default mapping was inconsistent, batch sweep locking contradicted batching, warning metadata was not emitted, and exact label taxonomy was missing. Gemini's `completed_at` finding was a plan-excerpt issue; the live schema already contains `completed_at`. |
| R4 Claude/Codex/Gemini | MAJOR | Found false `mailbox_empty` when literal-email snapshots lack config, missing dynamic `from_state` validation, unspecified historical dedup substrate, no-trigger reactivation retry ambiguity, missing real Gmail label API path, cron dry-run scope not represented, missing reactivation baseline fields, lock target ambiguity, missing pending-flag clear test, and noise-label false unknowns. |
| R5 Claude/Codex/Gemini | MAJOR | Remaining blockers: cold-start `reactivate_reply` conflicts with dynamic validation and existing #2017 contract test; literal-email fixture would be blocked by the email fixture redaction hook; config-missing vs known out-of-scope literal email behavior is contradictory; scheduling ownership and live label creation closeout remain ambiguous; tracked replies in existing state are not counted as pending by `pending_work_report`; compat reactivation fallback still risks no-trigger cycle collisions. |
| R6 Claude/Codex/Gemini | MAJOR | Claude returned MINOR; Codex returned MAJOR on production reactivation id mapping, missing `completed_at` stamping, single-client two-account label setup, non-recoverable paired state/learning writes, and untested snapshot freshness. Gemini repeated false missing-file findings from `/tmp`, plus valid pseudocode blockers around sweep stale skip, unlocked bootstrap state check, unbounded bootstrap prior state, missing thread enumeration, `lookup` KeyError, vague historical dedup matching, and undefined reactivation detection. |
| R7 Claude/Codex/Gemini | UNAVAILABLE | Fanout produced Claude and Gemini UNAVAILABLE artifacts. Codex emitted a raw CLI transcript with no parseable structured verdict because the installed Codex CLI streams session transcript output. No R7 verdict was used for plan advancement. |
| R8 Claude/Gemini, Codex unavailable | MAJOR | Claude and Gemini returned MAJOR. Remaining blockers: D5 current-cycle dedup candidate filtering was wrong for second-lifecycle no-trigger retries; missing baseline write/report rules could still produce false `mailbox_empty`; bootstrap prior-state validation was only in prose; `noise_excluded` was absent from final report returns; `list_threads` was misattributed as an existing contract API; sweep precheck was forgeable and unsafe without snapshot; intra-batch dedup was stale; and paired learning/state rows were positionally ambiguous. |

**Overall result:** FAIL after R8. This draft now contains post-R8 patches and must receive a fresh R9 adversarial review before any `status:plan-review` label.

Revisions made based on review:

- Added `docs/design/email-queue-state-schema.yaml` and `docs/design/email-as-queue-workflow.md` to implementation scope.
- Recast `needs_user_decision` as metadata rather than a sixth state.
- Added optional inbox-snapshot input for unknown-thread reporting; local state alone no longer claims full Gmail emptiness.
- Moved account-scope enforcement to report/ingest boundaries so existing low-level store contract tests can pass.
- Added path-first public API compatibility requirements for the existing #2017 contract tests.
- Added explicit account config and inbox snapshot contracts.
- Replaced the no-trigger dedup fallback with `cycle_id` + `dedup_event_id` semantics so retries dedup within a cycle but repeated lifecycle cycles can purge/extract/complete again.
- Added missing-extraction inbound state-machine edges and required design-doc transition-table updates.
- Replaced direct learning-log/state-log append pseudocode with same-lock append helpers and batch-aware sweep semantics.
- Added `dry_run=True` grace sweep semantics and snapshot/meta rebuild requirements.
- Restored one-time Gmail label creation as in-scope setup work for `ace` and `personal`, while keeping Gmail archive/delete out of #2026.
- Added exact #2026 label taxonomy.
- Added issue-task disposition table covering all seven #2026 implementation tasks.
- Added `scripts/email/email-queue-state.py` CLI, reactivation checker, and migration-label pass to file/test/acceptance scope.
- Made default account config alias-only; literal email normalization now requires local config or temp test config.
- Defined `needs_user_decision`/`needs_schema` as last-event-wins snapshot metadata.
- Added fail-closed behavior for literal-email snapshots when account config is missing.
- Added noise-label exclusion from unknown-thread counts.
- Added dynamic current-state validation under lock and a historical dedup-index requirement.
- Added stable `reactivation_id` fallback for no-trigger reactivation retries.
- Added real Gmail label API adapter scope and daily dry-run schedule entry.
- Added message-baseline fields for reactivation detection.
- Marked April plan and README edits as already applied by this planning session.
- Added a cold-start `reactivate_reply()` compatibility wrapper path that stamps `bootstrap_reactivation: true` while keeping normal production reactivation fail-closed without `latest_message_id` or `reactivation_id`.
- Removed the committed literal-email fixture proposal; tests must use inline reserved placeholder domains plus temporary account config.
- Added disabled-alias config semantics so known disabled accounts are reported as out of scope while unmappable literal email snapshots remain `config_missing`.
- Added `reactivation_pending_count` so replies on already tracked `completed`, `awaiting-reply`, or `purged` threads make `mailbox_empty: false`.
- Split normal production reactivation from cold-start bootstrap and required `MissingReactivationId` when neither `latest_message_id`, `reactivation_id`, nor bootstrap context exists.
- Clarified #2026 owns the checker/report command plus a non-destructive daily dry-run scheduled task; destructive deletion remains #2423 and live Gmail read orchestration remains #2024.
- Required live label existence verification for both in-scope accounts before closing #2026, or a blocked/user-approved split if credentials are unavailable.
- Added an importable CLI seam at `scripts/email/state/cli.py` so unit tests can inject fake Gmail clients while the hyphenated wrapper stays thin.
- Added local-state account-scope filtering so disabled/unknown local rows become warning buckets rather than pending work.
- Added `completed_at` stamping on completion transitions and tests for grace sweep timestamp reliability.
- Tightened historical dedup so no-trigger stale events from an earlier lifecycle raise instead of silently skipping.
- Added `list_threads()` and thread enumeration in the report/CLI contract.
- Moved cold-start bootstrap detection under the store lock and bounded it to allowed prior states.
- Added reactivation checker id mapping from `latest_message_id` to `triggering_message_id`, with stable `reactivation_id` fallback.
- Required reactivation precheck or inbox snapshot before sweep apply, and skip/report behavior for completed threads with new replies.
- Switched Gmail label setup to per-account client selection for `ace` and `personal`.
- Made state events authoritative for paired learning events with deterministic transaction ids and recovery/backfill.
- Added snapshot freshness/rebuild contract and tests for missing/corrupt/stale metadata.
- Scoped historical no-trigger retry matching to candidates in the current snapshot cycle.
- Added explicit message-baseline write rules and baseline-missing report/checker semantics that make `mailbox_empty: false`.
- Moved bootstrap prior-state validation to the `reactivate_reply()` wrapper.
- Added `noise_excluded` and `baseline_missing_count` to all report return branches.
- Reclassified `list_threads()` as a new report helper, not part of the existing #2017 public contract.
- Replaced forgeable sweep precheck booleans with a `ReactivationPrecheck` object tied to log path, account set, and snapshot hash.
- Updated batch append pseudocode to maintain an in-batch dedup set.
- Attached paired learning events directly to state events instead of relying on positional parallel lists.

---

## Risks and Open Questions

- **Risk:** Existing docs and old plans disagree on runtime state location. This plan chooses local runtime state and requires docs reconciliation because committing raw email state is worse.
- **Risk:** Gmail label creation depends on available Gmail client credentials. If unavailable during implementation, the code/tests can land, but #2026 closeout must record that production label setup remains blocked rather than claiming full completion.
- **Risk:** Existing tests currently xfail broadly. Implementation must remove xfail markers only after the real storage module passes the expanded tests.
- **Risk:** #2024 has its own stale ace-only plan. After #2026 reaches plan-review or approval, #2024 should be revised for the same two-account scope before implementation.
- **Risk:** The module will use `fcntl` on Linux. Implementation should guard POSIX-only imports or skip platform-specific tests cleanly on Windows; this issue is labeled `machine:dev-primary`.
- **Risk:** Do not add `scripts/email/__init__.py`. Tests rely on namespace-package behavior; adding that file can shadow Python's stdlib `email` package because `tests/conftest.py` puts `REPO_ROOT/scripts` on `sys.path`.
- **Open:** Whether production label setup should be run during the same implementation session or as a separate operator step after tests pass. Recommendation: implement and test the apply path, then run only the label-creation command for `ace` and `personal` if credentials are available; do not archive/delete Gmail in #2026.

---

## Complexity: T2

T2 because this creates a new state module with multiple submodules, local runtime persistence, concurrency/idempotency behavior, and tests, but it stays within one feature surface and avoids live Gmail archive/delete automation.
