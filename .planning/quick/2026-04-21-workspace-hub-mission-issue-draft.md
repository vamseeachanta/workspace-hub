# Proposed GitHub issue draft

Title: feat(portfolio): canonicalize workspace-hub repo mission and ecosystem role contract

## Summary

Canonicalize the mission and ecosystem role of `workspace-hub` so the repo has one explicit control-plane contract across its main onboarding and navigation documents.

## Why

Current mission intent is spread across multiple files:
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- `AGENTS.md`

This creates drift risk for:
- repo-by-repo mission revisions
- future issue triage
- llm-wiki role definition
- downstream repo boundary decisions

## Goal

Define `workspace-hub` clearly as the ecosystem control plane and align the top-level docs to that role without prematurely freezing the open llm-wiki repo-boundary decision tracked in `#2398`.

## Desired outputs

- one canonical workspace-hub mission statement
- explicit non-goals
- explicit role definitions for key downstream repos:
  - `digitalmodel`
  - `assetutilities`
  - `aceengineer-website`
  - `worldenergydata`
- explicit statement that llm-wiki is the durable cross-repo knowledge layer, while embedded-vs-spinout architecture remains under active evaluation
- updated top-level docs with no contradictory mission language

## Suggested files in scope
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- `AGENTS.md` only if needed for consistency
- `CLAUDE.md` only if needed for consistency

## Acceptance criteria
- a single consistent mission contract is visible across the main workspace-hub docs
- workspace-hub’s control-plane role is explicit
- non-goals are explicit
- downstream repo role labels are explicit and consistent
- wording supports future issue ranking with 20% llm-wiki weighting
- wording does not prematurely decide the #2398 llm-wiki spinout question

## Notes

Use adversarial plan review before approval. This issue should be the first approval packet before revising downstream repo missions.
