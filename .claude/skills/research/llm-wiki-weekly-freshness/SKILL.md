---
name: llm-wiki-weekly-freshness
description: Class-level governance workflow for keeping llm-wiki-style markdown knowledge bases current, public-safe, graph/index-valid, and useful for code development. Use when reviewing llm-wiki architecture/content, scanning new LLM concepts, maintaining public knowledge graphs, producing an issue roadmap, or running recurring freshness cadence.
---

# LLM Wiki Weekly Freshness

## Trigger
Use this skill when the task involves any of:
- Reviewing, improving, or maintaining an `llm-wiki` or similar markdown knowledge-base repository.
- Comparing repository knowledge coverage against current LLM/software-development concepts.
- Creating GitHub issues to keep the wiki useful for engineering/code development.
- Designing or running a weekly freshness cadence for LLM knowledge ingestion.
- Changing public-safe graph/index generators, validators, schema docs, CSV/JSONL mirrors, reports, or source-scope boundaries.
- Closing out llm-wiki maintenance work where generated artifacts, validation evidence, issue state, and commits must align.

## Operating contract
1. **Treat this as planning/governance unless the user has approved implementation.**
   - For GitHub issue work, follow the local repo's planning gates.
   - Do not jump from gap discovery directly into implementation unless the relevant issue is already plan-approved.
2. **Keep the wiki public-safe by default.**
   - No private/raw archives, credentials, local absolute paths, vendor/client material, dotfiles, symlink escapes, connection strings, or machine-specific manifests.
   - Prefer committed markdown and deterministic generated metadata over local runtime state.
3. **Optimize for code-development leverage.**
   - Rank gaps by how much they improve implementation decisions, architecture review, testing strategy, agent prompts, retrieval, and issue planning.
   - Avoid generic news collection unless it maps to code-development utility.
4. **Keep generator, validator, tests, schema docs, and reports in lockstep.**
   - A graph/index change is incomplete until all five surfaces agree.
   - Validate parity between JSONL, CSV, summaries, reports, and documented schema, not just row counts.

## Weekly workflow

### 1. Repo architecture review
Inspect the repo structure and identify:
- Domain taxonomy and whether it matches current engineering/code workflows.
- Markdown source layout and generated artifacts.
- Existing ingestion/index/validation scripts.
- Reports or manifests used by agents for retrieval.
- Public-safety boundaries for generated graphs, indexes, reports, and issue artifacts.

Evidence to gather:
- `git status --short`
- `git remote -v`
- key docs/README/schema files
- current issue labels and open freshness/indexing issues
- test and validation entry points
- generated artifact/report paths and schema version strings

### 2. Current LLM concept scan
Review current concepts from high-signal sources, then convert only durable items into wiki work:
- model release notes and provider docs
- evaluation/benchmarking practices
- agentic coding workflows
- retrieval/context engineering
- structured outputs/tool calling
- inference/runtime/serving changes
- security, prompt-injection, data-boundary patterns

For each concept, record:
- concept name
- why it matters for code development
- target wiki domain/page
- source URL/citation
- freshness date
- proposed validation or example artifact

### 3. Code-development usefulness mapping
For each candidate gap, ask what repo decision, code pattern, evaluation, documentation contract, automation pipeline, or agent workflow it would improve. Prioritize items that improve engineering velocity, correctness, agent routing, reusable architecture guidance, retrieval quality, or public-safety guarantees.

### 4. Gap-to-issue conversion
Open issues only when the gap is actionable. Each issue should include:
- Problem statement tied to code-development leverage.
- Resource intel: repo files, external sources, related issues.
- Plan shape: expected files/artifacts, tests, validation.
- Public-safety constraints.
- Acceptance criteria.
- Labels for planning status and domain.

Prefer issue classes:
- **Taxonomy/schema gaps** — missing domains, stale page schema, weak metadata.
- **Freshness automation** — weekly scanner, source manifest, stale-page report.
- **Retrieval utility** — graph manifests, cross-links, query surfaces, agent context exports.
- **Concept coverage** — current LLM concepts mapped to durable wiki pages.
- **Validation/legal gates** — public-safe checks, link validation, artifact consistency.
- **Public graph/index hardening** — schema/validator/generator/report parity, source-scope boundaries, leakage guards, stale artifact detection.

### 5. Validation before closeout
For any repo change or generated artifact, run the relevant verification loop:
- targeted tests for changed scripts/pages
- artifact generation + validator
- full test suite when code changed
- legal/public-safety scan if artifacts or public content changed
- adversarial review for non-trivial planning or implementation

Do not close issues when adversarial review has unresolved MAJOR findings.

If closeout cannot finish, preserve restart state in a repo-tracked handoff with exact validation evidence, dirty files, issue status, and the next checkpoint. Do not lose partial closeout state after reports were generated but commits/pushes/issue closures are unfinished.

## Public-safe graph/index governance
Use this subsection when a repository emits public-safe graph manifests such as `nodes.jsonl`, `edges.jsonl`, CSV mirrors, summary metadata, or Markdown reports derived from an llm-wiki-style corpus.

### Provenance and schema fields
Recommended node fields:
- `schema_version`
- `node_id`
- `path`
- `title`
- `domain`
- `kind`
- `tags`
- `public_safe`
- `source_scope`
- `source_family`
- `source_corpus_digest`
- `backlinks`

Recommended edge fields:
- `schema_version`
- `edge_id`
- `source_node`
- `relation`
- `target_node`
- `evidence_path`
- `evidence`
- `source_scope`
- `source_family`
- `source_corpus_digest`

Use stable, repo-relative paths. `source_scope` should be explicit and bounded, for example `public-wiki`; do not imply that private raw data, client data, or unreviewed readable-raw corpora are part of the public graph.

