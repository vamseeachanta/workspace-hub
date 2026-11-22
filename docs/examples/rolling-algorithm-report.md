# Rolling algorithm report layout example

The [executable example](../../examples/algorithm_runs/rolling_report_example.py)
renders synthetic successful and reproducible failed runs into a single HTML
document. The [report contract](../architecture/algorithm-run-dataset-contract.yaml)
defines the mandatory Inputs and Outputs sections and the optional section names.
The [decision manual, report section](../governance/2026-07-10-algorithm-run-dataset-decision-manual.html#report)
defines their applicability and the separation of failed runs from analysis.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-26 | Added an executable synthetic layout to demonstrate the existing section contract. |
| 1 | 2026-10-27 | Added explicit scope and verification instructions to make the example boundary reproducible. |

## Plan-lite

The example will remain limited to the pure HTML renderer in
`examples/algorithm_runs/rolling_report_example.py`, this documentation and the
structural tests in `tests/architecture/test_rolling_report_example.py`.
Verification will cover mandatory sections, optional-section applicability,
failed-run exclusion, text escaping, restricted artifact links and deterministic
rendering, together with the existing report contract suite:

```sh
uv run --no-project --with pytest --with pyyaml --with jsonschema python -m pytest tests/architecture/test_rolling_report_example.py tests/architecture/test_algorithm_run_dataset_contract.py -q -rA -p no:cacheprovider --basetemp="$TMPDIR/rolling-report-tests"
```

The command will use an unused temporary directory outside the repository.
Immutable data and revision binding, artifact content verification, publication
and acceptance will remain deferred to a separate integration. Fixture links will
remain illustrative references rather than shipped artifacts.

## Run the example

```sh
python examples/algorithm_runs/rolling_report_example.py > "$TMPDIR/rolling-report.html"
```

`render_report(algorithm, runs)` returns HTML without file access or side effects.
Repeated calls with equal arguments return equal text. The command writes one
rolling document containing historical and current runs together. It does not
generate separate reports for individual runs. In a future integration the stable
path will follow `reports/algorithms/{algorithm_id}/index.html`; Git will retain
earlier report versions.

## Independent fixture calculation

All quantities here are synthetic and dimensionless. The illustrative algorithm
doubles an input: for the historical input, `1 × 2 = 2`; for the current input,
`2 × 2 = 4`. Independently subtracting these outputs gives `4 − 2 = 2`.
The assumed absolute uncertainty bound is `1`, so the illustrative current
interval is `[4 − 1, 4 + 1] = [3, 5]`. This interval has no statistical confidence
interpretation. These hand calculations supply the example's numeric literals
and the test expectations; the renderer performs no arithmetic.

The literal run partition is `historical-synthetic` and `current-synthetic` as
`succeeded_validated_reproducible`, with `failed-synthetic` as
`reproducible_failure`. The failed run models invalid input, has no numerical
result, and carries a synthetic phase, code, signature and diagnostic reference.
Tests deliberately inject a value of `999` and marked analytical text into that
failed run. This arbitrary sentinel must never enter the analytical population;
it is not an expected result of the doubling calculation. A separate applicability
test uses `0` to check that a zero metric is still displayed.

## Layout and applicability

| Section | Example activation |
| --- | --- |
| Inputs | Always present; inventories input references for every displayed run. |
| Outputs | Always present; inventories primary output references for successful runs only. |
| Metrics | Successful runs supply eligible metric observations, with units in their labels. |
| Plots and comparisons | Successful runs supply an explicit comparison identifying its run set and derivation. |
| Uncertainty | Successful runs supply a method, assumptions and interval. |
| Diagnostics and health | A failed run exists or a successful run supplies warning diagnostics. |
| Insights | Successful runs supply prequalified synthetic analytical text. |
| Decision brief | Successful runs supply an illustrative reviewed decision or no-decision. |

Empty inventories retain their headings and an explicit empty message. Empty
optional sections disappear. Failed diagnostics have a separate section and
cannot supply primary outputs, metrics, comparisons, uncertainty, insights or
decision text, even when those fields are populated in an incoming example record.
The caller supplies optional evidence only when applicable: comparison relevance,
scientific validity and review eligibility are not evaluated by this renderer.
The fixture's validation and review descriptions are illustrative, not actual
acceptance or review records.

Every dynamic text field is HTML-escaped. Artifact attributes are escaped and
restricted to simple relative paths below `fixtures/`; absolute paths, active URL
schemes, traversal, encoding escapes and query strings are rejected. The listed
artifact references are illustrative fixture locators, not shipped files or
verified content-addressed objects. The renderer neither resolves nor opens them.
Structural tests parse headings, tables, text and link attributes without a browser.

## Deferred integration

Immutable data/revision integration is deferred. This layout has no dataset
access, native output-schema validation, content hashes, revision resolution,
publication ledger, acceptance gate or production publisher. In particular it
does not establish exact Hugging Face revision pins, source commits or stale-link
detection. An integrated report must bind every displayed run to verified immutable
data and an exact revision, preserve native output metadata and apply publication,
validation and review eligibility before rendering. This example makes no claim
that those broader requirements are complete.
