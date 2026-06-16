# Statusline Provider Coverage

Issue: [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893)

The compact AI usage statusline renders the provider coverage contract as:

```text
C:<weekly-remaining>%|O:<weekly-remaining>%·<weekly-reset>d·5h<five-hour-remaining>%|G:<binding-window-remaining>%·<reset>|H=O
```

Provider meanings:

- `C` is Claude. Live Claude Code `rate_limits.seven_day` data is authoritative when present. If it is absent, the statusline may render a local stats-cache estimate, but it must mark that estimate with `?`.
- `O` is Codex/OpenAI. Weekly remaining comes from `week_pct` as `100 - week_pct`; the 5-hour suffix comes from `five_hour_pct` as `100 - five_hour_pct`. `five_hour_pct` is produced by `scripts/ai/assessment/query-codex-usage.sh` from Codex app-server `.primary.usedPercent` and session-log `.payload.rate_limits.primary.used_percent`, so it is used-polarity at the producer.
- `G` is Gemini via the agy usage snapshot helper. It renders the binding window, not a fabricated weekly equivalent.
- `H=O` is Hermes as an explicit alias to the Codex/OpenAI pool. Hermes does not get an independent quota percentage unless a future collector proves a separate pool exists.

The `O` 5-hour display is intentionally remaining-polarity. This differs from `scripts/ai/assessment/lib/display.sh`, which currently prints the raw `five_hour_pct` used-polarity field. Do not compare those two strings as if they shared polarity.

`scripts/readiness/statusline_provider_coverage.py` produces repo-level renderer-contract evidence from freshness-controlled fixtures. A `COMPLETE` renderer contract proves that the statusline can render the required provider surfaces from seeded inputs; it is not live telemetry proof for the current provider accounts.

The helper refuses final `COMPLETE` when measured statusline paths are dirty or missing, or when the [#2894](https://github.com/vamseeachanta/workspace-hub/issues/2894) closeout blocker is `open` or `unknown`.
