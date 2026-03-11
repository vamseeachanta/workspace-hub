# WRK-1069 Plan — Codex

## Verdict: MAJOR

Plan needs revision before implementation proceeds.

### Findings

- [P1] Static pricing.yaml is insufficient for historical accuracy. Token pricing
  changes over time; records need effective-date anchored pricing to avoid
  retroactive mispricing. Mitigation: JSONL cost_usd field stores calculated cost
  at record time — use that as primary source; pricing.yaml is fallback only for
  missing cost_usd entries. Add effective_from date to each model entry.

- [P1] Join key between JSONL records and pricing.yaml not defined. Need explicit
  normalization: JSONL model field → pricing.yaml models key (strip provider
  prefix, lowercase). Fallback to defaults.unknown_model with visible warning.

- [P2] "Malformed JSONL skipped" too weak for accounting path. Totals can look
  valid while underreporting spend. Must surface skipped count in output:
  "(N records skipped — malformed)" printed after table.

- [P2] Non-blocking cost print in close-item.sh creates no auditable artifact.
  Should persist evidence/cost-summary.yaml in WRK assets dir at close, not just
  print to terminal.

- [P2] Exit-code handling underspecified. Define explicitly: exit 0 = success
  with data, exit 1 = no data found, exit 2 = config/infrastructure error.
  close-item.sh suppresses only exit 1; warns on exit 2.
