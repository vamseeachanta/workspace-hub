# Telegram/Hermes dispatch registry schema guardrail

Session-derived detail from the multi-machine Telegram/Hermes dispatch work around issue #2720.

## Durable lesson

Dispatch policy loaders must distinguish **inventory schema** from **dispatch schema**.

A workstation registry may contain machines that are useful for inventory or future planning but are not dispatch targets yet. Those records can legitimately be incomplete for dispatch-only fields. A loader that requires every machine to have dispatch-grade fields (for example `storage`, `telegram_hermes.hermes_profile`, freshness thresholds, or data-access profile) can fail before host selection ever evaluates the intended dispatch hosts.

## Recommended contract

1. Require only minimal inventory fields for every machine record:
   - stable machine id
   - hostname
   - OS/platform
   - broad role or class
2. Require dispatch-grade fields only when `telegram_hermes.dispatch_enabled: true` or equivalent is set:
   - `telegram_mode`
   - `hermes_profile`
   - `sync_policy`
   - `data_access_profile`
   - readiness freshness thresholds
   - repo/storage fields consumed by dispatch policy
3. Treat unknown or incomplete non-dispatch machines as inventory entries, not dispatch candidates.
4. Fail closed when an enabled dispatch host is missing a required dispatch field.
5. Add tests for both sides:
   - a non-dispatch inventory-only machine missing dispatch fields must not break registry loading
   - a dispatch-enabled host missing a dispatch-required field must raise a policy error
6. Add a live-registry smoke test against `config/workstations/registry.yaml` before claiming dispatch automation is ready.

## Review smell

If dispatch policy loading fails on a host that the command did not select and that is not dispatch-enabled, the loader is over-validating inventory data and should be split into baseline validation plus dispatch-enabled validation.
