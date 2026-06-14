# Email-as-Queue Workflow

Issue: #2017

Email is treated as a queue, not a durable archive. The durable record is the structured extraction written to the target repository; the raw email remains an operational input.

## Scope

#2017 defines the contract artifacts used by downstream implementation:

- Local queue state model and schemas.
- CRE extraction schema.
- Spam classification rules.
- Redacted fixture corpus and contract tests.

Pipeline orchestration belongs to #2024. Queue-state storage implementation belongs to #2026. New Gmail-side delete/archive automation belongs to #2423.

Existing `gmail-archive-extract.py` routing behavior is grandfathered production infrastructure. This design does not add new Gmail mutations.

#2026 implements the local state layer for the two approved accounts only:

- `ace` (`vamsee.achanta@aceengineer.com`)
- `personal` (`achantav@gmail.com`)

`skestates` remains out of scope until a future issue explicitly adds it. In #2026, "mailbox empty" means no pending work among known in-scope threads and, when a caller supplies an inbox snapshot, no unknown in-scope Gmail threads. Local state alone reports unknown-thread coverage as `not_evaluated` rather than claiming the mailbox is empty.

## Decisions

### State Authority

Queue state is local-only in v1:

- Append-only event log: `~/.hermes/email-state/queue-state.jsonl` by default, overrideable with `EMAIL_QUEUE_STATE_DIR`.
- Materialized read snapshot: `queue-state-snapshot.yaml` next to the event log.
- Snapshot freshness metadata: `queue-state-snapshot.meta.yaml` next to the event log.
- Learning/correction log: `queue-learning-log.jsonl` next to the event log.
- Account normalization config: `accounts.yaml` next to the event log by default, overrideable with `EMAIL_QUEUE_ACCOUNTS_CONFIG`.

Runtime state is private machine state and must not be committed. Durable extracted facts belong in the appropriate repository ecosystem target, not in raw email archives.

Every thread identity is scoped by `(account_id, thread_id)`. Snapshot keys use `{account_id}::{thread_id}`.

### Extraction Format

Extracted records are YAML. CRE listings use `scripts/email/extraction-schemas/cre-listing-v1.yaml` and target `assethold/data/cre-listings`.

### Deletion Safety

`completed` threads are retained through a seven-day grace window. After the grace window, local queue state transitions to `purged`; Gmail content is not touched by this contract.

### Reactivation

Replies on `awaiting-reply`, `completed`, or `purged` threads transition back to `extracted` and link to the prior extraction when it exists. If a linked extraction is missing, the system emits `extraction_missing_on_reactivation` to both queue-state and learning logs, then treats the message as new inbound.

### Learning Loop

Manual corrections are appended to `queue-learning-log.jsonl`. Quarterly review reports summarize misclassifications, unknown senders, schema gaps, and spam false positives.

### Spam Rules

`scripts/email/spam-detection-rules.yaml` is evaluated before routing. Spam classification skips #2017 queue-state creation. If the sender is unmapped, the pipeline injects a synthetic `DELETE` routing action so the grandfathered routing path has an explicit action.

## State Machine

States: `inbound`, `extracted`, `awaiting-reply`, `completed`, `purged`.

Transitions:

- `inbound -> extracted`: actionable, data extraction, drive document, or archive classification.
- `extracted -> awaiting-reply`: extracted data exists and a response is pending.
- `extracted -> completed`: extracted data exists and no response is pending.
- `awaiting-reply -> extracted`: new reply reactivates the topic.
- `awaiting-reply -> completed`: user marks complete.
- `completed -> purged`: seven-day grace has elapsed.
- `completed -> extracted`: new reply reactivates the topic.
- `purged -> extracted`: new reply reactivates with prior extraction context when available.

Spam/noise/unsubscribe classifications may produce routing actions but do not create a #2017 queue-state entry.

## Dependency Contract

| Component | Owner |
|---|---|
| Design contract, schemas, fixtures, xfail contract tests | #2017 |
| `scripts/email/queue_state.py` storage implementation | #2026 |
| Pipeline orchestration and scheduled sweep wiring | #2024 |
| Gmail-side delete/archive automation | #2423 |
| Skill consolidation | #2019 |
