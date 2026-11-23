---
name: public-knowledge-graph-governance
description: Maintain public-safe knowledge graph artifacts for llm-wiki and similar markdown knowledge bases. Use when changing graph generators, validators, schema docs, weekly freshness checks, or public/private source-scope boundaries.
---

# Public Knowledge Graph Governance

Use this skill when a repository emits public-safe graph manifests such as `nodes.jsonl`, `edges.jsonl`, CSV mirrors, summary metadata, or Markdown reports derived from an llm-wiki-style corpus.

## Core Contract

Keep generator, validator, tests, schema docs, and report text in lockstep. A graph change is not complete until all five surfaces agree:

1. Generator output fields and allowed relation behavior.
2. Validator required fields, allowed relations, CSV parity, and freshness checks.
3. Tests for both accepted artifacts and rejection cases.
4. Schema documentation for each JSONL/CSV/report field.
5. Generated artifacts/reports validated against the current corpus.

## Public-safe Provenance Fields

For public graph artifacts, each node and edge should carry bounded provenance that proves source scope without exposing private/raw corpora.

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

## Relation Allowlist Discipline

Treat relation names as part of the public schema. Remove provisional workflow/control relations from v1 public artifacts unless they are intentionally documented and tested.

Common pitfall: leaving implementation-stage relation names such as `blocked-by-clearance` in a public v1 allowlist after reviewers reject them. Fix the validator, schema doc, generator tests, and any fixture artifacts together.

## Edge-Field Leakage Guard

Do not treat public-safe filtering as complete just because excluded files were not emitted as nodes. Edge fields can still leak excluded surfaces through `target_ref`, `evidence_path`, `evidence_locator`, CSV mirrors, summaries, or reports.

Fail closed when schema says a target class is excluded:

- If unresolved targets are documented as dropped, `target_layer == "unresolved"` must not be an accepted validator target layer and must not appear in generated artifacts.
- Agent instruction surfaces such as `CLAUDE.md` and `AGENTS.md` must be rejected anywhere in public artifacts, not only excluded from source discovery.
- High-risk code/result relations need direct negative coverage for forged curated evidence and malformed curated lines with zero or multiple external URLs.

See `references/session-2026-05-unresolved-agent-edge-leakage.md` for the concrete patch and validation pattern.

## Backlinks

If graph consumers need reverse navigation, compute backlinks from emitted edges rather than hand-maintaining them in source pages.

Rules:

1. Initialize backlinks for all emitted nodes.
2. For each edge whose target is a known node, add the source node unless it is self-referential.
3. Sort backlink arrays before writing artifacts for deterministic diffs.
4. Validate CSV mirrors against JSONL after serialization, not independently.

## Default Freshness Validation

Weekly graph validation should detect stale artifacts by default. Do not make current-corpus validation opt-in unless there is a deliberate test-only escape hatch.

Recommended behavior:

1. Resolve the repository root explicitly from CLI input or infer it from the artifact/report path and cwd.
2. Rebuild an in-memory graph from the current public corpus.
3. Compare summary counts, corpus digest, schema version, and key output parity against the checked-in artifacts.
4. Fail closed if artifacts are stale, missing, or generated from a different public-safe source set.

## Update Workflow

1. Write or update failing tests first for the intended contract drift.
   - Prefer contract-targeted RED tests over incidental corpus-shape assertions. For graph hardening, test unresolved target rejection/sanitization, private/source leakage across every output surface, CSV-vs-JSONL parity, and schema/generator alignment directly.
   - Avoid bare exact node/edge counts unless the fixture is deliberately minimal and every created page is part of the asserted contract.
2. Patch the generator.
3. Patch the validator immediately after the generator; do not leave CSV headers or allowed relation lists stale.
4. Patch schema docs and report text in the same change.
5. Regenerate artifacts if the repository tracks them.
6. Normalize artifact/report paths before validation: pick one final report date/path, regenerate once, and stage only artifacts validated against that exact report.
7. Run targeted tests, full tests, artifact validator, legal/safety scan for public/private leakage, and adversarial review before closeout.

## Closeout Hygiene for Tracked Artifacts

Public graph work often produces generated files plus dated reports. Before committing:

- Treat `AM` status on generated artifacts as a warning: reset/re-stage final versions so staged content matches the validated working tree.
- Do not validate one dated report while staging another dated report; the validator command, summary `run_date`, report filename, and committed report must align.
- Keep transient review scratch directories such as `.planning/quick/` out of commits unless the repository explicitly tracks review artifacts.
- Re-run the artifact validator after final staging normalization, not only after the first generation.

## Reference

- `references/session-2026-05-public-graph-review-majors.md` captures the review-major remediation pattern that motivated this skill.
- `references/session-2026-05-public-graph-closeout-hygiene.md` captures the artifact/report date-drift and staging-normalization closeout pattern.
- `references/session-2026-05-graph-hardening-red-test-targets.md` captures the RED-test targeting pattern: test contract violations directly instead of incidental graph counts.
