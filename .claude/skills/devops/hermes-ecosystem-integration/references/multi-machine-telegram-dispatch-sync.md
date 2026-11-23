# Multi-machine Telegram dispatch + repo sync pattern

## Core rule

Telegram is a dispatch and notification surface, not a synchronization source of truth.

For multiple computers running Hermes with Telegram access, keep authoritative state in:

1. GitHub issues and labels for work routing, gate state, approvals, and closeout evidence.
2. Git remotes for code, docs, plans, skill changes, and generated handoff artifacts.
3. Repo-backed Hermes configuration and skill directories for reusable behavior.
4. Per-host runtime files only for secrets, local credentials, machine-specific paths, and service state.

## Minimum control-plane design

- Each host has its own hardened Hermes gateway and Telegram bot configuration, or a clearly namespaced shared bot with strict allowlists.
- Telegram commands should dispatch against explicit targets: host, repo, issue, branch/worktree, and approval gate.
- A host must run a preflight before accepting dispatched work: repo path exists, `git fetch` succeeds, current branch/worktree status is known, and no unrelated dirty state will be overwritten.
- Work completion should post back a GitHub issue comment and/or pushed commit evidence, then Telegram should summarize the durable links.
- Cross-machine sync should be pull/fetch/rebase/merge via git and issue state reconciliation, not copied chat transcript state.

## Readiness gates to encode in implementation

- Token and allowlist redaction at every status/reporting boundary.
- Per-host identity in Telegram replies so the operator knows which machine is acting.
- Dispatch policy that rejects ambiguous or unsafe requests instead of guessing the target machine/repo.
- Dry-run/status command before destructive actions.
- Approval prompts remain live and manual/smart per host; cron-mode approvals stay denied unless separately planned.
- Failure output includes durable recovery handles: issue URL, repo path, branch/worktree, and last command/evidence artifact.

## Skill linkage

- Use `operations/telegram-hermes-bot` for per-host bot installation, systemd, token hygiene, and mobile approval smoke tests.
- Use this `hermes-ecosystem-integration` skill for repo-backed sync, config/skill propagation, and multi-host control-plane design.

## Anti-patterns

- Treating Telegram chat history as the audit log.
- Letting multiple hosts write to the same branch/worktree without explicit ownership.
- Reporting "synced" based only on a Telegram acknowledgement rather than `git`/GitHub evidence.
- Printing tokens, env files, or allowlist internals into Telegram status output.
