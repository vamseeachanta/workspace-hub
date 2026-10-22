# Model registry drift and quota snapshot checks

The nightly `R-MODEL-DRIFT` gate checks registry consistency and readable local
model settings. It does not discover provider availability or prove that the
configured generation is the newest available generation.

## Registry rules

Every `latest_models` key receives a consistency result. IDs shall be non-empty
strings and shall occur in `context_windows_k`. Shared IDs require an exact
`model_aliases` mapping from ID to the list of keys allowed to share that ID.
Objects marked `deprecated: true` with a `model_id` shall occur only under
`audit`; their IDs shall not be referenced elsewhere, including context maps.
Duplicate YAML mapping keys fail instead of accepting the last definition.

`last_updated` is read as a calendar date. The default age bound is **14 days**,
a maintainer policy choice carried from the existing nightly registry guard,
not a model-provider service guarantee. `MODEL_REGISTRY_MAX_AGE_DAYS` or the
validator's `--max-age-days` overrides this positive bound. Age equal to the
bound passes; greater age or a future date warns. Missing or malformed dates
are `NOT_EVALUATED`. The older `R-REGISTRY` file-modification-time guard remains
independent; checkout timestamps do not establish the date of model research.

## Live configuration bindings

| Registry key | Source | Exact key path |
|---|---|---|
| `openai_primary` | User/project `.codex/config.toml` | top-level `model` |
| `openai_primary` | User/project `.hermes/config.yaml` | top-level `model` |
| `claude_primary` | User/project `.claude/settings.json` | JSON `$.model` |

Table 1. Explicit file bindings; these files are read, never executed.

Project values override user values when the project file contains `model`.
A malformed readable file fails, even when another file could supply a value.
Claude settings declare only one configured default: `claude_strong`,
`claude_balanced` and `claude_fast` have no independent live binding and report
`NOT_EVALUATED`. Aliases such as `opus` are not silently expanded: a value
different from the registry fails and includes both values. A value absent from
all `latest_models` IDs also fails as unknown, without inferring generation order.
Environment and interactive session overrides are outside this file-only check.

`NOT_EVALUATED` means evidence is missing, not that the check passed. The gate
prints each result and counts compared and unevaluated observations. A partial
run cannot emit an aggregate pass. Python 3.11 and PyYAML are required; an absent
validator runtime is explicitly unevaluated.

To update the registry, confirm model IDs and context sizes against current
provider documentation, update the maps and `last_updated`, declare any aliases,
move deprecated definitions to `audit`, and run the fixture tests. This check
does not authorize inventing context sizes for missing entries.

## Worked example

The fixture directory `tests/readiness/fixtures/model-drift` contains a synthetic
registry and a Claude live-config fixture. Copy the registry into a temporary
project's `config/agents/model-registry.yaml` and `settings.json` into its
`.claude/settings.json`. Use an empty temporary user root. Run:

```sh
python3 scripts/readiness/model_drift.py --registry "$example/config/agents/model-registry.yaml" \
  --user-root "$empty_user" --project-root "$example" --today 2026-10-15
```

The exact output below uses a tab between status and detail. The independent
calculation is October 15 minus October 1 = 14 calendar days; one supplied
Claude observation is compared and the strong key has no live binding.

```text
PASS	claude_primary: registry consistent
PASS	claude_strong: registry consistent
PASS	freshness: age_days=14 bound_days=14
PASS	claude_primary/claude: live=example-alpha registry=example-alpha
NOT_EVALUATED	claude_strong/live: no documented configuration binding
INFO	live: compared=1 not_evaluated=1
```

## Quota timestamps and limits

`query-quota.sh`, called by `provider-utilization-refresh.sh`, writes repository
snapshots through `scripts/ai/quota_snapshot.py`. The top-level `generated_at`
contains `iso8601` (UTC string) and `epoch` (Unix seconds). A same-directory
temporary file is flushed and renamed; invalid input or a failed rename leaves
the previous destination intact. Every agent has `source` and `as_of`; unknown
observation dates remain JSON null. Refreshing a copied entry does not invent
its observation time. Snapshot publication time and observation time differ.

The compatibility `timestamp` field is retained because the existing statusline
uses that field. Its configurable `STATUSLINE_QUOTA_MAX_AGE_HOURS` default is
6 hours, the existing consumer policy: older or undatable files receive `?`.
Tests use a fixed clock and demonstrate the existing boundary. Direct
`generated_at` consumption, rejection of a missing `generated_at` despite a
present legacy timestamp, and per-observation age gating remain follow-up work
because the permitted staging manifest excludes the statusline directory.

Refresh scheduling can be inspected without changing it:

```sh
crontab -l
systemctl --user list-timers --all --no-pager
```

These commands establish installed schedule entries only. Recent successful
refresh evidence requires reading the matching log and embedded snapshot dates.

## Sources

- [YAML 1.2.2, sections 3.2.1.3 and 10.2](https://yaml.org/spec/1.2.2/):
  mapping-key uniqueness and Core-schema scalar interpretation. The validator
  uses PyYAML's safe loader with duplicate-key rejection; registry IDs must be
  strings and ambiguous YAML scalars shall be quoted. Full YAML 1.2 conformance
  is not claimed for PyYAML's scalar resolver.
- [RFC 3339 (2002), sections 5.6 and 5.7](https://www.rfc-editor.org/rfc/rfc3339):
  the Internet profile of ISO 8601 and UTC timestamps. The licensed ISO document
  is not required or reproduced; no provider numerical specification is assumed.
- `scripts/readiness/nightly-readiness.sh`, `R-REGISTRY`: existing age policy.
- `.claude/statusline-command.sh`, `quota_file_state`: existing quota-age policy.

All example IDs, capacities and quota percentages are synthetic fixture inputs.
Expected dates and percentages are independently calculated in test docstrings.
