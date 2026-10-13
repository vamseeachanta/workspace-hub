# LLM-wiki RAG/query evaluation implementation reference

Use this when implementing or reviewing the weekly-cadence roadmap tranche that makes `llm-wiki` directly useful for code development through repeatable retrieval benchmarks.

## Durable objective

Treat the wiki as a coding substrate, not a passive document archive. The implementation should prove that agents can retrieve the right context for real development tasks and detect regressions week to week.

## Recommended durable artifacts

Create stable, repo-tracked artifacts rather than one-off reports. The current proven `llm-wiki` implementation shape is:

- `tests/fixtures/rag-benchmark/questions.json` — canonical question set with expected paths/domains/terms.
- `scripts/llm_wiki_rag_benchmark.py` — deterministic benchmark runner.
- `scripts/validate_rag_benchmark.py` — standalone artifact/scorecard validator.
- `artifacts/retrieval/rag-benchmark/latest-scorecard.json` — machine-readable latest scorecard for weekly comparisons.
- `docs/rag-benchmark.md` — user-facing operating docs.
- `docs/reports/<date>-llm-wiki-rag-benchmark.md` or HTML equivalent — human-facing run report with failures, trends, and next actions.
- `tests/test_llm_wiki_rag_benchmark.py` and `tests/test_rag_benchmark_artifacts.py` — TDD coverage for runner behavior and artifact shape.

Older or future layouts such as `knowledge/evals/llm-wiki/...` are acceptable only if the plan explicitly migrates the artifact contract and updates tests/docs together. Do not split fixtures, scorecards, and validators across multiple unlinked locations.

Prefer fixtures grounded in actual code-development tasks: API lookup, module ownership, standards provenance, domain-specific engineering method lookup, and repo navigation. Do not use generic trivia questions.

## Fixture shape

Each fixture should include:

- `id`: stable slug.
- `query`: natural-language agent query.
- `task_type`: e.g. `code_lookup`, `domain_context`, `standards_trace`, `repo_navigation`, `implementation_prior_art`.
- `expected_domains`: wiki domains that should be hit.
- `expected_paths`: exact wiki pages or manifest entries expected in top results when known.
- `required_terms`: terms that must appear in retrieved snippets or answer context.
- `anti_hits`: pages/domains that indicate noisy retrieval if they dominate.
- `rationale`: why this query matters for code work.

Keep fixtures small enough for weekly execution but representative enough to catch drift. Start with 15–30 queries; grow only when failures reveal uncovered task classes.

## Scoring pattern

Use a transparent scorecard before adding model-judged scoring:

1. `hit_at_k`: expected path/domain appears in top K results.
2. `required_term_coverage`: expected terms appear in retrieved context.
3. `noise_penalty`: anti-hit dominance or unrelated domain dominance.
4. `freshness_signal`: result references current manifests/pages rather than stale generated indexes.
5. `developer_actionability`: retrieved context includes enough path/provenance information for the next code action.

If adding LLM judgment later, keep deterministic metrics as the gating layer and use model judgment only for secondary diagnosis.

## Weekly cadence integration

- Run after weekly freshness/update jobs, not before.
- Compare against the previous successful run and flag regressions separately from first-time failures.
- Emit issue-ready failure clusters: missing page, stale manifest, poor alias/title, weak cross-link, or retrieval-noise problem.
- Keep the weekly report public-safe: no client identifiers, secrets, private contact details, or unpublished confidential source text.

## Review traps

- Do not benchmark only page existence; the target is task-relevant retrieval quality for coding agents.
- Do not make the eval dependent on live web search if the purpose is to test the repo/wiki substrate.
- Do not hide failures in aggregate scores; list the failing fixture IDs and expected paths.
- Do not create broad follow-up issues from a single failed query; group failures by root cause first.
- Do not accept a runner that only prints prose. It must write machine-readable results so weekly automation can compare deltas.
