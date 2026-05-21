# Scheduler Routing Issue Trees

Use this reference when creating GitHub issues from evidence about scheduled jobs, cron, Hermes Gateway jobs, native provider CLIs, or provider-session observability.

## Core distinction to preserve

Do not conflate these two facts:

- **Runtime/control-plane flow**: whether scheduled AI work is executed through Hermes Agent / Hermes Gateway cron versus a native provider CLI such as `claude -p`.
- **Observability integration**: whether provider sessions are logged/exported into the repo ecosystem through hooks, session exporters, or provider-session audits.

A native Claude cron job can be visible in repo logs while still not flowing through Hermes Agent runtime. Issue bodies should say that explicitly.

## Pre-create evidence checklist

Before creating issues, gather and cite evidence from the relevant scheduler surfaces:

1. Canonical system schedule source, usually `config/scheduled-tasks/schedule-tasks.yaml`.
2. Rendered system cron, usually `bash scripts/cron/setup-cron.sh --dry-run`.
3. Live system crontab, usually `crontab -l`.
4. Hermes Gateway jobs, usually `hermes cron list`.
5. Provider/session logs or audit output proving whether native provider sessions and Hermes sessions are separate raw-log sources.
6. Any task wrapper showing direct provider invocation, e.g. `claude -p`, `codex`, or `gemini`.

## Recommended issue tree shape

Create a parent planning issue plus targeted follow-ups instead of one overloaded ticket:

- Parent: define the scheduler routing contract and classification taxonomy.
- Native-provider migration child: migrate or explicitly justify AI-executing system cron jobs that bypass Hermes Agent runtime.
- Exporter/audit child: harden fragile session export or audit scripts found during evidence gathering.
- Parity/report child: add a read-only report comparing canonical system cron, live crontab, and Hermes Gateway cron.

## Body-writing rules

- Preserve related existing issues as related/history, not duplicates, when they cover narrower health, parity, or historical setup work.
- Include the exact commands or files that produced the evidence.
- Use placeholders such as `<PARENT_ISSUE>` only in temporary body files; render them before `gh issue create`.
- Verify each created issue has `unresolved_placeholder=false` by re-querying the body.
- Keep gate language explicit: new issues start as intake/planning (`status:needs-plan`); no implementation occurs until plan, adversarial review, and user approval.

## Useful labels

Common labels for this class of issue, if present in the repo taxonomy:

- `enhancement` or `bug`
- `priority:high` or `priority:medium`
- `cat:operations`
- `cat:ai-orchestration`
- `cat:harness`
- `status:needs-plan`

Always verify labels exist before using them.
