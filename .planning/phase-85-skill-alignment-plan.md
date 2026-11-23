# Phase 85: Skill-Workflow Alignment Plan

> Issue: #85 (WRK-1270) | Status: research complete | Date: 2026-04-01

## 1. Current State Inventory

### 1.1 Active Skills Total: 564 SKILL.md files (excluding `_archive/`)

### 1.2 Flat Prefix Clusters Requiring Nesting

| Family | Location | Flat Count | Status |
|--------|----------|-----------|--------|
| `orcaflex-*` | `engineering/marine-offshore/` | 24 skills | **Largest — needs nesting** |
| `orcawave-*` | `engineering/marine-offshore/` | 7 skills | Needs nesting |
| `aqwa/` | `engineering/marine-offshore/aqwa/` | 5 skills (4 sub + 1 root) | **DONE — exemplar** |
| `github-*` | `development/github/` | 13 skills | Already under `github/` parent — flat within it |
| `metocean-*` | `data/energy/` | 3 skills | Minor cluster |
| `pdf-*` | `data/documents/` | 4 skills | Minor cluster |
| `openfoam*` | `engineering/cfd/` | 2 skills | Already partially nested under `cfd/` |

### 1.3 Aqwa Exemplar Structure (target pattern)

```
aqwa/
  SKILL.md          (root — overview, routing)
  batch-execution/SKILL.md
  input/SKILL.md
  output/SKILL.md
  reference/SKILL.md
```

### 1.4 SKILL.md Files Over 200-Line Limit (5 violations)

| Lines | File |
|-------|------|
| 267 | `data/research-literature/SKILL.md` |
| 227 | `gsd-research-phase/SKILL.md` |
| 204 | `gsd-debug/SKILL.md` |
| 201 | `engineering/marine-offshore/risk-assessment/SKILL.md` |
| 201 | `data/documents/knowledge-base-builder/SKILL.md` |

## 2. Recommended Nesting Order

Priority: largest families first, highest reference count, most active usage.

### Batch 1 — orcaflex (24 skills)

**From:** `engineering/marine-offshore/orcaflex-*` (24 flat dirs)
**To:** `engineering/marine-offshore/orcaflex/` with sub-dirs

Proposed sub-grouping:
```
orcaflex/
  SKILL.md                  (new root — overview, routing to sub-skills)
  modeling/                  (orcaflex-modeling, orcaflex-model-generator, orcaflex-model-sanitization, orcaflex-monolithic-to-modular)
  environment/               (orcaflex-environment-config, orcaflex-vessel-setup, orcaflex-rao-import)
  analysis/                  (orcaflex-extreme-analysis, orcaflex-modal-analysis, orcaflex-installation-analysis, orcaflex-jumper-analysis, orcaflex-mooring-iteration, orcaflex-operability)
  post-processing/           (orcaflex-post-processing, orcaflex-results-comparison, orcaflex-visualization)
  validation/                (orcaflex-code-check, orcaflex-spec-audit, orcaflex-static-debug, orcaflex-yaml-gotchas)
  specialist/                (orcaflex-specialist — general expert skill)
  batch/                     (orcaflex-batch-manager)
  conversion/                (orcaflex-file-conversion)
  line-wizard/               (orcaflex-line-wizard)
```

**Effort:** High (24 moves + root SKILL.md + reference updates)
**Estimated time:** 2-3 hours

### Batch 2 — orcawave (7 skills)

**From:** `engineering/marine-offshore/orcawave-*` (7 flat dirs)
**To:** `engineering/marine-offshore/orcawave/`

Proposed sub-grouping:
```
orcawave/
  SKILL.md                  (new root)
  analysis/                  (orcawave-analysis, orcawave-qtf-analysis, orcawave-damping-sweep)
  mesh/                      (orcawave-mesh-generation)
  multi-body/                (orcawave-multi-body)
  integration/               (orcawave-to-orcaflex, orcawave-aqwa-benchmark)
```

**Effort:** Medium (7 moves + root SKILL.md)
**Estimated time:** 1 hour

### Batch 3 — github (13 skills, lower priority)

Already under `development/github/` parent. The `github-` prefix is redundant within that directory.
**Action:** Strip `github-` prefix from subdirectory names.

```
development/github/
  SKILL.md                  (new root — if missing)
  code-review/               (was github-code-review)
  issue-tracker/             (was github-issue-tracker)
  pr-manager/                (was github-pr-manager)
  ... etc.
```

