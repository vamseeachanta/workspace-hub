# CLI option behavior across output formats

Option help and registration do not establish that an option changes output.
The behavior contracts for issue #3447
execute commands with synthetic local inputs and compare independently expected
rows in each advertised format.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Add option parity contracts and structured validation errors to detect format-dependent behavior. |

## Bounded command inventory

The following inventory covers the commands exercised by these tests. It is not
a repository-wide or cross-repository coverage claim.

| Command | Advertised formats | Observable options covered | Contract tests |
| --- | --- | --- | --- |
| `scripts/ai/wrk_cost_report.py` | Table, CSV | Positional filter, input file, CSV selector; empty selection and unsupported JSON | `tests/ai/test_cost_cli_format_parity.py` |
| `scripts/data/drive-index-search/search.py` | Tab-separated text, JSON | Registry, query, domain, drive, repeated index, limit; invalid timeout and unsupported CSV | `tests/data/drive_index_search/test_format_parity.py` |

Neither command advertises a detail option. CSV is rejected by search and JSON
is rejected by cost reporting. No extra format is inferred from another command.
The linked provider-routing example (worldenergydata issue #924)
motivates these contracts; its package is outside this repository's write scope.

## Behavior and error contract

Each format is tested against literal expected identities or independently
summed totals. Equality between formats alone could preserve the same defect in
both. Filtered tests assert exclusion as well as inclusion; empty filters have
separate assertions. Search tests compare ordered paths, preserving the limit's
visible meaning. Cost tests compare all rendered data columns and detect duplicate
identities. Timestamps and format-specific presentation are not compared.

Search selects the JSON error envelope before parsing the complete invocation.
Argument validation, including missing arguments, invalid types, unknown options,
nonpositive limits and nonfinite or nonpositive timeouts, returns an error object
on standard output and a diagnostic on standard error. Registry validation uses
the same shape, with a distinct code:

```json
{"error": {"code": "argument_error", "message": "--limit must be positive"}}
```

The other code is `registry_error`. Error invocations retain argparse's existing
invalid-invocation exit status. Successful search JSON retains its existing
schema; registry errors now return an explicit error instead of an empty success
envelope. Partial index failures retain the existing `coverage_gaps` behavior.
An output selector after the `--` delimiter is positional text and does not
activate JSON. JSON abbreviations accepted by argparse retain error handling.

The source of the registry schema and exit behavior is the command and
`scripts/data/drive-index-search/registry.py`. Positive limits and timeouts are
CLI input constraints, not sourced engineering acceptance limits. There are no
engineering equations, coefficients or acceptance constants in this change.

## Worked example

Use a writable scratch directory through `TMPDIR`, then run from the repository
root. The amounts below are synthetic recorded costs, not provider prices:

```sh
cat > "$TMPDIR/parity-costs.jsonl" <<'EOF'
{"wrk":"alpha","input_tokens":10,"output_tokens":2,"cost_usd":0.2,"provider":"fixture"}
{"wrk":"alpha","input_tokens":20,"output_tokens":3,"cost_usd":0.3,"provider":"fixture"}
{"wrk":"beta","input_tokens":7,"output_tokens":1,"cost_usd":0.1,"provider":"fixture"}
EOF
uv run --no-project python scripts/ai/wrk_cost_report.py alpha --data-file "$TMPDIR/parity-costs.jsonl"
uv run --no-project python scripts/ai/wrk_cost_report.py alpha --data-file "$TMPDIR/parity-costs.jsonl" --csv
```

Method: select alpha, then sum its input tokens, output tokens and recorded costs.
The hand calculation is inputs = 10 + 20 = 30; outputs = 2 + 3 = 5;
cost = 0.2 + 0.3 = 0.5; record count = 2. Beta must be absent. CSV answer:

```csv
WRK-ID,INPUT,OUTPUT,COST_USD,SESSIONS,PROVIDERS
alpha,30,5,0.5000,2,fixture
```

The table must contain the same alpha totals. The cost test module's docstring
records this independent calculation. Search's test docstring independently
defines the set intersections: land contains alpha and beta; marine contains
gamma; filtering land by marine yields no rows. Equal fixture text makes the
documented canonical-path tie breaker determine the limited result, alpha.

## Running and extending the contracts

```sh
uv run --no-project --with pytest --with pyyaml python -m pytest tests/ai/test_cost_cli_format_parity.py tests/data/drive_index_search/test_format_parity.py -q -rA -p no:cacheprovider
```

Set pytest's `--basetemp` to a new directory under the chosen scratch root when
test artifacts must stay outside the worktree. Search fixtures direct invocation
metrics to scratch and require no live indexes or network. The broader existing
adapter suite requires its separately generated SQLite fixture; these new
contracts create their own JSONL indexes.

For another command, enumerate every advertised format and each filtering or
detail option. Run an unfiltered baseline and the same option cases in each
format, asserting independent expected rows, changed fields and excluded rows.
For unsupported combinations, assert a nonzero exit and an explicit diagnostic.
Exercise missing arguments and invalid values with the machine-readable selector
both before and after the invalid argument. Keep fixture oracles independent of
the implementation and document any hand calculation in the test docstring.

Later coverage includes the issue-review command's table/YAML/JSON grouping and
consumer packages with detail options. Those commands are not claimed as tested
by this bounded change. Independent provider review remains required before merge.
