# New-Machine Setup — pointer

> Canonical user-facing docs have been migrated to **[`docs/setup/`](../../docs/setup/)** per [#2751](https://github.com/vamseeachanta/workspace-hub/issues/2751) G7.

## Where to read

| You want to ... | Read |
|---|---|
| Bootstrap a fresh machine | [`docs/setup/FRESH_MACHINE_SETUP.md`](../../docs/setup/FRESH_MACHINE_SETUP.md) |
| Audit / repair an existing machine | [`docs/setup/EXISTING_MACHINE_AUDIT.md`](../../docs/setup/EXISTING_MACHINE_AUDIT.md) |
| Authenticate Claude/Codex/GH/Gemini/Hermes | [`docs/setup/PROVIDER_AUTH_GUIDE.md`](../../docs/setup/PROVIDER_AUTH_GUIDE.md) |
| Read fleet status from the control plane | [`docs/setup/MACHINE_REGISTRY.md`](../../docs/setup/MACHINE_REGISTRY.md) |
| Diagnose a known issue | [`docs/setup/TROUBLESHOOTING.md`](../../docs/setup/TROUBLESHOOTING.md) |
| Browse the index | [`docs/setup/README.md`](../../docs/setup/README.md) |

## Why this file is a stub

This file (`.claude/docs/new-machine-setup.md`) is the **agent-internal namespace** — read by Claude during session bootstrap. The full user-facing walkthrough belongs in `docs/setup/` where it's discoverable to operators (and search engines, and other devs). This stub remains to satisfy backward-compatibility for any code that still references the old path.

## Quick refresher (single command)

```bash
bash scripts/setup/new-machine-setup.sh
```

Idempotent. Cross-platform (Linux/macOS/Windows Git Bash). Native Windows PowerShell sibling: `pwsh scripts/setup/new-machine-setup.ps1` (lands in Phase 5 of #2751).

## Operational tracker

After bootstrap, post the contents of `config/machine-baselines/<token>.md` as a comment on **[#2753](https://github.com/vamseeachanta/workspace-hub/issues/2753)** (evergreen tracker).
