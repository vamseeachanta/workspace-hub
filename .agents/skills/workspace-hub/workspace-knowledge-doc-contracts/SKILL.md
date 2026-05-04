---
name: workspace-knowledge-doc-contracts
version: 1.0.0
category: workspace-hub
description: Class-level workspace knowledge, LLM-wiki, repo mission contracts, stale doc references, semantic taxonomy, and knowledge-source reconnaissance.
tags: [knowledge, documentation, llm-wiki, contracts]
---

# Workspace Knowledge Doc Contracts

## When to Use
Use when building/repairing LLM-wiki knowledge, aligning repo mission contracts, auditing stale documentation references, extracting learnings into issues, or turning domain gaps into issue roadmaps.

## Class-Level Workflow
1. Inventory knowledge sources and distinguish canonical docs from generated/session artifacts.
2. Repair metadata/frontmatter before indexing or downstream issue creation.
3. Keep repo mission/contract documents aligned with live repository purpose.
4. Convert real gaps into deduplicated issues only after source-grounded evidence exists.
5. Maintain semantic taxonomy terms consistently across reports and docs.

## Metadata-only LLM-wiki execution for large/sensitive corpora

Use this sub-pattern when an approved plan promotes a large or sensitive corpus (external-drive archives, standards libraries, training decks, client/project files) into LLM-wiki pages without copying raw data:

1. **Gate first**: confirm explicit plan approval (`status:plan-approved` or a local approval marker) before writing wiki pages.
2. **RED test first**: add focused tests that initially fail for expected page existence and boundary fields: `extraction_policy`, `raw_copy_allowed: false`, `ocr_allowed: false` where applicable, source-of-record absolute paths, and index/log updates.
3. **Create pointer/shell pages, not extraction dumps**:
   - standards/spec libraries use `extraction_policy: metadata-only`; no clauses, copied standards text, or detailed licensed titles.
   - training/client corpora use `extraction_policy: metadata-first`; curated summaries only; no full deck text, speaker notes, OCR output, screenshots, figures, or raw bytes.
   - standards resolver stubs use public metadata only (`code_id`, `publisher`, `revision` or explicit unverified/deferred marker, `revision_source`, `verified_on`, `public_url`).
4. **Update discoverability surfaces**: update `wiki/index.md`, `wiki/log.md`, and parent source-catalog cross-links so new pages are not orphaned.
5. **Verify broadly**: run targeted pytest, `scripts/knowledge/tests/test_llm_wiki.py`, `llm_wiki.py lint/status` for affected domains, and a raw-data guard such as `git show --name-only --format='' HEAD | grep -E 'knowledge/wikis/.*/raw/|\.(pdf|pptx|ppt|xlsx|xls|docx|doc|png|jpg|jpeg|dwf|db)$' || true`.
6. **Force-add intentionally ignored wiki files**: workspace-hub may ignore `knowledge/wikis/*`; use `git add -f` only for intended wiki pages/tests/reports and check targeted `git status` to avoid unrelated provider/report churn.
7. **Treat fetch/rev-list as push truth**: if `git push` reports a transient remote lock/rejected ref but the remote already points at the new commit, verify with `git fetch origin main` and `git rev-list --left-right --count HEAD...origin/main`; `0 0` is the sync ground truth.
8. **Close issues with evidence**: include commit hash, test/lint results, raw-data guard result, and preserved boundaries in GitHub comments.

## Consolidated Session Learnings

The `references/` directory contains archived narrow skills absorbed during the 2026-04-29 umbrella consolidation pass. Use the subsections below as the class-level index, then open the named reference when a case-specific recipe is needed.
## Absorbed Narrow Skills (2026-04-29)

### `docs-stale-reference-guardrails`

- Former skill demoted to `references/docs-stale-reference-guardrails.md`.
- Preserved insight: Prevent deleted workflow/path references from creeping back into live docs by combining strict scans, legacy allowlists, and shared regex helpers.

### `extract-learnings-to-issues`

