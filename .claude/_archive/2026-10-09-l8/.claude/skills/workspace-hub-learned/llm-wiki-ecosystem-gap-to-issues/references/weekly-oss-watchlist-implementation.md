# Weekly OSS engineering-tool watchlist implementation pattern

Use when implementing the weekly OSS/concept watchlist issue family for `llm-wiki` or a similar repo-backed engineering knowledge base.

## Durable artifact shape

A useful weekly OSS watchlist implementation should produce all of these, not just a report:

1. `data/oss_tool_watchlist.json` or equivalent structured manifest.
   - Include at least: tool slug/name, owner/repo, public upstream URL, public docs URL, check/source strategy, domain, wiki target, affected tier-1 paths, tier-1 public links where applicable, last checked/version/release marker, confidence/noise policy, and why it matters.
2. `data/oss_tool_issue_map.json` or equivalent dedupe/routing map.
   - Keep routing data-driven; avoid hardcoded issue IDs in scanner code.
3. Deterministic scanner/report generator.
   - Offline-first fixture/state mode is acceptable and often preferable for validation stability.
4. Deterministic validator.
   - Validate manifest shape, report sections, public URLs, safe repo-relative paths, tier-1 links, roadmap links, and forbidden public-safety patterns.
5. Dated human-readable report under `docs/reports/`.
6. Dated and latest machine-readable state under `artifacts/watchlist/`.
7. Tests for scanner behavior, artifact/report shape, validator behavior, and routing precedence.

## Routing precedence trap

Do not route only by `slug -> recommendation_action -> default`.

A real defect occurred when `data/oss_tool_issue_map.json` defined a `docs_changed` route, but scanner routing ignored `signal_type`. `docs_changed` is a signal type, not necessarily a recommendation action, so rows silently fell through to the default issue route.

Use this precedence unless a future design explicitly documents otherwise:

1. Tool slug-specific route.
2. Signal-type route, e.g. `docs_changed`.
3. Recommendation-action route, e.g. `update_existing_wiki_page` or `create_initial_seed_page`.
4. Default route.

Add a regression test where a row has `signal_type = docs_changed` and `recommendation_action = update_existing_wiki_page`, with distinct issue IDs for both routes. Assert that the `docs_changed` route wins over the recommendation-action fallback.

## Previous-state fixture shape

For delta tests, match the scanner's real previous-state contract. In the proven implementation, `_previous_for_tool()` read from a `rows` list, not a `tools` dictionary. A test fixture using the wrong shape produced `no_change` instead of `docs_changed`, hiding the intended routing exercise.

Preferred fixture pattern:

```json
{
  "rows": [
    {
      "slug": "example-tool",
      "observed_value": "v1.0.0",
      "observed_release_date": "2026-01-01",
      "observed_docs_marker": "old-doc-marker"
    }
  ]
}
```

## Public-safety validation

For public `llm-wiki` artifacts:

- Reports must stay metadata/summary/link-only.
- Do not vendor upstream source code or copy documentation text into the repo.
- Do not include private mount paths such as `/mnt/ace` or `/mnt/ace-data`.
- Do not include client/vendor/private identifiers, secrets, credentials, API keys, tokens, passwords, connection strings, private keys, SSNs, or bank-account data.
- If a repository-wide legal scan fails on pre-existing unrelated content, run and report the diff-only legal scan for the staged implementation; do not claim the repo-wide failure was fixed by the issue.

## Closeout evidence checklist

Before closing the issue, capture:

- Targeted watchlist tests.
- Full test suite if practical.
- Generator + validator result with explicit success output.
- Diff-only legal scan result.
- Static staged-diff scan result, with benign validator-regex matches called out if needed.
- Code-stage adversarial review after implementation.
- Re-review if the first adversarial review returns MAJOR/MINOR.
- Commit hash, pushed branch state, issue comment URL, and clean/synced `main...origin/main` evidence.

## Route-state validation after issue closeout

For weekly watchlist implementations that keep a durable issue-routing manifest, add a route-state validator as soon as routes reference live GitHub issues. It should catch both stale governance state and malformed manifest entries before a weekly scanner keeps posting to the wrong destination.

Minimum validator checks:

- Every active route issue reference resolves via `gh issue view` or an equivalent fixture-backed contract in tests.
- Active watchlist route entries must not point at closed issues unless the route is explicitly marked archived/deprecated.
- Malformed route entries fail closed; do not silently skip records with missing route IDs, invalid issue numbers, or unknown route keys.
- The closeout path for an implemented/closed issue must update the active route manifest in the same change that closes the issue, or document why the route remains active.

Regression tests should include:

1. A closed issue still present in the active route manifest → validator fails.
2. A malformed route entry that previously would have been skipped → validator fails.
3. A valid open issue route → validator passes.

## Common closeout gotcha

If `git push origin main` is rejected because remote advanced, do not retry blindly. Fetch, inspect divergence/reflog, rebase the local implementation, rerun at least targeted tests, then push. This preserves the implemented work while respecting concurrent repo writes.
