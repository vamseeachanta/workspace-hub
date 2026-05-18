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
9. Validation closeout sequence should include:
   - targeted unit/regression tests for generator/validator
   - full generator run
   - validator run against generated artifacts
   - legal/public-safety scan for unsafe paths/secrets/private/raw references
   - artifact parity checks for JSONL/CSV/report/schema
   - adversarial re-review before commit/closeout

## Regression tests to add when this class changes

- Non-allowlisted `*links*.md` page must not become a curated high-risk source.
- Extensionless internal links resolve to `.md` nodes only when public-safe.
- High-risk edge with mismatched evidence line is rejected.
- High-risk evidence line with multiple external URLs is rejected.
- High-risk evidence line with multiple high-risk relation signals is rejected.
- CSV field order/content parity with JSONL is enforced.
- Report count drift from summary is rejected.
- `raw/`, `private/`, `CLAUDE.md`, and `AGENTS.md` never appear in generated public graph nodes/edges.
