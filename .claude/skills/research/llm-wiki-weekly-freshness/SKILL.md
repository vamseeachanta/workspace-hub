---
name: llm-wiki-weekly-freshness
description: Weekly cadence workflow for keeping an llm-wiki repository current, public-safe, and maximally useful for code development. Use when asked to review llm-wiki architecture/content, scan new LLM concepts, produce an issue roadmap, or maintain recurring freshness.
---

# LLM Wiki Weekly Freshness

## Trigger
Use this skill when the task involves any of:
- Reviewing or improving an `llm-wiki` repository.
- Comparing repository knowledge coverage against current LLM/software-development concepts.
- Creating GitHub issues to keep the wiki useful for engineering/code development.
- Designing or running a weekly freshness cadence for LLM knowledge ingestion.

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

## Weekly workflow

### 1. Repo architecture review
Inspect the repo structure and identify:
- Domain taxonomy and whether it matches current engineering/code workflows.
- Markdown source layout and generated artifacts.
- Existing ingestion/index/validation scripts.
- Reports or manifests used by agents for retrieval.
- Public-safety boundaries for generated graphs, indexes, and reports.

Evidence to gather:
- `git status --short`
- `git remote -v`
- key docs/README/schema files
- current issue labels and open freshness/indexing issues
- test and validation entry points

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

### 3. Gap-to-issue conversion
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

### 4. Validation before closeout
For any repo change or generated artifact, run the relevant verification loop:
- targeted tests for changed scripts/pages
- artifact generation + validator
- full test suite when code changed
- legal/public-safety scan if artifacts or public content changed
- adversarial review for non-trivial planning or implementation

Do not close issues when adversarial review has unresolved MAJOR findings.

## Public-safe graph/index specific checks
When maintaining generated wiki graph/index artifacts:
- Tie artifacts to committed source corpus with a digest.
- Validate JSONL/CSV content parity, not just row counts.
- Fail closed on header-only CSV when JSONL contains rows.
- Reject dotfile path parts.
- Reject symlinks or require resolved targets to stay inside the approved public wiki corpus shape.
- Keep paths repo-relative and deterministic.
- Validate report sections and summary/report drift.
- Commit a durable schema/contract artifact for the manifest version and validate that all generated JSONL/CSV/report outputs use the same schema version string.
- Keep heuristic bridge/opportunity lists explicitly diagnostic; add negative tests proving they are not emitted as authoritative edges without explicit markdown/frontmatter/link-map evidence.
- Prefer a stable canonical weekly report path when the report is part of a recurring cadence; date-stamped reports are acceptable only when the repo intentionally archives snapshots and validates stale-report cleanup.

## Weekly report format
Produce a compact report with:
1. Current state.
2. Evidence inspected.
3. New concept signals.
4. Repo architecture gaps.
5. Recommended issue backlog ranked by leverage.
6. Automation/freshness cadence proposal.
7. Blockers/risks.
8. Exact next action.

## References
- `references/public-safe-graph-validation.md` — session-derived checks for public-safe graph manifests and adversarial-review blockers.