- Former skill demoted to `references/extract-learnings-to-issues.md`.
- Preserved insight: Extract unstructured user reflections and learnings, distill core themes, route insights to existing GitHub issues as contextual comments rather than creating duplicates.

### `knowledge-source-recon`

- Former skill demoted to `references/knowledge-source-recon.md`.
- Preserved insight: Reconnaissance pattern to inventory all knowledge sources across the workspace-hub ecosystem's existing intelligence infrastructure. Maps raw sources for LLM Wiki ingestion planning. Leverages pre-built registries and indexes rather than re-scanning directories.

### `llm-wiki-ecosystem-gap-to-issues`

- Former skill demoted to `references/llm-wiki-ecosystem-gap-to-issues.md`.
- Preserved insight: Review the workspace-hub LLM-wiki/document-intelligence ecosystem, identify high-leverage gaps, and create grounded GitHub feature issues without duplicating existing work.

### `llm-wiki-pattern`

- Former skill demoted to `references/llm-wiki-pattern.md`.
- Preserved insight: Build and maintain persistent, compounding knowledge bases using the LLM Wiki pattern (Karpathy). Unlike RAG (retrieve chunks at query time), the wiki is a persistent artifact that gets compiled and maintained by the LLM.

### `llm-wiki-roadmap-integration`

- Former skill demoted to `references/llm-wiki-roadmap-integration.md`.
- Preserved insight: Integrate repo-ecosystem work into an existing llm-wiki / knowledge-roadmap issue without creating duplicate GitHub issues.

### `parallel-llm-wiki-gap-to-issues`

- Former skill demoted to `references/parallel-llm-wiki-gap-to-issues.md`.
- Preserved insight: Use parallel subagents to mine remaining LLM-wiki/document-intelligence gaps, de-duplicate against existing GitHub issues, then create only the strongest bounded follow-on issues.

### `repair-legacy-llm-wiki-frontmatter-dates`

- Former skill demoted to `references/repair-legacy-llm-wiki-frontmatter-dates.md`.
- Preserved insight: Diagnose and repair legacy llm-wiki source pages that have ingested timestamps but are missing required added/last_updated frontmatter dates.

### `repo-mission-portfolio-audit`

- Former skill demoted to `references/repo-mission-portfolio-audit.md`.
- Preserved insight: Audit the workspace-hub repo portfolio to extract each repo's mission, identify documentation gaps, and prioritize a plan/approval sequence with explicit LLM-wiki weighting for future issue triage.

### `semantic-taxonomy-reporting-consistency`

- Former skill demoted to `references/semantic-taxonomy-reporting-consistency.md`.
- Preserved insight: Keep semantic-diff taxonomy summaries consistent with evidence tables when adding richer categories to legacy comparison/reporting pipelines.

### `workspace-hub-mission-contract-first-packet`

- Former skill demoted to `references/workspace-hub-mission-contract-first-packet.md`.
- Preserved insight: Plan the first repo-mission canonicalization packet for the workspace ecosystem by reusing the existing control-plane issue, locking Wave-1 scope, and making review criteria deterministic.

### `tier1-indexing-scorecard-and-freshness-audit`

- Former skill demoted to `references/tier1-indexing-scorecard-and-freshness-audit.md`.
- Preserved insight: Audit tier-1 repos for code-placement/retrieval readiness, write a scorecard report, create follow-up GitHub issues, and add a daily freshness cron while avoiding legacy product-doc reference patterns.

### `exclude-wiki-Codex-md-from-harness-line-limit-hook`

- Former skill demoted to `references/exclude-wiki-Codex-md-from-harness-line-limit-hook.md`.
- Preserved insight: Fix false-positive pre-commit failures where workspace-hub's AGENTS.md line-limit hook blocks edits to auto-generated wiki schema files under knowledge/wikis/.

### `memory-bridge-commit-fallbacks`

- Former skill demoted to `references/memory-bridge-commit-fallbacks.md`.
- Preserved insight: Fallback procedures when the Hermes ↔ Codex memory bridge writes .Codex/memory outputs but the internal git commit/push path fails because of dirty, stale, or broken submodule state.
