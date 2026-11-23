# Spec Locality Policy

Version: 1.0.0
Last Updated: 2026-02-17

## Policy

All new planning and specification artifacts are centralized in `workspace-hub`.

## Canonical Locations

1. Issue plans (canonical active planning artifacts):
- `docs/plans/`

2. Plan approval markers:
- `.planning/plan-approved/`

3. Shared planning / evidence templates and archived planning support artifacts:
- `.planning/templates/`
- `.planning/archive/`

## Work Queue Integration

Canonical tracking is GitHub issues plus issue-plan artifacts under `docs/plans/`.

- New work intake starts as a GitHub issue; do not create new local `WRK-*.md` queue files or `specs/wrk/` entries.
- Active plan documents belong in `docs/plans/` and must follow `docs/plans/_template-issue-plan.md`.
- User approval is recorded by the GitHub issue labels `status:plan-review` / `status:plan-approved` and the marker `.planning/plan-approved/<issue>.md`.
- Existing legacy local queue content is compatibility data, not the canonical intake or planning path.

## Migration Guidance

1. Existing legacy repo-local planning content (for example `specs/`, `specs/wrk/`, or WRK-linked execution notes) should be migrated or referenced from `docs/plans/` when still active, or moved to `.planning/archive/` when retained only for history.
2. If a child repo still carries legacy planning directories, leave a pointer to `workspace-hub/docs/plans/` as the canonical active planning location.
3. Do not add new active plan/spec files to child-repo `.planning/`, `specs/`, or `specs/wrk/` directories.

## Enforcement

Use these scripts:

- `scripts/operations/compliance/audit_contract_drift.sh`
- `scripts/operations/compliance/validate_agent_contract.sh`
- `scripts/operations/compliance/audit_wrk_location.sh`
- `scripts/operations/compliance/audit_skill_symlink_policy.sh`
- `scripts/operations/compliance/validate_work_queue_schema.sh`
- `scripts/operations/compliance/check_governance.sh`
