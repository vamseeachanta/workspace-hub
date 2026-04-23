# Prospect Deliveries Log

> Append-only ledger of every prospect-demo delivery. Each row is
> written by `prospect_adapter.deliver()` (or an engineer by hand for
> off-pipeline manual deliveries) and MUST NOT be mutated after the
> fact — corrections are a NEW row referencing the prior row's
> `prospect_id` + `delivered_utc`.
>
> See the state-machine spec in
> `docs/gtm/prospect-demo-sop.md` §3 for the canonical column meanings.

## Column schema

| Column                  | Type / enum                                                                | Nullable |
|-------------------------|----------------------------------------------------------------------------|----------|
| `prospect_id`           | string (from `prospect.company` slug + date)                               | no       |
| `demo`                  | enum: `demo_01`..`demo_05`                                                 | no       |
| `delivered_utc`         | ISO-8601 timestamp (first terminal-state transition time)                  | no       |
| `email_sent_utc`        | ISO-8601 timestamp                                                         | yes (null if `state == FAILED_EMAIL`) |
| `email_attempt_count`   | integer 1..3                                                               | no       |
| `url_published_utc`     | ISO-8601 timestamp                                                         | yes (null unless `state == DELIVERED` with URL) |
| `url_publish_attempt_count` | integer 0..3                                                           | no       |
| `gated_url_hash`        | sha256 hex prefix (first 16 chars) of `(prospect_id + salt + date)`        | yes (null when URL not published) |
| `purge_after_utc`       | ISO-8601 timestamp copied from `intake.output.purge_after_utc`             | yes (null when no URL published) |
| `state`                 | enum: `DELIVERED`, `DELIVERED_EMAIL_ONLY`, `FAILED_EMAIL`, `UNPUBLISHED`   | no       |
| `fallback_applied`      | enum: `F1`, `F2`, `F3`, `F4`, `F5`                                         | yes (null when no fallback triggered) |
| `notes`                 | free-form string (NO prospect-specific engineering values)                 | yes      |

## Deliveries

| prospect_id | demo | delivered_utc | email_sent_utc | email_attempt_count | url_published_utc | url_publish_attempt_count | gated_url_hash | purge_after_utc | state | fallback_applied | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|

<!-- Append one row per delivery below this line. -->
