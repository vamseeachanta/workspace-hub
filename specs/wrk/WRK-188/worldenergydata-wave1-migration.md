---
title: "WRK-188 Worldenergydata Wave-1 Migration Plan"
description: "Dry-run manifest and controlled apply checklist for worldenergydata spec centralization"
version: "1.0"
module: governance
status: "draft"
progress: 35
created: "2026-02-17"
updated: "2026-02-17"
priority: "high"
tags: [spec-migration, worldenergydata, governance]
links:
  wrk: ".claude/work-queue/pending/WRK-188.md"
  parent: "specs/wrk/WRK-185/ecosystem-centralization-review.md"
---

# WRK-188 Worldenergydata Wave-1 Migration

## Scope
- In scope: `worldenergydata/**/specs/**`
- Out of scope: all other repositories

## Migration Script Contract

`migrate_specs_to_workspace.sh` behavior expected for apply mode:
1. Copy files from repo-local `specs/` trees into `specs/repos/<repo>/<original-spec-path>/`.
2. Replace original local `specs/` directory with pointer `README.md`.
3. Leave no non-README files under migrated local `specs/` trees.

## Prerequisites

```bash
mkdir -p reports/compliance
test -x scripts/operations/compliance/migrate_specs_to_workspace.sh
test -x scripts/review/cross-review.sh
test -z "$(git -C worldenergydata status --porcelain)"
mkdir -p specs/repos/worldenergydata
test -z "$(find specs/repos/worldenergydata -type f 2>/dev/null)"
```

## Dry-Run Commands
```bash
scripts/operations/compliance/migrate_specs_to_workspace.sh --repos worldenergydata | tee reports/compliance/wrk-188-worldenergydata-dryrun.log
find worldenergydata -type f -path '*/specs/*' -print0 | sort -z | xargs -0 sha256sum > reports/compliance/wrk-188-worldenergydata-source-checksums.txt
```

## Apply Commands (Do Not Run Before Approval)
```bash
scripts/operations/compliance/migrate_specs_to_workspace.sh --apply --repos worldenergydata
find specs/repos/worldenergydata -type f -path '*/specs/*' -print0 | sort -z | xargs -0 sha256sum > reports/compliance/wrk-188-worldenergydata-target-checksums.txt
```

## Verification
1. Source and target file counts match.
2. Checksum diff is empty after path-normalized comparison:
```bash
ROOT="$(pwd)"
diff \
  <(sed "s#  ${ROOT}/worldenergydata/##" reports/compliance/wrk-188-worldenergydata-source-checksums.txt | sort) \
  <(sed "s#  ${ROOT}/specs/repos/worldenergydata/##" reports/compliance/wrk-188-worldenergydata-target-checksums.txt | sort)
```
3. `worldenergydata/**/specs/README.md` pointer exists and includes:
- heading: `# Specs Pointer`
- centralized path beginning with ``specs/repos/worldenergydata/``
4. Governance check passes in gate mode for changed scope.
5. Claude workflow continuity check is `APPROVE` or `MINOR` and explicitly confirms no workflow-gate bypass.

Failure policy:
1. Any failed check => stop immediately.
2. If apply already ran, execute rollback.
3. Record failure + command output in WRK-188 progress notes before retry.

## Claude Workflow Continuity Check
Run before apply:
```bash
scripts/review/cross-review.sh specs/wrk/WRK-188/worldenergydata-wave1-migration.md claude --type plan
```
Pass condition:
- Claude review states the migration can proceed while preserving standard workflow:
  - WRK linkage
  - plan approval gate
  - cross-review gate
  - governance checks

## Rollback
1. Revert migration commit.
2. Re-run file count and source checksum checks on restored state:
```bash
find worldenergydata -type f -path '*/specs/*' | wc -l
find worldenergydata -type f -path '*/specs/*' -print0 | sort -z | xargs -0 sha256sum > reports/compliance/wrk-188-worldenergydata-source-checksums-rollback.txt
```
3. Record rollback reason in WRK-188 progress notes.
