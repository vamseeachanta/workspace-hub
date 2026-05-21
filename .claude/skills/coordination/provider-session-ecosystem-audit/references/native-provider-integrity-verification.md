# Native provider integrity verification

Use this reference when a user asks whether work done through a native provider CLI (for example Claude Code) is flowing through, bypassing, or corrupting the Hermes/repo ecosystem.

## Core distinction

Do not collapse these two claims:

1. **Runtime/proxy flow**: native Claude runs through Hermes Agent as the executing runtime.
2. **Repo ecosystem integration**: native Claude writes provider-specific telemetry into repo-local orchestrator/audit artifacts that Hermes can inspect alongside Hermes/Codex/Gemini.

The common verified architecture is usually the second, not the first: native providers keep native session stores, while hooks/exporters feed provider-specific streams into `logs/orchestrator/<provider>/`.

## Verification sequence

1. Inspect the provider's native session store.
   - Claude example: `~/.claude/projects/<cwd-encoded>/*.jsonl`.
   - Confirm current session IDs, timestamps, and whether recent rows mention Hermes paths.

2. Inspect repo hook configuration before making claims.
   - Claude example: `.claude/settings.json` for hook registration.
   - Then inspect the hook script that writes session telemetry, for example `.claude/hooks/session-logger.sh`.

3. Verify exact write destinations in the hook/exporter script.
   - Expected Claude pattern: primary write to `.claude/state/sessions/session_YYYYMMDD.jsonl` and dual-write to `logs/orchestrator/claude/session_YYYYMMDD.jsonl`.
   - Treat absence of `~/.hermes`, `/home/*/.hermes`, or `logs/orchestrator/hermes` write paths as evidence of provider-path isolation.

4. Inspect current-day orchestrator records for the native provider.
   - Example: `logs/orchestrator/claude/session_YYYYMMDD.jsonl`.
   - Check tool/file/cmd fields for unintended writes to Hermes-owned paths.

5. Run the provider ecosystem audit from repo root when available.
   - Workspace-hub example: `uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py --stdout`.
   - Confirm each provider is represented separately, e.g. `claude`, `hermes`, `codex`, `gemini`, with `source=raw_logs` and current record counts.

6. State the conclusion with the right precision.
   - Good: "Native Claude does not appear to run through Hermes Agent runtime, but it is integrated into the repo observability/governance ecosystem via Claude-specific hooks and orchestrator logs."
   - Avoid: "Claude flows through Hermes" unless the runtime/proxy path is actually proven.

## Pitfall: silent exporter failure under `set -euo pipefail`

Exporter scripts that extract dates from filenames with a pipeline can exit before a later empty-value guard runs. Example anti-pattern:

```bash
session_date=$(echo "$basename" | grep -oE '[0-9]{8}' | head -1)
[[ -z "$session_date" ]] && continue
```

With `set -euo pipefail`, a filename such as `session_bg_22fe54.json` causes `grep` to return 1 and the script exits before `[[ -z ... ]]` executes.

Durable fix pattern:

```bash
session_date=$(echo "$basename" | grep -oE '[0-9]{8}' | head -1 || true)
[[ -z "$session_date" ]] && continue
```

Classify this as an exporter robustness issue, not evidence that a native provider corrupted Hermes logs, unless the raw logs/audit are also unreadable or inconsistent.

## Reporting format

When answering the user, separate:

- **Confirmed**: native session locations, hook write paths, current-day orchestrator evidence, audit success.
- **Not proven**: runtime/proxy flow through Hermes.
- **Caveat**: exporter/script failures and whether they affect freshness only or actual log integrity.
- **Next action**: harden exporter or hook if needed.
