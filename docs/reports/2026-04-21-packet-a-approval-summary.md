# Packet A Approval Summary — workspace-hub mission contract

Date: 2026-04-21
Packet: `docs/plans/2026-04-21-workspace-hub-mission-contract-packet-a.md`
Purpose: first repo-mission approval packet for the portfolio sequence

## What Packet A does

Packet A defines and aligns the canonical workspace-hub mission contract without bundling validator/governance mechanics into the same approval.

In scope:
- `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- generic cross-link in `docs/standards/CONTROL_PLANE_CONTRACT.md`

## Core decisions in Packet A

1. `workspace-hub` is the ecosystem control plane
2. `GSD` is the workflow control plane used within `workspace-hub`
3. Tier-1 role map for this packet:
   - `workspace-hub` = ecosystem control plane
   - `digitalmodel` = engineering computation core
   - `assetutilities` = shared utility substrate
   - `aceengineer-website` = GTM and externalization layer
4. `worldenergydata` role definition is explicitly deferred to the Wave-2 repo mission packet
5. `llm-wiki` is a durable cross-repo knowledge layer
6. The repo boundary for llm-wiki remains unresolved and must be described neutrally:
   - `repo-boundary architecture remains under evaluation per #2398`

## Required non-goals

Packet A requires the canonical contract to state:
- workspace-hub does not own engineering computations; digitalmodel owns that layer
- workspace-hub does not serve as the shared utility library; assetutilities owns that layer
- workspace-hub does not own the GTM/public website surface; aceengineer-website owns that layer
- workspace-hub does not silently decide the llm-wiki repo boundary before #2398 is resolved

## Why Packet A is the right approval object

- It isolates the business/portfolio meaning from validator/governance mechanics.
- It matches the repeated review finding that the mission-contract idea is stable while tooling concerns were causing churn.
- It keeps the first repo approval packet small enough to evaluate directly.
- It creates the canonical spine needed before revising downstream repos.

## What Packet A does NOT do

Moved to Packet B:
- validator script implementation
- parser semantics and fixtures
- AGENTS blob-pin enforcement
- CI integration and enforcement wiring
- governance-heavy review bookkeeping

## Approval decision being requested

Approve Packet A as the first bounded repo-mission revision packet for the portfolio.

If approved, the next execution step is:
1. turn Packet A into the active canonical plan for workspace-hub mission revision
2. review whether to map it onto existing issue `#1525` or create a narrower GitHub issue for Packet A only
3. after Packet A approval, keep Packet B as the follow-on tooling/enforcement packet

## Recommended follow-up after approval

A. immediate implementation target
- workspace-hub mission contract and top-level doc reconciliation

B. deferred follow-up packet
- validator and governance enforcement (`Packet B`)
