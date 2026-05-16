# Telegram Hermes Desktop smoke checklist

> Manual UX checklist for [#2720](https://github.com/vamseeachanta/workspace-hub/issues/2720). Do not record bot tokens, chat IDs, phone numbers, or invite links in this file.

## Scope

This checklist verifies operator ergonomics only. Dispatch authority remains with GitHub issue labels, git lease refs, and repo-backed readiness.

## Linux coordinator / worker

- [ ] Telegram Desktop or mobile chat can send `/status --host dev-primary`.
- [ ] Response includes stable `host_id`, hostname, role, workspace root, and dispatch posture.
- [ ] Response does not include env values, bot tokens, API keys, phone numbers, or chat invite links.
- [ ] `/dispatch <issue> --mode plan --host auto` returns a dry decision or gated rejection with issue URL and host ID.
- [ ] Unsafe `GATEWAY_ALLOW_ALL_USERS=true` is reported as a readiness failure if present.

## Windows licensed hosts

- [ ] Host appears as `desktop-status-only` unless a separate approved implementation enables unattended execution.
- [ ] Paths are rendered as Windows paths, e.g. `D:\workspace-hub`, not Linux translations.
- [ ] Solver/license status can be summarized without exposing license server secrets.
- [ ] Dispatch attempts to Windows hosts return `host_status_only` unless dispatch is explicitly enabled in the registry.

## macOS portable host

- [ ] Host appears as manual/status-only.
- [ ] Paths are rendered as `/Users/...`.
- [ ] No cron/unattended execution is implied.

## Failure/rollback smoke

- [ ] Setting `telegram_hermes.dispatch_enabled: false` for a host removes it from dispatchable candidates.
- [ ] Token validation errors use `[REDACTED]` and do not echo token prefixes or suffixes.
- [ ] Existing lease refs are preserved as evidence during rollback.
