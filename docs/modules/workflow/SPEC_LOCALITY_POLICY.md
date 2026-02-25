# Spec Locality Policy

Version: 1.0.0
Last Updated: 2026-02-17

## Policy

All new planning and specification artifacts are centralized in `workspace-hub`.

## Canonical Locations

1. WRK-linked execution specs:
- `specs/wrk/WRK-<id>/`

2. Repository/domain specs:
- `specs/repos/<repo>/`

3. Shared templates:
- `specs/templates/`

## Work Queue Integration

- `WRK-*.md` files must exist only under `.claude/work-queue/`.
- Route C work should set `spec_ref` to `specs/wrk/WRK-<id>/<slug>.md`.

## Migration Guidance

1. Existing repo-local `specs/` content should be migrated to `specs/repos/<repo>/`.
2. Leave a `specs/README.md` pointer in child repos during transition.
3. Do not add new spec files to child repo `specs/` directories.

## Enforcement

Use these scripts:

- `scripts/operations/compliance/audit_contract_drift.sh`
- `scripts/operations/compliance/validate_agent_contract.sh`
- `scripts/operations/compliance/audit_wrk_location.sh`
- `scripts/operations/compliance/audit_skill_symlink_policy.sh`
- `scripts/operations/compliance/validate_work_queue_schema.sh`
- `scripts/operations/compliance/check_governance.sh`
