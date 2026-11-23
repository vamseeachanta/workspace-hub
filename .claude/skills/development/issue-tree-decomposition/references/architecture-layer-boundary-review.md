# Architecture layer boundary review issue tree

Use this reference when decomposing a broad repo-ecosystem architecture review into GitHub child issues. The goal is to create review/planning tracks that clarify boundaries before implementation, not to authorize architecture changes.

## Trigger

User asks to create or decompose a feature/issue reviewing boundaries across layers such as:
- data sources, raw/local/private data, public knowledge repos
- execution inputs, tools, code execution, compute/runtime placement
- report outputs, client-facing HTML/PDF/chatbot/publication surfaces

## Pre-create checks

1. Search open issues for duplicate phrasing across all three layer nouns.
2. Inspect available labels and reuse existing category/domain labels.
3. Read grounding docs before writing the first-pass guesses. In workspace-hub-like repos, start with:
   - data residence/storage policy
   - business/knowledge promotion or evidence-boundary docs
   - content/reporting/publication pipeline docs
4. Keep legal/IP/data-residence constraints explicit: private/local/client/licensed raw data must not be promoted into public knowledge or client-facing artifacts without provenance, license, sanitization, and legal sanity checks.

## First-pass child issue split

### Data layer child

Likely scope:
- raw external source data and API/download captures
- private/local source data and client-sensitive material
- curated fixtures/reference data that may be safe to track
- raw-like knowledge staging for llm-wiki or equivalent knowledge systems
- public knowledge outputs after sanitization/promotion
- provenance, license, source, retrieval, and lineage metadata

Acceptance criteria should require a boundary table defining: storage location, commit policy, public/private status, promotion gate, and regeneration path.

### Execution layer child

Likely scope:
- input contracts and work packets: issues, plans, YAML/JSON specs, fixtures, source registries
- transform tools: ingest scripts, parsers, wiki builders, report generators, validation harnesses
- agent/provider execution paths and review prompts
- compute/runtime placement: local machines, licensed machines, remote workers, background jobs
- validation gates: tests, legal scans, adversarial reviews, artifact verification
- execution evidence bundles: logs, manifests, checksums, run metadata, command evidence

Acceptance criteria should require a contract mapping inputs → tool/runtime → outputs → evidence.

### Report layer child

Likely scope:
- raw outputs and intermediate artifacts
- internal review reports and evidence bundles
- client-facing HTML reports
- limited PDF exports where needed
- chatbot/query surfaces and retrieval indexes
- public knowledge/website outputs
- claim/evidence rules for public and client-facing surfaces

Acceptance criteria should require a report taxonomy separating raw outputs, internal evidence, review artifacts, and client/public deliverables.

## Parent issue closeout

After creating child issues:
1. Verify each child with `gh issue view`.
2. Comment on the parent issue with Markdown links to each child issue and a one-line scope summary.
3. State that the children are planning/review tracks, not implementation approval.
4. Link the grounding docs used for the first-pass guesses.

## Pitfalls

- Do not collapse data, execution, and report concerns into one child issue; that recreates the umbrella.
- Do not treat public `llm-wiki` as raw data storage. It is a promoted/sanitized knowledge surface.
- Do not let report-layer public claims exceed repository evidence, validation outputs, or explicit engineering caveats.
- Do not commit raw downloads, ZIP archives, private data, credentials, or generated analysis reports just because they were mentioned in issue bodies.
