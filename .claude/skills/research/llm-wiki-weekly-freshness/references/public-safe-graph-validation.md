# Public-safe graph validation learnings

Use this reference when maintaining generated knowledge/link graph artifacts for an llm-wiki or similar public markdown knowledge base.

## Failure modes caught by adversarial review

### Header-only CSV bypass
A validator that parses CSV rows and then checks parity only under `if rows:` can miss header-only CSV files. If JSONL has rows and CSV parses to an empty list, validation must fail closed.

Required regression tests:
- `nodes.csv` contains only headers while `nodes.jsonl` has node records.
- `edges.csv` contains only headers while `edges.jsonl` has edge records.

Required validator behavior:
- Distinguish parse success from nonexistence/header failure.
- Compare row counts and projected content whenever CSV parsing succeeds, including zero rows.
- Report clear failures such as `nodes.csv row count mismatch with nodes.jsonl` or `nodes.csv content mismatch with JSONL artifact`.

### Unsafe source inclusion through dotfiles and symlinks
Filtering only for repo containment is insufficient for a public graph. A path under `wikis/<domain>/wiki/...` can still be unsafe if it is a dotfile or an in-repo symlink pointing outside the approved wiki corpus.

Required regression tests:
- `wikis/<domain>/wiki/.private.md` is not emitted as a node.
- `wikis/<domain>/wiki/safe-name.md` symlinked to an in-repo non-wiki/private file is not read/emitted.

Required generator behavior:
- Reject any source path with path parts beginning with `.`.
- Reject symlinks entirely, or require the resolved target to remain inside the approved public wiki corpus shape, not merely inside the repo root.
- Keep generated node/source paths repo-relative and deterministic.

### Report drift truncation
If reports show only the first N summary entries, validation should check the truncation/count line as well as the listed values. Otherwise a stale report with the same first N entries but wrong total count can pass.

### Missing schema/contract artifact
Adversarial implementation review may block closeout when generated manifests use an implicit schema version but no committed contract explains the fields, version string, artifact set, and compatibility rules.

Required fix pattern:
- Add a durable schema/contract artifact, for example `docs/schemas/public-graph-v1.md` or a JSON Schema file.
- Validate that `nodes.jsonl`, `edges.jsonl`, CSV metadata/header expectations, `summary.json`, and the report all use the same schema version string.
- Add tests for schema-version consistency and fail closed on version drift such as `public-graph/v1` vs `public-graph-v1`.

### Heuristic diagnostics promoted to graph truth
Bridge opportunities and cross-domain suggestions are useful weekly-cadence diagnostics, but they must not become authoritative graph edges unless backed by explicit source evidence.

Required fix pattern:
- Label opportunity lists as diagnostics/non-edge suggestions in `summary.json` and reports.
- Record generation rule, count, and confidence/heuristic wording.
- Add a negative test proving bridge opportunities are not emitted as `related`, `related-domain`, or equivalent edge records without explicit markdown/frontmatter/link-map evidence.

### CSV/JSONL content equivalence
Large CSV churn with small JSONL changes is a review smell. The validator should prove that both formats represent the same graph, not merely that both files exist.

Required fix pattern:
- Compare node IDs and edge IDs across CSV and JSONL exactly.
- Compare stable projected fields when available.
- Decide and document whether embedded newlines in CSV fields are allowed; reject them unless intentionally supported.

### Recurring report path choice
For weekly freshness cadence, prefer a stable canonical report path such as `docs/reports/public-safe-knowledge-graph-report.md` when downstream agents consume the report. Date-stamped snapshots are acceptable only if the repo intentionally archives history and has cleanup/staleness validation.

## Closeout rule
Do not close a public-knowledge artifact issue when adversarial review has unresolved MAJOR findings, even if targeted tests, full tests, and legal scan pass. Fix the blocker, add regression coverage, regenerate artifacts, rerun validation, and re-review with compact file/stdin-safe prompts.
