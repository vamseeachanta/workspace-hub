---
id: ADR-004
type: decision
title: "Establish three-tier data residence strategy across workspace-hub"
category: data-governance
tags: [data-governance, data-residence, worldenergydata, digitalmodel, policy]
repos: [workspace-hub, worldenergydata, digitalmodel]
confidence: 0.90
created: "2026-02-08"
last_validated: "2026-02-08"
source_type: session
related: [ADR-003]
status: active
access_count: 0
---

# Establish Three-Tier Data Residence Strategy Across Workspace-Hub

## Context

Engineering data was scattered across worldenergydata and digitalmodel with no formal governance. Vessel hull geometry in worldenergydata was incorrectly attributed as "gathered from digitalmodel" (circular). SN curves (37 curves from DNV, API, BS, AWS standards) were hardcoded as Python dictionaries in digitalmodel code. Material properties were buried in the package tree. No boundary test existed to determine where data should live.

## Decision

Establish a three-tier data residence model:

1. **Tier 1 (Collection Data)** → worldenergydata: Raw data from external public sources
2. **Tier 2 (Engineering Reference Data)** → digitalmodel: Industry standard lookup tables and engineering parameters
3. **Tier 3 (Project Data)** → project repos: Project-specific configurations and deliverables

Key implementation decisions:

- Canonical policy at `docs/DATA_RESIDENCE_POLICY.md`
- Boundary test: "Where did this data originate?" determines tier
- Handoff contract: digitalmodel declares dependencies via `config/data_sources.yaml`, read-only path-based access
- SN curves externalized from Python code to `data/fatigue/sn_curves.yaml`
- Steel grades relocated to `data/materials/steel_grades.yaml`
- worldenergydata established as authoritative source for hull geometry collection

## Results

- Policy document: `docs/DATA_RESIDENCE_POLICY.md`
- SN curves externalized: 37 curves from 4 standards in YAML
- Steel grades canonical location: `digitalmodel/data/materials/steel_grades.yaml`
- External data contract: `digitalmodel/config/data_sources.yaml`
- INVENTORY.md provenance corrected
- CLAUDE.md references added in both repos

## Rationale

- Three-tier model provides clear ownership boundaries based on data origin
- Externalizing engineering data from code improves maintainability and auditability
- Read-only handoff contract prevents circular dependencies
- Keeping hardcoded dicts as fallback ensures backward compatibility during transition
- Policy applies boundary test consistently: public source → Tier 1, engineering standard → Tier 2, project → Tier 3

## Consequences

- All new data must pass the boundary test before being added to a repository
- digitalmodel gains a `data/` directory at repo root for Tier 2 reference data
- worldenergydata must not reference digitalmodel as a data source
- Future data additions must update `config/data_sources.yaml` if cross-repo
- Steel material has dual locations during transition (canonical + legacy for backward compat)

## References

- Policy: `docs/DATA_RESIDENCE_POLICY.md`
- Spec: `specs/modules/enumerated-conjuring-cake.md`
- Related: digitalmodel `docs/modules/data/DATA_REORGANIZATION_PLAN.md`
- Work item: WRK-097
