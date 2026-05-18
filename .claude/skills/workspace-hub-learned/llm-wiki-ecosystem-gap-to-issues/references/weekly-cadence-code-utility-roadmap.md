# Weekly-cadence / code-utility roadmap pattern

Use this reference when a user asks how to keep an LLM wiki continuously up to date and more useful for engineering/code development.

## Durable recommendation shape

After architecture and repo-state review, prioritize issues that turn a wiki from a static content dump into an operational engineering substrate:

1. Weekly freshness control loop
   - Scheduled crawl/update workflow
   - freshness manifest / stale-domain report
   - explicit source-watch configuration
   - generated weekly change summary
2. Agent-facing entrypoints and domain manifests
   - `llms.txt` or equivalent root entrypoint
   - per-domain manifest files that point agents to canonical pages, source queues, provenance rules, and query examples
   - machine-readable navigation before prose-only navigation
3. Public-safe knowledge graph manifests
   - derived graph of topics, repos, docs, standards, source families, and backlinks
   - public-safe metadata only; no confidential client/source payload
   - deterministic build so code tools can consume it
4. RAG/query benchmark suite
   - representative engineering questions
   - expected source coverage / provenance assertions
   - regression checks that fail when important answers become stale or ungrounded
5. Weekly OSS / concept watchlist
   - recurring scan for new LLM, agent, RAG, MCP, code-search, eval, and documentation concepts
   - curated candidate queue, not blind ingestion
   - promotion criteria into durable wiki pages
6. CLI/MCP query surface
   - local CLI and/or MCP server over wiki indexes/manifests/graph
   - optimized for engineering agents that need fast code-development context
   - should usually follow stable manifests and graph schema, not precede them

## Sequencing heuristic

Recommended order:

1. Freshness loop first: it keeps the substrate alive.
2. Entrypoints/manifests second: they make the repo agent-readable.
3. Graph third: it connects concepts and code/domain artifacts.
4. Eval benchmark fourth: it measures whether the wiki is useful.
5. OSS watchlist fifth: it feeds weekly updates without polluting the wiki.
6. CLI/MCP last: expose only after the data contracts stabilize.

## Issue/planning workflow

For each proposed issue:

- create a narrow GitHub issue with live repo evidence and non-duplicate checks
- generate a plan artifact under `docs/plans/YYYY-MM-DD-issue-NN-<slug>.md`
- verify each plan includes: summary, evidence, scope boundaries, implementation phases, file map, tests/validation, public-safety constraints, risks, acceptance criteria, dependencies, and approval gate
- comment on the issue linking the plan artifact
- keep implementation blocked until adversarial plan review and explicit user approval

## Anti-patterns

- Do not solve weekly currency by simply ingesting more documents; create controls, manifests, and tests first.
- Do not expose a CLI/MCP surface before contracts are stable enough for agents to rely on.
- Do not mix private project intelligence into a public wiki graph; keep public-safe metadata boundaries explicit.
- Do not create one giant roadmap issue if six narrower issues can be planned, reviewed, approved, and executed independently.