### Relation allowlist discipline
Treat relation names as public schema. Remove provisional workflow/control relations from public v1 artifacts unless they are intentionally documented and tested. If reviewers reject relation names, update validator, schema docs, generator tests, fixture artifacts, and report text together.

### Edge-field leakage guard
Do not treat public-safe filtering as complete just because excluded files were not emitted as nodes. Edge fields can still leak excluded surfaces through `target_ref`, `evidence_path`, `evidence_locator`, CSV mirrors, summaries, or reports.

Fail closed when schema says a target class is excluded:
- If unresolved targets are documented as dropped, `target_layer == "unresolved"` must not be an accepted validator target layer and must not appear in generated artifacts.
- Agent instruction surfaces such as `CLAUDE.md` and `AGENTS.md` must be rejected anywhere in public artifacts, not only excluded from source discovery.
- High-risk code/result relations need direct negative coverage for forged curated evidence and malformed curated lines with zero or multiple external URLs.

### Backlinks
If graph consumers need reverse navigation, compute backlinks from emitted edges rather than hand-maintaining them in source pages:
1. Initialize backlinks for all emitted nodes.
2. For each edge whose target is a known node, add the source node unless it is self-referential.
3. Sort backlink arrays before writing artifacts for deterministic diffs.
4. Validate CSV mirrors against JSONL after serialization, not independently.

### Default freshness validation
Weekly graph validation should detect stale artifacts by default. Do not make current-corpus validation opt-in unless there is a deliberate test-only escape hatch.

Recommended behavior:
1. Resolve the repository root explicitly from CLI input or infer it from the artifact/report path and cwd.
2. Rebuild an in-memory graph from the current public corpus.
3. Compare summary counts, corpus digest, schema version, and key output parity against the checked-in artifacts.
4. Fail closed if artifacts are stale, missing, or generated from a different public-safe source set.

### TDD and artifact update workflow
1. Write or update failing tests first for the intended contract drift.
   - Prefer contract-targeted RED tests over incidental corpus-shape assertions.
   - For graph hardening, test unresolved target rejection/sanitization, private/source leakage across every output surface, CSV-vs-JSONL parity, and schema/generator alignment directly.
   - Avoid bare exact node/edge counts unless the fixture is deliberately minimal and every created page is part of the asserted contract.
2. Patch the generator.
3. Patch the validator immediately after the generator; do not leave CSV headers or allowed relation lists stale.
4. Patch schema docs and report text in the same change.
5. Regenerate artifacts if the repository tracks them.
6. Normalize artifact/report paths before validation: pick one final report date/path, regenerate once, and stage only artifacts validated against that exact report.
7. Run targeted tests, full tests, artifact validator, legal/safety scan for public/private leakage, and adversarial review before closeout.

### Closeout hygiene for tracked artifacts
Public graph work often produces generated files plus dated reports. Before committing:
- Treat `AM` status on generated artifacts as a warning: reset/re-stage final versions so staged content matches the validated working tree.
- Do not validate one dated report while staging another dated report; the validator command, summary `run_date`, report filename, and committed report must align.
- Keep transient review scratch directories such as `.planning/quick/` out of commits unless the repository explicitly tracks review artifacts.
- Re-run the artifact validator after final staging normalization, not only after the first generation.

## Weekly report format
Produce a compact report with:
1. Current state.
2. Evidence inspected.
3. New concept signals.
4. Repo architecture gaps.
5. Public graph/index health, if applicable.
6. Recommended issue backlog ranked by leverage.
7. Automation/freshness cadence proposal.
8. Blockers/risks.
9. Exact next action.

## Issue quality checklist
A good llm-wiki maintenance issue includes:
- Clear problem statement tied to code-development leverage.
- Current evidence path: repo files, generated reports, graph metrics, issue links, or source pages.
- Scope boundaries: what is in/out for this issue.
- Acceptance criteria with validation commands or report artifacts.
- Public/private data classification where source material may cross governance boundaries.
- Dependencies on existing architecture contracts, graph schema, citation model, or source-ingest workflows.

## Pitfalls
- Do not create a flat backlog of generic “add topic X” issues. Tie each issue to a reusable architecture or development outcome.
- Do not treat external AI trends as authoritative without source provenance and update dates.
- Do not bypass issue planning gates just because the task is documentation-heavy.
- Do not close an llm-wiki issue after only generating reports; verify that committed files, pushed state, issue labels/comments, and tests all match the claimed closeout.
- Do not let public-safe filtering stop at source discovery; validate every emitted field and every mirror/report surface.
- Do not let generated artifact path drift invalidate closeout evidence.

## References
- `references/public-safe-graph-validation.md` — session-derived checks for public-safe graph manifests and adversarial-review blockers.
- `references/issue-closeout-handoff-pattern.md` — restart-handoff pattern from an llm-wiki public-graph issue closeout where validation passed but implementation files still needed final commit and issue closure.
- `references/session-2026-05-unresolved-agent-edge-leakage.md` — concrete edge-field leakage patch and validation pattern.
- `references/session-2026-05-public-graph-review-majors.md` — review-major remediation pattern for public graph artifacts.
- `references/session-2026-05-public-graph-closeout-hygiene.md` — artifact/report date-drift and staging-normalization closeout pattern.
- `references/session-2026-05-graph-hardening-red-test-targets.md` — RED-test targeting pattern for direct contract violations.
- `references/absorbed-llm-wiki-cadence-governance.md` — archived original narrow cadence-governance skill body for traceability.
- `references/absorbed-public-knowledge-graph-governance.md` — archived original public graph governance skill body for traceability.
