# Public-safe knowledge graph validation pattern

Use this reference when implementing or closing an llm-wiki public-safe knowledge graph issue.

## Durable artifact shape

A useful public-safe graph tranche should produce both machine-readable artifacts and a human report:

- `artifacts/retrieval/public-graph/nodes.jsonl`
- `artifacts/retrieval/public-graph/edges.jsonl`
- `artifacts/retrieval/public-graph/nodes.csv`
- `artifacts/retrieval/public-graph/edges.csv`
- `artifacts/retrieval/public-graph/summary.json`
- `docs/reports/<YYYY-MM-DD>-public-safe-knowledge-graph-report.md`

The schema should be versioned, e.g. `public-graph/v1`, and graph rows should be metadata/link-only. Paths must be repo-relative and the graph must avoid raw/private source paths.

## Public-safety invariants

Validate these explicitly before closeout:

- node paths and edge evidence paths are repo-relative, never absolute local paths
- `wikis/**/raw/**` content is not exposed as graph nodes, targets, or evidence text
- artifacts and report do not contain obvious secrets or private identifiers
- every node/edge carries the expected schema version
- relation values are allowlisted and stable
- duplicate edge tuples are counted and reported
- unresolved targets are counted and surfaced rather than silently discarded
- `summary.unresolved_targets` and `summary.unresolved_target_count` match the unresolved targets actually emitted in graph edges; do not count suppressed/unsafe/non-emitted targets in summary diagnostics
- safe unresolved markdown links and wikilinks are emitted as allowlisted graph edges (typically `cites -> unresolved:<slug>`), while unsafe/private unresolved targets are fully suppressed from both edges and summary
- external targets are decoded and scanned across the full URL, not just the path: scheme/netloc/path/params/query/fragment
- percent-encoded local/private path evidence in URL query strings or fragments is rejected, e.g. encoded `/home/...`, `/mnt/...`, dotfile, `..`, or private/raw path fragments
- nullish relationship values such as `None`, `none`, `null`, `~`, and empty strings are treated as absent, never emitted as aliases such as `external:None`
- bare wikilink/stem resolution is deterministic and ambiguity-safe: if multiple public pages share a stem, emit an unresolved target or skip; do not pick the first sorted match

Useful relation families:

- `implements`
- `validates`
- `cites`
- `supersedes`
- `related-domain`
- `source-family`
- `public-result`
- `blocked-by-clearance`

## Validation sequence

1. Inspect the live dirty state with untracked-file awareness. Do not rely on `git diff` alone; new graph implementations often exist entirely as untracked files until staged.
2. Write targeted regression tests before patching implementation when an adversarial review finds public-safety or schema-contract gaps.
3. Run targeted tests for graph generation/validation and confirm new regressions fail before the fix when practical.
4. Run the generator and validator explicitly on the live artifact/report paths.
5. Run repo-specific diff-only legal scan as the new-work gate. If full-repo legal scan fails on pre-existing committed corpus material, document it as baseline debt and do not claim full legal green.
6. Run full relevant tests if feasible.
7. Do an adversarial review of generator, validator, tests, artifacts, and report before commit; MAJOR findings block closeout even if local tests pass.
8. Commit with explicit pathspecs to avoid sweeping unrelated dirt.
9. Post a closeout evidence comment before closing the GitHub issue.

## Schema-contract checks

Validator and tests should enforce the documented schema, not just artifact parseability/parity:

- `node_id == path` for node rows unless the schema explicitly introduces a separate ID namespace
- node `kind` is an allowlisted enum matching the schema documentation
- `summary.json` includes all required keys, including unresolved target detail, high-degree threshold, and public-safety note
- count fields in `summary.json` match artifacts (`node_count`, `edge_count`, eligible page count, unresolved target count)
- JSONL and CSV artifacts are semantically consistent for the same rows
- report sections cite the same run date/schema version/artifact counts as `summary.json`

## Regression tests to add after adversarial findings

When a review finds graph safety/schema holes, add tests for the class of failure before patching:

- use `add_edge`-style helpers that return whether an edge was actually emitted, then update summary diagnostics only on `True`
- encoded unsafe external URL payload in query/fragment/params is rejected or skipped
- nullish `supersedes`/relationship metadata does not produce `external:None`
- ambiguous bare wikilinks do not silently resolve to an arbitrary same-stem page
- validator rejects `node_id != path`
- validator rejects invalid node `kind`
- validator rejects missing required summary keys or count mismatches
- validator rejects `summary.unresolved_targets` drift from emitted unresolved edge targets

## Pitfalls

- `git diff` can be empty when all work is untracked. Use `git status --short`, `git ls-files --others --exclude-standard`, or read files directly before concluding there is no implementation diff.
- A generated artifact directory can hide safety regressions even when code tests pass. Inspect `summary.json` and sample JSONL/CSV rows directly.
- Full legal scans may fail on existing committed wiki corpus content. Preserve the distinction between baseline scan debt and the diff-only gate for the current issue.
- Treat unexpected files in the dirty tree as contamination until proven in-scope. For example, an enforcement script copied from another repo/issue should be classified before being committed with an llm-wiki graph feature.
- Do not close the issue until the evidence comment has landed and `gh issue view` verifies state/comments.
