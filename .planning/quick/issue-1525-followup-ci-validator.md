# Proposed follow-up issue draft for #1525

Title: chore(ci): enforce workspace-hub mission-contract validator in CI

## Summary
Add CI enforcement for `scripts/validation/check_workspace_hub_mission_contract.py` so the workspace-hub mission contract and reconciled control-plane docs do not drift after the initial mission-contract packet lands.

## Why
Issue `#1525` creates a canonical mission contract plus a deterministic validator, but manual execution alone is not enough to preserve the contract. Without CI enforcement, later edits to `README.md`, `docs/README.md`, `docs/BUSINESS_BRAIN.md`, or `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` can silently reintroduce contradictory role language.

## Scope
- wire `scripts/validation/check_workspace_hub_mission_contract.py` into CI
- fail PRs when required phrases, forbidden phrases, non-goal bullets, or semantic role-claim checks drift
- keep `docs/standards/CONTROL_PLANE_CONTRACT.md` generic
- do not redesign the mission contract itself in this issue

## Acceptance criteria
- CI runs the validator on pull requests that touch the covered files
- failing validator output is visible in CI logs
- docs-only PRs that violate the contract are blocked
- validator remains easy to run locally