**Effort:** Medium (13 renames + reference updates)
**Estimated time:** 1 hour

### Batch 4 — Minor clusters (metocean, pdf, openfoam)

| Cluster | Action | Effort |
|---------|--------|--------|
| `metocean-*` (3) | Nest under `data/energy/metocean/` | Low — 30 min |
| `pdf-*` (4) | Nest under `data/documents/pdf/` (partially done) | Low — 30 min |
| `openfoam*` (2) | Already under `cfd/`, just consolidate | Low — 15 min |

### Batch 5 — 200-line enforcement

Split 5 oversized SKILL.md files. Typical approach: extract reference tables or examples into sub-skills.

**Effort:** Low — 1 hour total

## 3. Script Co-Location Mapping

### Scripts with direct tool-family mapping

| Script | Current Location | Target Co-Location |
|--------|-----------------|-------------------|
| `scripts/pipelines/convert_openfoam_to_orcaflex.py` | `scripts/pipelines/` | `orcaflex/conversion/scripts/` or keep in `scripts/pipelines/` (shared) |
| `scripts/pipelines/stubs/stub_orcaflex.py` | `scripts/pipelines/stubs/` | `orcaflex/scripts/` |
| `scripts/openfoam/run-openfoam-tutorials.sh` | `scripts/openfoam/` | `engineering/cfd/openfoam/scripts/` |
| `scripts/openfoam-analysis/*` | `scripts/openfoam-analysis/` | `engineering/cfd/openfoam-analysis/scripts/` |
| `scripts/solver/process-queue.py` | `scripts/solver/` | Stays — shared across solvers |
| `scripts/pipelines/gmsh_openfoam_orcaflex.*` | `scripts/pipelines/` | Stays — multi-tool pipeline |
| `scripts/operations/system/install_openfoam_v13.sh` | `scripts/operations/` | Stays — system-level |
| `scripts/operations/system/openfoam_*.md` | `scripts/operations/` | Candidate for co-location with `cfd/openfoam/` |

### Co-location rule

- **1:1 mapping** (script serves exactly one skill family) -> move to `<skill>/scripts/`
- **Multi-tool pipeline** (gmsh->openfoam->orcaflex) -> stays in `scripts/pipelines/`
- **System/ops scripts** (install, system config) -> stays in `scripts/operations/`
- **Shared utilities** -> stays in `scripts/lib/`

## 4. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Broken SKILLS_SUMMARY.md references (3215 lines) | **High** | Regenerate after each batch; it appears auto-generated |
| Broken SKILLS_GRAPH.yaml (33 lines) | Medium | Update manually — small file |
| Cross-references in other SKILL.md files | **High** | 18 files reference `orcaflex-*` paths — must grep and update |
| INDEX.md in marine-offshore | Medium | Update after batch 1 and 2 |
| ecosystem-terminology SKILL.md references | Low | Single file, easy update |
| Git history disruption | Low | Use `git mv` to preserve history |
| data/engineering/orcaflex-enrichment | Low | Orphaned in `data/` — decide: move to `orcaflex/` or leave |

## 5. Execution Checklist

For each batch:

1. `git mv` all directories (preserves history)
2. Create root `SKILL.md` for the nested family
3. Grep all `.md` and `.yaml` files for old paths -> update references
4. Regenerate `SKILLS_SUMMARY.md` and update `SKILLS_GRAPH.yaml`
5. Update `INDEX.md` in parent directory
6. Verify no broken skill loading (manual test)
7. Commit per-batch (atomic, revertible)

## 6. Estimated Total Effort

| Batch | Items | Time |
|-------|-------|------|
| 1 — orcaflex nesting | 24 skills | 2-3 hours |
| 2 — orcawave nesting | 7 skills | 1 hour |
| 3 — github prefix strip | 13 skills | 1 hour |
| 4 — minor clusters | 9 skills | 1.5 hours |
| 5 — 200-line splits | 5 files | 1 hour |
| Script co-location | ~5 scripts | 30 min |
| Reference cleanup | global | 1 hour |
| **Total** | | **8-9 hours** |

## 7. Dependencies

- No external dependencies
- Umbrella issue: #1547 (if applicable)
- Should be done during low-activity period (no parallel GSD work on marine-offshore skills)
