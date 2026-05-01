# Archived Skill: `workspace-hub-mission-contract-first-packet`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/workspace-hub-mission-contract-first-packet`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/workspace-hub-mission-contract-first-packet`
Consolidation date: 2026-04-29

---

---
name: workspace-hub-mission-contract-first-packet
description: Plan the first repo-mission canonicalization packet for the workspace ecosystem by reusing the existing control-plane issue, locking Wave-1 scope, and making review criteria deterministic.
version: 1.0.1
category: workspace-hub-learned
tags: [workspace-hub, mission, portfolio, planning, adversarial-review, llm-wiki]
---

# Workspace-Hub Mission Contract — First Packet Pattern

Use this when the user wants to revise repo missions across the workspace ecosystem and approve them one by one.

## When to use
- User asks for repo mission analysis across multiple repos
- User wants a repo-by-repo approval sequence
- You need a first approval packet before touching downstream repo missions
- The work touches llm-wiki architecture but must not prematurely decide embedded vs spinout boundaries

## Core pattern
1. Start with `workspace-hub`, not downstream repos.
2. Before creating a new GitHub issue, search for an existing open parent issue covering the control-plane / ecosystem contract.
3. If `#1525` (`Define canonical repo control-plane contract across workspace ecosystem`) is still open, reuse it instead of creating a duplicate mission issue.
4. Draft the local plan under `docs/plans/` and add the row to `docs/plans/README.md`.
5. Run adversarial review before surfacing for approval.
6. Expect the first draft to fail if verification is subjective; tighten it into deterministic checks.

## Recommended Wave-1 scope
Lock the first packet to:
- `workspace-hub` = control plane
- `digitalmodel` = engineering computation core
- `assetutilities` = shared utility substrate
- `aceengineer-website` = GTM / externalization layer

Explicitly defer `worldenergydata` to Wave 2 unless the plan intentionally expands scope.

## Critical review hardening learned in practice
Cross-provider reviewers objected to these weak patterns:
- subjective tests like “docs use consistent terminology”
- llm-wiki neutrality stated only as intent
- mixed in-scope / deferred downstream repo language
- unverified supporting report references

Fix them before trying to get approval:

### 1. Make verification deterministic
Add a concrete validation artifact, e.g.:
- `scripts/validation/check_workspace_hub_mission_contract.py`

That validator should check required / forbidden phrases across the reconciled mission docs.

### 2. Use a literal llm-wiki neutrality guardrail
Require the exact phrase:
- `repo-boundary architecture remains under evaluation per #2398`

Also forbid wording that declares llm-wiki permanently embedded or spun out.

### 3. Verify every cited local input artifact
If the plan cites a supporting report like:
- `docs/reports/2026-04-21-repo-mission-revision-sequence.md`

include it in the embedded evidence block as EXISTS.

### 4. Keep artifact map unambiguous
If one report contains multiple sections (mission contract, downstream role map, glossary, llm-wiki guardrails), list it as one artifact with named sections, not multiple artifacts pointing to the same file.

## First-packet files usually in scope
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- new canonical report such as `docs/reports/workspace-hub-mission-contract.md`
- validator such as `scripts/validation/check_workspace_hub_mission_contract.py`

## Recommended acceptance criteria shape
Include all of these explicitly:
- canonical mission contract file exists
- deterministic validation script exists
- reconciled docs pass the validator
- `workspace-hub` control-plane role is explicit
- `digitalmodel`, `assetutilities`, and `aceengineer-website` roles are explicit
- `worldenergydata` is explicitly deferred if not in scope
- literal `#2398` neutrality phrase is present
- non-goals are explicit
- `docs/plans/README.md` row exists
- review artifacts exist

## Operational note
If the first review wave returns mixed results like Claude/Codex MAJOR and Gemini APPROVE, do not surface the plan as approval-ready. Patch the plan immediately, update the `## Adversarial Review Summary`, and rerun cross-review.
