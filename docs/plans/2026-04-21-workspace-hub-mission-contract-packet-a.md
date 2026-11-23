# Packet A Plan — workspace-hub canonical mission contract

> Status: draft
> Date: 2026-04-21
> Source context: split extracted from issue `#1525`
> Purpose: approval-ready mission-contract packet with document reconciliation only

---

## Goal

Create the canonical workspace-hub mission contract and align the top-level workspace-hub documents to it, without bundling validator implementation or CI/governance enforcement work into the same packet.

## Why this packet exists

Repeated adversarial review on the monolithic `#1525` packet showed that the mission-contract content is substantively stable, while the remaining MAJOR findings were concentrated in validator semantics, evidence bookkeeping, and governance enforcement mechanics.

This packet isolates the durable document contract from those tooling concerns.

---

## In scope

Normative contract and reconciled docs only:
- `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- generic cross-link touch in `docs/standards/CONTROL_PLANE_CONTRACT.md`

Core content to define:
- `workspace-hub` as ecosystem control plane
- `GSD` as workflow control plane used within workspace-hub
- tier-1 role map for:
  - `workspace-hub`
  - `digitalmodel`
  - `assetutilities`
  - `aceengineer-website`
- explicit non-goals
- glossary
- llm-wiki neutrality phrase tied to `#2398`
- explicit defer note for `worldenergydata` to Wave 2

---

## Out of scope

These move to Packet B:
- `scripts/validation/check_workspace_hub_mission_contract.py`
- `tests/validation/test_workspace_hub_mission_contract.py`
- parser/normalization semantics
- regex catalogs for enforcement
- AGENTS blob-pin enforcement
- CI wiring and CI follow-up execution
- review-wave bookkeeping beyond normal plan-review evidence

---

## Resource intelligence summary

Grounding sources:
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- `docs/standards/CONTROL_PLANE_CONTRACT.md`
- issue `#2398`
- issue `#2390`
- `docs/reports/2026-04-21-repo-mission-revision-sequence.md`
- `docs/reports/2026-04-21-issue-1525-review-decision.md`

Key current-state findings:
- workspace-hub mission is currently fragmented across README, docs index, business brain, repository overview, and the control-plane standard.
- the role map for the tier-1 repos is conceptually stable across existing docs, but wording is inconsistent.
- llm-wiki must be described as a durable cross-repo knowledge layer without pre-deciding the unresolved embedded-vs-spinout question in `#2398`.
- `worldenergydata` should be explicitly deferred rather than partially defined in this packet.

---

## Deliverable

A canonical mission/role contract at `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` plus aligned top-level workspace-hub docs that consistently describe the ecosystem control-plane model.

---

## Files to change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` | normative mission contract |
| Modify | `README.md` | align root overview |
| Modify | `docs/README.md` | align docs index overview |
| Modify | `docs/BUSINESS_BRAIN.md` | align ecosystem-role wording |
| Modify | `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` | align repo-relationship wording |
| Modify | `docs/standards/CONTROL_PLANE_CONTRACT.md` | add generic cross-link only |

---

## Canonical content requirements

Required statements in `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`:
- `workspace-hub is the ecosystem control plane`
- `GSD is the workflow control plane used within workspace-hub`
- `digitalmodel is the engineering computation core`
- `assetutilities is the shared utility substrate`
- `aceengineer-website is the GTM and externalization layer`
- `worldenergydata role definition is deferred to the Wave-2 repo mission packet`
- `llm-wiki is a durable cross-repo knowledge layer`
- `repo-boundary architecture remains under evaluation per #2398`

Required `## Non-goals` bullets:
- workspace-hub does not own engineering computations; digitalmodel owns that layer
- workspace-hub does not serve as the shared utility library; assetutilities owns that layer
- workspace-hub does not own the GTM/public website surface; aceengineer-website owns that layer
- workspace-hub does not silently decide the llm-wiki repo boundary before #2398 is resolved

Required `## Glossary` terms:
- ecosystem control plane
- workflow control plane
- engineering computation core
- shared utility substrate
- GTM and externalization layer

---

## Acceptance criteria

- `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` exists and contains the required role statements
- it includes a real `## Non-goals` section
- it includes a real `## Glossary` section
- `README.md`, `docs/README.md`, `docs/BUSINESS_BRAIN.md`, and `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` are reconciled to the same role model
- `docs/BUSINESS_BRAIN.md` distinguishes ecosystem control plane vs workflow control plane
- `docs/standards/CONTROL_PLANE_CONTRACT.md` gains only a generic relationship/cross-link and does not become workspace-hub-specific
- no document prematurely resolves `#2398`
- `worldenergydata` is explicitly deferred, not silently omitted

---

## Suggested review standard for Packet A

This packet should be reviewed primarily for:
1. correctness of the role model
2. clarity of non-goals
3. absence of premature llm-wiki architectural commitment
4. consistency across the top-level docs

It should not be blocked on implementation-level validator semantics.

---

## Next packet dependency

After Packet A is approved, Packet B should implement the validator and enforcement mechanics against the approved canonical contract.