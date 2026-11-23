# Archived Skill: `parallel-llm-wiki-gap-to-issues`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/parallel-llm-wiki-gap-to-issues`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/parallel-llm-wiki-gap-to-issues`
Consolidation date: 2026-04-29

---

---
name: parallel-llm-wiki-gap-to-issues
description: Use parallel subagents to mine remaining LLM-wiki/document-intelligence gaps, de-duplicate against existing GitHub issues, then create only the strongest bounded follow-on issues.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [llm-wiki, github-issues, parallel-research, de-duplication, knowledge-management, workspace-hub]
---

# Parallel LLM-Wiki Gap-to-Issues

Use when the user wants more LLM-wiki / document-intelligence improvement issues and the repo already has a large existing issue graph, reports, and prior planning artifacts.

## Why this skill exists

A naive single-pass issue brainstorm creates duplicates fast in workspace-hub because many adjacent items already exist as:
- umbrella issues
- batch-pack designs
- architecture/policy docs
- partially overlapping implementation issues
- recently created follow-ons in the same session

The reliable pattern is:
1. split the search space across parallel subagents,
2. force each subagent to stay read-only,
3. have each one produce issue-ready candidates with duplicate assessment,
4. synthesize centrally,
5. create only the strongest non-duplicate items,
6. repeat on the remaining surface until marginal candidates become weak.

## Best-use trigger conditions

- User asks to "continue with recommendations using parallel agents"
- You already created some issues and need the next wave without overlap
- Repo has strong prior artifacts (queue docs, reports, architecture docs, issue history)
- Problem is not implementation, but identifying the next best bounded GitHub issues

## Core execution pattern

### Phase 1 — Load context and recent created issues

Before delegating, capture the already-created issue numbers from the current session and identify the main clusters already covered.

For LLM-wiki work in workspace-hub, common clusters already covered in one session can include:
- provenance / reverse lookup / doc_key
- batch-pack execution waves
- navigation / portals / index quality
- transient-to-durable promotion
- governance / conformance / retention

Always pass the newly created issue numbers into subagent context so they do not rediscover the same work.

### Phase 2 — Partition the search space

Use up to 3 parallel subagents, each with a sharply bounded surface. The pattern that worked well was:

1. navigation / discoverability
   - wiki indexes
   - accessibility registry
   - landing pages
   - portals / explorers / uplinks

2. source-ingest / promotion pipeline
   - batch packs
   - registries / ledgers / summaries
   - external-source priority queue
   - remaining designed-but-unfiled promotion waves

3. tacit knowledge / governance / transient artifacts
   - handoffs
   - review artifacts
   - WRK completions
   - retention / conformance / audit trail gaps

Important: tell subagents explicitly to do read-only analysis and NOT create issues.

### Phase 3 — Force duplicate-aware outputs

In each subagent prompt, require:
- 2-4 candidates max
- issue-ready wording
- explicit duplicate check against named open issues
- a recommendation whether to file or not file
- scope boundaries to avoid overlap

This is critical. Without it, subagents overproduce vague ideas that collide with open work.

## Required evidence sources

Tell subagents to prioritize existing repo intelligence over rescanning blindly.

For workspace-hub LLM-wiki work, the highest-yield sources were:
- docs/reports/2026-04-16-llm-wiki-resource-intelligence-unified-review.md
- docs/reports/llm-wiki-external-source-priority-queue.md
- docs/reports/llm-wiki-staged-batch-packs.md
- docs/reports/engineering-wiki-skill-ingest-readiness-2039-2042.md
- docs/reports/engineering-wiki-skill-ingest-priority-pack.yaml
- docs/document-intelligence/intelligence-accessibility-map.md
- docs/document-intelligence/durable-vs-transient-knowledge-boundary.md
- docs/document-intelligence/standards-codes-provenance-reuse-contract.md
- data/document-index/intelligence-accessibility-registry.yaml
- data/document-index/resource-intelligence-maturity.yaml
- data/design-codes/code-registry.yaml
- knowledge-base/wrk-completions.jsonl

Use live `gh issue list/view` to verify duplicates rather than trusting local docs alone.

## Synthesis rules in the main agent

After subagents return:
1. group candidates by theme
2. discard anything clearly covered by an existing open issue
3. prefer issues that are:
   - bounded
   - grounded in live repo evidence
   - distinct from umbrella issues
   - implementation-shaped, not vague strategy restatements
4. if two candidates overlap, choose the narrower one with clearer boundaries
5. if a residual candidate is too heterogeneous after exclusions, do NOT file it

A key learning: sometimes the correct output is "do not file another issue" for a source family after overlap removal.

## Creation workflow

For each surviving candidate:
1. draft the body in `/tmp/*.md`
2. include grounding bullets from live repo state or docs
3. explicitly list exclusions to prevent duplicate scope
4. create with `gh issue create --body-file`
5. verify immediately with `gh issue view --json number,title,url,labels,body`

## Reusable issue families this pattern surfaced well

This approach was especially effective for finding the next wave of:
- wiki reverse lookup / provenance issues
- batch-pack execution issues
- source-title aliasing / index chunking issues
- registry-backed explorer/navigation issues
- closed-issue promotion ledgers
- transient-promotion candidate queues
- WRK normalization / structured seed work
- conformance checks like promotion audit-trail checker and invented-layer detector

## Practical heuristics

- If a candidate depends on a policy doc but no enforcement exists, it is often a good issue.
- If a candidate is mentioned as "future work" in a normative doc and not already filed, it is high-signal.
- If an issue family shrinks to only a few mixed leftovers after exclusions, do not file it as a standalone wave.
- Separate curated navigation improvements from canonical index mechanics:
  - portals/faceted entry points are different from chunking the authoritative index.
- Separate schema/policy from enforcement:
  - field definition issue != checker issue
  - queue extraction issue != retention/pruner issue

## Anti-patterns to avoid

- Do not ask subagents to search the whole repo with no theme; results get noisy fast.
- Do not create issues directly from subagent outputs without a central duplicate pass.
- Do not file broad residual issues for tiny heterogeneous leftovers.
- Do not rely only on local docs for duplicate checks; use live GitHub issue state.
- Do not merge multiple adjacent ideas into one issue unless the scope boundary is extremely clear.

## Minimal template for delegate_task context

Include:
- repo path
- user intent (continue recommendations with parallel agents)
- recently created issues
- allowed focus area for that subagent
- required duplicate-check set
- instruction: read-only only, do not create issues
- expected output: 2-4 issue-ready candidates with rationale and duplicate assessment

## Success criterion

You know this pattern worked when each wave produces only a small number of strong, clearly non-duplicate issues, and later waves naturally converge toward fewer worthwhile candidates rather than endless brainstorm sprawl.
