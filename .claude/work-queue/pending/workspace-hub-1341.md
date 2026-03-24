---
id: workspace-hub#1341
title: "slim down large repos — relocate PDFs, reduce .git bloat"
status: pending
priority: high
complexity: complex
created_at: 2026-03-24T09:14:36Z
parent:
target_repos:
  - client_projects
  - energy
  - rock-oil-field
  - saipem
  - OGManufacturing
  - seanation
  - aceengineer-admin
  - doris
  - frontierdeepwater
  - aceengineer-website
  - workspace-hub
  - digitalmodel
  - ai-native-traditional-eng
commit:
spec_ref:
related: []
blocked_by: []
synced_to: []
plan_reviewed: false
plan_approved: false
percent_complete: 0
computer: ace-linux-2
execution_workstations: [ace-linux-1]
plan_workstations: [dev-primary]
provider: claude
provider_alt:
stage_evidence_ref: .claude/work-queue/assets/WRK-1341/evidence/stage-evidence.yaml
subcategory: operations
category: infrastructure
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1341
---
# Slim Down Large Repos — Relocate PDFs, Reduce .git Bloat

## Mission
Large repos are causing slow sync times. Three-pronged approach:
1. Remove PDFs from repos and relocate to mounted document-intelligence volume (related WRK exists)
2. Investigate saving large .git folders to a separate branch or using shallow clones (emergency measure)
3. Make all existing repos lean going forward — enforce size limits, add .gitattributes LFS rules or exclusions

## Context
- Sync times are unacceptably long on some machines
- PDFs should live in document-intelligence mount, not in git
- .git folder bloat is the primary culprit for slow clones/fetches

## Acceptance Criteria
- [ ] Audit all repos for large files (PDFs, binaries) with size report
- [ ] Remove PDFs from git history (git filter-repo or BFG) and relocate to document-intelligence mount
- [ ] Evaluate orphan-branch approach for preserving .git history without bloating clones
- [ ] Implement shallow clone or partial clone strategy for daily use
- [ ] Add .gitattributes / pre-commit hooks to prevent large binary re-introduction
- [ ] Verify sync times improve on all machines
- [ ] Document the new policy for binary/PDF files

## Research Notes (2026-03-24)

### Repo Size Inventory (from Tier 2 Index, 2026-01-13 assessment)

| Repo | Size | Priority |
|------|------|----------|
| client_projects | 13 GB | P1 — largest, mixed Tier 3 |
| energy | 5.4 GB | P1 |
| rock-oil-field | 5.2 GB | P1 |
| saipem | 4.1 GB | P1 |
| OGManufacturing | 2.4 GB | P2 — meta-repo with submodule refs |
| seanation | 1.5 GB | P2 |
| aceengineer-admin | 821 MB | P3 |
| doris | 521 MB | P3 |
| frontierdeepwater | 490 MB | P3 |
| aceengineer-website | 281 MB | P3 |
| ai-native-traditional-eng | 12 MB | skip — already lean |

Top 4 repos account for ~28 GB. Total across all Tier 2: ~33 GB.

### Likely Bloat Sources
- Committed PDFs, Excel files, data files (not LFS-tracked)
- .git/objects pack bloat from large binary history
- OGManufacturing has submodule references to multiple other repos — needs special handling

### Relocation Target
- **`/mnt/ace-data`** = **`/mnt/ace`** = local `/dev/sda1` on ace-linux-1 (7.5TB NFS-shared to ace-linux-2)
- Work to be done on ace-linux-1 (direct local access to target volume)
- Existing literature store: `/mnt/ace-data/digitalmodel/docs/domains/<domain>/literature/`

### INVESTIGATE: Document Location Consolidation
Too many document/data locations exist across the ecosystem. Before relocating, audit and consolidate:

**Known locations (need full inventory on ace-linux-1):**
- `/mnt/ace/docs/` — legacy docs, integrity files
- `/mnt/ace/O&G-Standards/` — standards PDFs
- `/mnt/ace/Production/` — production history
- `/mnt/ace/data/` — unknown scope
- `/mnt/ace/digitalmodel/docs/domains/` — literature store (document-intelligence)
- `/mnt/ace/OGManufacturing/` — unclear if repo mirror or data
- Various repo-internal `docs/`, `data/`, `specs/` dirs with committed PDFs/binaries

**Questions to resolve:**
1. What is the canonical directory structure under `/mnt/ace-data/` for relocated docs?
2. Should it mirror repo names (`/mnt/ace-data/<repo>/docs/`) or be domain-organized?
3. Which existing `/mnt/ace/` directories already serve as doc stores vs. are legacy dumps?
4. Are any repos symlinking into `/mnt/ace/` already? If so, which pattern do they follow?
5. How does this relate to the document-intelligence index (`assets.json` manifest from ORGANIZATION_PLAN.md)?
6. Do we consolidate first then slim repos, or slim repos first and sort later?

### Related Work
- WRK-1341 AC #2 covers git-filter-repo / BFG for history rewriting
- worldenergydata WRK-196 flagged large legacy files in `common/legacy/`

### Strategy Sequence
1. **Audit first** — `git rev-list --objects --all | git cat-file --batch-check` per repo to identify large objects
2. **Relocate PDFs/binaries** to `/mnt/ace-data/<repo>/`, update any code paths that reference them
3. **Rewrite history** with git-filter-repo (preferred over BFG — actively maintained)
4. **Orphan branch** — push current history to `archive/pre-slim` branch before force-pushing cleaned main
5. **Shallow clone config** — set `clone.defaultRemoteTimeout` and recommend `--depth 1` for CI/daily use
6. **Guard rails** — .gitattributes LFS rules + pre-commit hook rejecting files >5 MB
7. **Backup** — full backup of `/mnt/ace-data/` after consolidation + slimmed repos pushed to GitHub
