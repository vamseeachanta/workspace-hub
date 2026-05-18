# Email skill state labels

> Email is a queue, not an archive. These labels mark queue state; they are not a retention policy by themselves.

## Gmail labels

| Label | Meaning | Owner action | Exit condition |
|---|---|---|---|
| `wh-email/extracted` | Actionable data has been extracted from the thread into the appropriate durable target or local state tracker. | Confirm extracted data is complete and useful. | Move to `wh-email/completed`, `wh-email/awaiting-reply`, or delete the email if no live action remains. |
| `wh-email/awaiting-reply` | A human or external party must reply before the topic can close. | Keep the thread live and review when a new reply arrives. | New reply reactivates the thread for triage; resolved thread moves to `wh-email/completed`. |
| `wh-email/completed` | The topic is resolved and no further action is expected. | Apply the completion grace period, then delete if no new activity appears. | Delete after the configured grace period unless a new reply reopens the topic. |
| `wh-email/noise` | The message has no durable value or action after triage. | Delete or unsubscribe/block through the current outreach/cleanup workflow. | Email removed from the queue. |

## Local tracker

`~/.hermes/email-state.yaml` is the local authoritative queue-state tracker for automation runs. It may reference account aliases, message/thread identifiers, extraction targets, and current state. Do not copy credentials, OAuth tokens, cookie values, or secret file contents into this repository; summarize any credential-dependent setup as `[REDACTED]` in committed docs.

## Queue rule

The active path is: triage unread mail, extract only durable/actionable information, act or wait, then delete completed/noise messages. Deprecated archive-everything flows remain only under `.claude/skills/email/_archived/` for historical reference.
