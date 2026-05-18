# Multi-host Telegram/Hermes dispatch readiness and redaction gotchas

Use this reference when building or reviewing a Telegram-driven Hermes control plane across multiple machines.

## Dispatch readiness must fail closed

A host must not be marked `dispatchable: true` unless all command-plane prerequisites are present:

- dispatch is explicitly enabled for that host
- user allowlist is configured
- broad allow-all settings are false/unset
- required local tools are present (`git`, `gh`, `hermes` for GitHub-backed workspace dispatch)
- workspace policy files are present where the workspace root is local
- a bot-token environment variable is configured locally

Prefer a registry key such as `telegram_hermes.bot_token_env` with a safe default like `TELEGRAM_HERMES_BOT_TOKEN`. The readiness report should mention only the env var name, never the value.

## Redaction must cover formatted error reasons

Do not only redact explicit `token=` fields. Provider/library validation errors can echo token material in a reason string, e.g. `invalid token <token>`. Any formatter such as `format_token_validation_failure(token, reason=...)` should redact both:

- the explicit token argument
- secret-like substrings embedded in `reason` or nested status payload values

Regression test pattern:

1. Build fake credentials by string concatenation so repo scanners do not flag them as live secrets.
2. Assert the full credential and distinctive suffix are absent from rendered output.
3. Assert `[REDACTED]` appears and safe context remains.

## Local host checks are OS-independent

Do not gate local workspace/git/data checks on `os == linux`. In a multi-machine registry, a local dispatch host may be declared as macOS or Windows but still be the machine executing the readiness collector. If it is local and dispatch-enabled, it must run the same fail-closed checks regardless of declared OS:

- `workspace_root` exists on this machine
- workspace policy marker such as `AGENTS.md` is present when required
- git sync state is explicitly known and clean (`dirty=false`, `ahead=0`, `behind=0`, upstream present)
- required storage roots / remote mounts are present for the declared data-access profile

Regression test pattern: monkeypatch or construct the registry so a host resolves as local, set `os: macos` or `os: windows`, point `workspace_root` at a missing path, and assert `status == fail`, `dispatchable is False`, and the failure names the missing local workspace. This catches fail-open branches hidden behind Linux-only conditionals.

## Remote evidence is not coordinator evidence

A coordinator cannot prove a remote host is safe by checking coordinator-local environment variables or paths. For remote dispatch hosts, require a host-local evidence artifact with schema identity, producer, timestamp/freshness, host identity, and explicit host-local check results. Reject handcrafted minimal blobs such as `status: pass` without the evidence envelope.

Auto-selection must skip any host with `status != pass`, missing-data findings, missing git sync fields, dirty/ahead/behind state, or stale/invalid evidence. `warn` is not dispatchable.

## Redaction scope includes evidence and identifiers

Redaction must run recursively over readiness/status/evidence return values before they reach CLI, Telegram, GitHub comments, or provider review artifacts. Cover token-like values, token fragments, chat IDs, allowlists / `allowed_user_ids`, invite links, phone-like identifiers, and secret-like metadata keys. Preserve safe env var pointer names such as `TELEGRAM_HERMES_BOT_TOKEN`; redact values, not operator instructions.

## Sync boundary

Telegram is the command/notification plane. Git/GitHub/repo artifacts remain the synchronization plane. Do not imply Telegram itself syncs working trees or durable state across hosts.
