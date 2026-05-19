---
name: llm-wiki-cadence-governance
description: Weekly governance workflow for keeping an llm-wiki repository current, code-development-useful, and connected to actionable GitHub issue planning.
---

# LLM Wiki Cadence Governance

Use this skill when reviewing an llm-wiki repository, comparing it against current LLM/AI engineering concepts, or opening issues to keep the wiki useful for code development and repo architecture decisions.

## Trigger Conditions

- User asks to review, refresh, or maintain an `llm-wiki` repository.
- User asks for a weekly cadence to keep AI/LLM concepts current.
- User asks what GitHub issues should be opened from an llm-wiki architecture/content gap review.
- A session produces llm-wiki maintenance artifacts that need durable closeout or restart handoff.

## Core Principle

Treat llm-wiki as a development leverage system, not a passive knowledge base. Every review should connect external concept freshness, internal repo architecture gaps, and actionable GitHub issues that move engineering work forward.

## Weekly Cadence Workflow

1. **Repository architecture inventory**
   - Inspect current information architecture: domains, concept pages, source maps, graph/manifest generation, validation scripts, and docs reports.
   - Identify stale pages, orphaned nodes, weak cross-links, missing source citations, and concepts not tied to code-development use cases.

2. **External concept freshness scan**
   - Review current LLM/agent engineering topics relevant to the workspace: agents, tool use, RAG, context engineering, evals, model-routing, inference/serving, structured outputs, safety, data governance, and code-agent workflows.
   - Capture concepts as candidate deltas, not undigested research dumps.

3. **Code-development usefulness mapping**
   - For each candidate gap, ask: what repo decision, code pattern, evaluation, documentation contract, or automation pipeline would this improve?
   - Prioritize items that improve engineering velocity, correctness, agent routing, or reusable architecture guidance.

4. **Issue portfolio creation**
   - Open de-duplicated GitHub issues only after checking existing issues and plan state.
   - Prefer issue clusters by class: freshness pipeline, graph/index quality, source/citation governance, domain pages, code integration guides, eval/readiness scorecards.
   - Keep implementation gated by the workspace issue workflow: plan → adversarial review → user approval → TDD implementation.

5. **Validation and closeout**
   - Run the repo's available tests/validators for graph manifests, schemas, docs, and legal/public-safety gates before claiming readiness.
   - If closeout cannot finish, preserve restart state in a repo-tracked handoff with exact validation evidence, dirty files, issue status, and the next checkpoint.

## Issue Quality Checklist

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
- Do not lose partial closeout state. If the session ends before commit/push/issue close, write a handoff first.

## Support References

- `references/issue-closeout-handoff-pattern.md` — concise restart-handoff pattern from an llm-wiki public-graph issue closeout where validation passed but implementation files still needed final commit and issue closure.
