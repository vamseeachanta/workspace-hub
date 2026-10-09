# Public graph manifest validation hardening

Use this reference when llm-wiki work touches generated public-safe knowledge graph artifacts, especially manifests under `artifacts/retrieval/public-graph/` and reports under `docs/reports/`.

## Durable validation pattern

1. Treat public graph generation as a security/publication boundary, not a formatting task.
2. High-risk semantic relations must be fail-closed:
   - `implements`
   - `validates`
   - `public-result`
3. Only allow those relations from explicit curated link-map evidence lines. Do not infer them from arbitrary prose, arbitrary Markdown link pages, or filename heuristics.
4. Use a filename allowlist for curated link maps. Current known allowlist:
   - `code-results-links.md`
   - `cross-links.md`
   - `cross-links-tier1.md`
   - `public-data-software-links.md`
5. For each high-risk edge, validator should verify:
   - `evidence_type == "link_map_line"`
   - evidence source path is a public-safe repo-relative wiki path
   - evidence source filename is in the curated link-map allowlist
   - cited evidence line contains exactly one external URL for the target
   - cited evidence line maps to exactly one high-risk relation, not ambiguous multi-intent prose
6. Public graph source discovery should be narrow:
   - include `wikis/<domain>/wiki/**/*.md`
   - exclude agent instruction files such as `CLAUDE.md` and `AGENTS.md`
   - exclude any path containing `raw` or `private`
   - reject absolute local paths in artifacts and reports
7. Validator should not depend on a single dated report filename. Prefer latest matching `*-public-safe-knowledge-graph-report.md`, or require an explicit `--report-path` in CI.
8. Add report-summary consistency checks so Markdown report counts cannot drift from `summary.json`.
9. Make the validator independently fail-closed; do not assume artifacts were produced by the generator:
   - every node `path` / `node_id` must satisfy the same public-source predicate as generator discovery
   - every edge `source_node` must reference an accepted node
   - every repo-relative `target_node` / core target must either be a declared accepted node or fail validation
   - every `evidence_path` must exist and stay inside the accepted public wiki/link-map surface; reject `raw`, `private`, agent files, absolute paths, and off-surface files even when the basename looks allowlisted
10. Recompute deterministic `edge_id` values in the validator. The generator contract is SHA1 over `source_node|target_ref|relation|evidence_type|evidence_locator`, truncated to 16 hex characters; duplicate checks are not enough because forged-but-unique IDs can otherwise pass.
11. Prove artifact freshness against the live corpus, not only internal consistency:
   - preferred: regenerate into a temporary output/report path and byte-compare deterministic JSONL/CSV/summary/report outputs
   - acceptable alternative: persist and validate a public corpus digest plus artifact digests
   - stale but internally consistent artifacts must fail after a source markdown mutation
12. Apply the same public markdown target rules to normal Markdown links as to wikilinks. Unless the schema explicitly supports non-markdown artifact edges, `[label](foo.pdf)` / image / binary links should not become graph edges.
13. Resolve curated link-map scope explicitly. If root-level `wikis/cross-links-tier1.md` is supported, both generator and validator must allow exactly that shape. If not, remove it from the allowlist/schema/docs so basename allowlisting cannot imply broader path scope.
14. Validation closeout sequence should include:
   - targeted unit/regression tests for generator/validator
   - full generator run
   - validator run against generated artifacts
   - legal/public-safety scan for unsafe paths/secrets/private/raw references
   - artifact parity checks for JSONL/CSV/report/schema
   - artifact freshness/deterministic-regeneration check
   - adversarial re-review before commit/closeout
15. If the validation loop is interrupted before closeout, do not imply the issue is done. Preserve a handback with:
   - exact commands that passed and their key output counts
   - tracked/untracked file state observed
   - what was not yet verified: full tests, legal/public-safety scan, artifact parity/freshness, re-review, commit/push, issue comment/labels/close
   - the first resume action: revalidate live working tree before trusting the handback
   This prevents stale post-compression summaries from being mistaken for closure evidence.

## Regression tests to add when this class changes

- Non-allowlisted `*links*.md` page must not become a curated high-risk source.
- Extensionless internal links resolve to `.md` nodes only when public-safe.
- High-risk edge with mismatched evidence line is rejected.
- High-risk evidence line with multiple external URLs is rejected.
- High-risk evidence line with multiple high-risk relation signals is rejected.
- CSV field order/content parity with JSONL is enforced.
- Report count drift from summary is rejected.
- `raw/`, `private/`, `CLAUDE.md`, and `AGENTS.md` never appear in generated public graph nodes/edges.
- Forged off-scope nodes are rejected even if `node_id == path` and internal counts are consistent.
- Forged/off-surface `evidence_path` values are rejected even if the file exists or the basename is allowlisted.
- Wrong-but-unique `edge_id` values are rejected by recomputing the deterministic ID.
- Stale artifacts are rejected after mutating a source markdown file without regeneration.
- Normal Markdown links to PDFs/images/binaries are skipped or rejected according to the public graph contract.
- Root-level curated link-map behavior is covered explicitly: either accepted only for `wikis/cross-links-tier1.md` or rejected/documented as out of scope.
