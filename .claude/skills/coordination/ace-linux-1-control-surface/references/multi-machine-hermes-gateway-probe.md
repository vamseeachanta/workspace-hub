# Multi-machine Hermes/Gateway probe pattern

Use this reference when the user asks whether `ace-linux-1` can set off or monitor runs across multiple machines through Hermes, Telegram, GitHub, SSH, or workstation workers.

## Session-derived pattern

A useful control-surface probe should separate three questions:

1. **Machine reachability** — DNS/hosts, ping, SSH/WinRM/Tailscale, and registry-declared remote access path.
2. **Program readiness** — Hermes CLI version, gateway service status, GitHub auth, provider CLI availability (`claude`, `codex`, `gemini`), tmux/systemd state, and sanitized config signals.
3. **Dispatch topology** — whether the machine should poll Telegram directly, act as an SSH worker, or pick work up from a GitHub/file ledger.

## Key pitfalls

- Multiple Hermes gateways polling the same Telegram bot token cause Telegram `getUpdates` conflicts. Treat this as a topology bug, not a generic gateway failure.
- A machine can have Hermes installed and still be unusable as a worker if it has no reachable execution path from the control surface.
- Registry truth matters: if `config/workstations/registry.yaml` says a host has `ssh: null` and no Tailscale IP, report it as unverified from `ace-linux-1` instead of pretending the control surface can probe it.
- User-reported messaging login is not enough evidence for orchestration readiness. Verify gateway platform configuration and active service state per machine.
- Readiness is evidence-based, not registry-based: local hosts must run env/workspace/git/data checks on the coordinator; remote dispatch hosts must provide fresh host-local evidence written by that host. Missing, stale, malformed, or unsafe evidence is a fail-closed blocker.
- `warn` is status-only. Do not treat warning states as dispatch-eligible just because the operator wants to start a run.
- Redact tokens, API keys, connection strings, Telegram chat/user IDs, invite links, phone-like values, and credential paths before putting evidence into GitHub comments.

## Readiness evidence checklist

For a dispatch-capable host, collect or verify:

1. **Coordinator/local evidence** — run the readiness probe from the control surface for hosts whose workspace is locally accessible. Do not branch only on a declared OS string; a local Windows/macOS/Linux host still needs local env/workspace/git/data checks.
2. **Remote host-local evidence** — for remote hosts, require a JSON/status artifact generated on that host and stored in the configured evidence directory. The coordinator may validate freshness, schema, safety, and redaction, but it must not infer remote filesystem/git/data health from registry entries alone.
3. **Pass-only dispatch** — a host is dispatchable only when readiness is `pass`. `warn` can appear in dashboards, but it should never be selected for automatic work launch.
4. **Fail-closed blockers** — missing Telegram allowlist/token env pointers, dirty worktree, no upstream, ahead/behind drift, missing data roots, stale evidence, malformed evidence, or unsafe evidence output should block dispatch until explicitly remediated.
5. **Sanitized issue evidence** — status comments can include summarized failures and artifact paths, but must not include bot token tails, chat/user IDs, invite links, phone-like values, raw env values, or connection strings.

## Recommended status comment shape

When updating a GitHub issue, include:

- timestamp and probe host
- table of requested machines
- reachability, Hermes installed, gateway status, messaging platform status, GitHub auth, agent CLIs, and blockers
- evidence bullets with commands summarized, not raw secrets
- current blockers
- next logical steps and acceptance criteria

## Machine topology/status contract

Before claiming that one control surface can set off runs across several machines, capture a lightweight topology contract. This is an acceptance item for multi-machine orchestration issues, not optional narrative.

Minimum fields:

- host identity, aliases, OS, and intended role
- control path from `ace-linux-1`: SSH, Tailscale/SSH, WinRM, gateway callback, GitHub/file ledger, or `unverified`
- Telegram/gateway mode: single polling gateway, distinct bot token, worker-only, or disabled
- actual repo roots discovered live per host, not just registry-declared roots
- tier-1 repo availability and cleanliness per host
- local data volumes and cross-mounted remote volumes
- local-vs-remote data authority: which host owns the source data and which paths are mounts/caches
- program/tool status: Hermes, Gateway, GitHub CLI auth, provider CLIs, tmux/systemd, and domain tools
- GitHub mutation authority: usually `ace-linux-1` unless worker auth/readiness is freshly proven
- safe dispatch class: `control-plane only`, `Linux open-source engineering worker`, `Windows licensed simulation worker`, `status-only/manual host`, or `blocked`
- next logical step: fix reachability, update registry, add status probe, create worker ledger, or defer to licensed-machine planning

If live discovery conflicts with `config/workstations/registry.yaml`, treat the registry as stale and say so explicitly in the GitHub issue. Do not route work based only on registry entries.

## Layered fleet framing

For the current workspace, default to this framing until a fresh probe proves otherwise:

1. **Linux control/data layer** — `ace-linux-1` owns approvals, GitHub mutation, Telegram operator interaction, queue selection, and final reconciliation.
2. **Linux execution/data-adjacent worker layer** — `ace-linux-2` can run bounded open-source engineering or AI worker lanes after SSH/login-shell/tool/repo readiness is verified.
3. **Licensed Windows simulation layer** — `licensed-win-1` and `licensed-win-2` are external/company-specific licensed-software hosts. Keep them as a separate readiness/security/GUI/licensing class; do not fold them into Linux dispatch until their control path and constraints are explicit.

## Topology recommendation

Default recommendation: keep one Telegram-polling control gateway on `ace-linux-1`; use other machines as workers through SSH, Tailscale/SSH, WinRM, or a GitHub/file polling ledger. Only use per-machine Telegram gateways if each machine has a distinct bot token and explicit allowlist/routing rules.
