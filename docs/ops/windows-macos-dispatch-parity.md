# Windows / macOS pull dispatch

Deckhand retired 2026-10-18 (deckhand issue 599). The Telegram venue and Hermes
gateway promotion instructions formerly on this page no longer apply.

Use the existing [pull/poll dispatch guide](pull-dispatch-no-ssh.md) and
[continuous pull-dispatch runbook](../runbooks/dispatch-pull.md). On main, those
guides already document routed-card polling, fenced Git leases, outbound Git
reporting, per-issue command bindings and explicit write gates. They do not
require a bot announcement to discover work.

Retain the platform scheduler already configured for the existing pull workflow.
Scheduling and execution remain opt-in; retain the existing authorization,
readiness and repository access checks. Do not infer execution readiness from
the existence of a schedule or a successful poll.

Historical parity plans and deployment evidence remain in Git history and dated
reports. They do not establish current bot availability.
