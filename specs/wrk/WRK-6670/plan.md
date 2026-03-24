# WRK-6670: GH-First Work Queue — Single Source of Truth Migration

## Context

The work queue's local-markdown-as-source-of-truth has accumulated bugs: `rebuild-wrk-index.sh` skips `done/`, `whats-next.sh` doesn't filter `closed` status, and there's no machine filtering. This epic fixes immediate bugs, adds machine UX, then migrates to GitHub Issues as the single source of truth.

## Execution Order

```
Phase A (WRK-6671) Bug Fixes     ─┐
                                   ├──▶ Phase C (WRK-6673) GH Arch ──▶ Phase D (WRK-6674) Migration ──▶ Phase E (WRK-6675) Validation
Phase B (WRK-6672) Machine UX    ─┘
```

- **A & B run in parallel** — independent code regions
- **C depends on A+B** — GH architecture needs stable local code
- **D depends on C** — renumbering needs GH infra
- **E runs last** — validation of complete system

## Phase A — Bug Fixes (WRK-6671)

**Files modified:**
- `scripts/work-queue/rebuild-wrk-index.sh` line 12: add `"done"` to dir scan
- `scripts/work-queue/whats-next.sh` line 111: add `"closed"` to exclusion filter

**Other tasks:**
- Move WRK-1269 from `pending/` to `done/`
- Audit `pending/` for other misplaced items (script: `audit-pending-status.sh`)
- Investigate WRK-1341 title mismatch (LLM judgment)
- Rebuild index and verify clean output
- Review close/archive workflow (LLM review, no code change expected)

**ACs:** Zero stale/closed/done items in `/whats-next` ready sections. Index covers all directories.

## Phase B — Machine UX (WRK-6672)

**Files modified:**
- `scripts/work-queue/whats-next.sh`: add `--machine <name>` and `--all-machines` flags, default filter to `$(hostname -s)`, always show MACHINE column
- `scripts/work-queue/update-wrk-index.sh`: read `execution_workstations` into index
- `scripts/work-queue/dispatch-run.sh`: stamp `execution_machine: $(hostname -s)` on dispatch

**ACs:** Default view filtered to current machine. Machine column always visible. `--all-machines` shows everything.

## Phase C — GH Architecture (WRK-6673)

**Multi-repo design (Option 2 — privacy-preserving):**
- Issues live in their target repo (`digitalmodel#42`, `workspace-hub#1346`)
- Private repo issues stay private — never exposed in public repos
- Multi-repo items created in primary `target_repo`, body links to others
- Shared label scheme deployed to all participating repos
- Local cache in `workspace-hub` aggregates across all repos into unified view
- Repo list in `config/work-queue/gh-repos.yaml`

**Local file naming convention (P1-1 fix):**
- Repo-prefixed filenames: `digitalmodel-42.md`, `workspace-hub-1346.md`
- `id:` frontmatter: `digitalmodel#42`, `workspace-hub#1346`
- All scripts that glob `WRK-*.md` updated to glob `*-*.md` or use the repo-prefixed pattern
- During transition: both `WRK-NNN.md` and `repo-NNN.md` patterns supported

**Cross-repo reference format (P1-2 fix):**
- Wire format: `blocked_by: [workspace-hub#123, digitalmodel#7]`
- Regex updated from `WRK-(\d+)` to `(?:WRK-(\d+)|(\w[\w-]*)#(\d+))`
- Consumers to update before Phase D goes live:
  - `whats-next.sh` line 83 (`check_blockers`)
  - `update-wrk-index.sh` line 55 (raw string storage)
  - `session-planner.sh` line 153 (awk extraction)
  - `auto-unblock.sh` (blocker resolution)
  - `rebuild-wrk-index.sh` line 66 (blocking_count computation)

**Cross-repo GH Actions token (P1-3 fix):**
- Use a PAT with `repo` scope stored as `WRK_SYNC_TOKEN` secret in each participating repo
- `wrk-sync.yml` uses this token to push a sync commit to `workspace-hub` default branch
- Alternative (future): GitHub App with fine-grained cross-repo write permissions
- AC scoped: "auto-sync" requires PAT provisioned in all repos listed in `gh-repos.yaml`

**New files:**
- `config/work-queue/gh-repos.yaml` — list of repos to sync
- `config/work-queue/gh-sync-state.json` — per-repo `last_sync_at` timestamps (P2-3 fix)
- `.github/ISSUE_TEMPLATE/wrk-item.yml` — deployed to each target repo via `deploy-gh-templates.sh`
- `scripts/work-queue/setup-gh-labels.sh` — idempotent label creation across all repos (~80 lines)
  - AC scoped to initial creation only; label drift management is a follow-on item (P2-5)
- `scripts/work-queue/deploy-gh-templates.sh` — copies `wrk-item.yml` to each repo via `gh api PUT` (~40 lines, P2-6 fix)
- `scripts/work-queue/gh-sync-down.sh` — GH → local sync (~150 lines, core new script)
  - Iterates `for repo in $(cat gh-repos.yaml)` querying each repo
  - Delta-sync: `gh issue list --search "updated:>YYYY-MM-DD"` + per-repo `last_sync_at` from `gh-sync-state.json`
  - Pagination: `gh api --paginate` instead of `--limit 2000` to avoid silent truncation (P2-4 fix)
  - Cache TTL: 5-minute stale guard, `--force` to bypass
  - Offline fallback: per-repo — if one repo fails, log warning, continue others, print `[STALE: repo X last synced Xd ago]`
  - Local file naming: repo-prefixed (`digitalmodel-42.md`)
- `.github/workflows/wrk-sync.yml` — deployed to each repo; GH Actions on `issues: [opened, edited, closed, labeled]`
  - Uses `WRK_SYNC_TOKEN` secret to push sync commit to `workspace-hub`
- `.github/workflows/wrk-validate.yml` — validates required fields on issue creation (GH Actions validator, cross-review P1-A)

**Files modified:**
- `scripts/work-queue/whats-next.sh`: add `--gh` flag to trigger sync; add `--repo <name>` filter
- `scripts/work-queue/gh-next-id.sh`:
  - Accept `--repo owner/repo` flag (P2-1 fix)
  - Thread repo through collision avoidance
  - Update `_wrk_id_is_reserved` to be repo-aware (per-repo numbering, no cross-repo collisions)

**Design decisions (from cross-reviews):**
- **Option 2 multi-repo**: issues in target repos for privacy; local cache aggregates
- Labels-only for metadata — Projects v2 custom fields not API-creatable
- GH issue template validation NOT enforced via API — add GH Actions validator workflow per repo
- Pagination via `gh api --paginate`, not `--limit N`
- Numbering: each repo's own GH sequence (`repo#NNN`), no global counter

**ACs:** GH labels created across all repos (initial creation). Templates deployed. `gh-sync-down.sh` delta-syncs all repos with per-repo TTL and pagination. GH Actions auto-syncs per repo via PAT. `/work add` creates issue in target repo.

## Phase D — Migration (WRK-6674)

**New files:**
- `scripts/work-queue/audit-wrk-references.sh` — categorized report of WRK-\d+ references (~40 lines)
- `scripts/work-queue/renumber-to-gh.sh` — batch rename WRK files to repo-prefixed GH numbers (~180 lines, **highest-risk operation**)
  - Renames `WRK-NNN.md` → `repo-NNN.md` based on `target_repo` + `github_issue_ref`
  - Updates `id:` frontmatter to `repo#NNN`
  - Updates all cross-references (`blocked_by`, `related`, `children`, `parent`) to new format
  - Renames `assets/WRK-NNN/` → `assets/repo-NNN/`

**Files modified:**
- `scripts/work-queue/gh-next-id.sh`: stop prefixing `WRK-` in issue titles
- `scripts/work-queue/enforce-github-issue-ref.sh`: update glob from `WRK-*.md` to match new `repo-NNN.md` pattern (P2-2 fix — safety-critical hook)
- All scripts globbing `WRK-*.md`: update to new pattern (audit from `audit-wrk-references.sh`)

**ACs:** No new WRK IDs minted. Renumbering maps each item to `repo-NNN.md` with `id: repo#NNN`. Cross-references use `repo#NNN` format. All hooks updated to new glob pattern. Dual-format support during transition.

## Phase E — Validation (WRK-6675)

**New files:**
- `scripts/work-queue/cross-review-gh-local.sh` — automated GH vs local consistency check (~60 lines)
  - Queries all repos in `gh-repos.yaml` via `gh api --paginate`
  - Compares against local files using repo-prefixed naming

**ACs:** Two independent cross-review passes. Zero discrepancies between GH and local.

## Scripts to Create

| Script | Phase | Est. Lines | Purpose |
|--------|-------|-----------|---------|
| `audit-pending-status.sh` | A | 25 | Find misplaced pending/ items |
| `setup-gh-labels.sh` | C | 80 | Idempotent label creation across all repos |
| `deploy-gh-templates.sh` | C | 40 | Deploy issue template to all repos via GH API |
| `gh-sync-down.sh` | C | 150 | GH → local sync with pagination + delta-sync |
| `audit-wrk-references.sh` | D | 40 | WRK-\d+ reference report |
| `renumber-to-gh.sh` | D | 180 | Batch rename to repo-prefixed GH numbers |
| `cross-review-gh-local.sh` | E | 60 | GH vs local consistency |
| `.github/ISSUE_TEMPLATE/wrk-item.yml` | C | 80 | Issue template |
| `.github/workflows/wrk-sync.yml` | C | 50 | Auto-sync on issue state changes |
| `.github/workflows/wrk-validate.yml` | C | 40 | Validate required fields on issue creation |
| `config/work-queue/gh-repos.yaml` | C | 15 | Repo list for sync |
| `config/work-queue/gh-sync-state.json` | C | — | Per-repo sync timestamps (auto-generated) |

## Test Plan

| Test | Type | Phase | Expected |
|------|------|-------|----------|
| Rebuild includes done/ items | Happy | A | Index has done/ entries with status "done" |
| Closed items filtered from display | Happy | A | `whats-next` excludes `status: closed` |
| Empty done/ directory | Edge | A | No error on rebuild |
| Default shows local machine only | Happy | B | Only `computer: $(hostname)` items |
| `--all-machines` shows all | Happy | B | All machines visible |
| Machine column always visible | Happy | B | MACHINE header in all sections |
| `gh-sync-down.sh` creates local file | Happy | C | New GH issue → local repo-prefixed file |
| `gh-sync-down.sh` one repo offline | Error | C | Other repos sync; stale warning for failed repo |
| `gh-sync-down.sh` pagination | Edge | C | Repos with >100 issues fully synced |
| Cross-repo `blocked_by` parsed | Happy | C | `workspace-hub#123` recognized as active blocker |
| `deploy-gh-templates.sh` idempotent | Happy | C | Re-run doesn't create duplicate commits |
| `renumber-to-gh.sh --dry-run` | Happy | D | Reports renames with repo prefix, zero changes |
| Repo-prefixed filename no collision | Happy | D | `digitalmodel-42.md` and `workspace-hub-42.md` coexist |
| Cross-references updated after rename | Happy | D | `blocked_by: [workspace-hub#123]` format |
| `enforce-github-issue-ref.sh` matches new pattern | Happy | D | Hook fires on `repo-NNN.md` files |
| Items without GH ref | Edge | D | Flagged and skipped |
| Full cross-review zero discrepancies | Happy | E | GH ↔ local match across all repos |

## Risk Mitigation

- **Renumbering (Task 19):** Mandatory `--dry-run`, git commit checkpoint before, `cross-review-gh-local.sh` after. Uses `git mv` for atomicity. Rename log at `logs/wrk-renumber-YYYYMMDD.jsonl`. `--rollback` mode reads log and reverses. Pre-flight excludes burned collision GH issue numbers.
- **Parallel A/B conflicts:** Different code regions — A touches line 12/111, B touches lines 16-26 and 400+.
- **Breaking hooks/skills:** Task 18 audit catches all references. Dual-format regex during transition.
- **Cross-repo token security:** PAT with `repo` scope — minimum viable. Rotate regularly. Future: migrate to GH App with fine-grained permissions.
- **Filename collision:** Repo-prefixed naming (`digitalmodel-42.md`) eliminates by construction.

## Cross-Review Findings Tracker

| ID | Severity | Status | Resolution |
|----|----------|--------|------------|
| P1-1 | Critical | Fixed | Repo-prefixed filenames: `repo-NNN.md` |
| P1-2 | Critical | Fixed | Cross-repo `blocked_by` wire format defined; consumer update list |
| P1-3 | Critical | Fixed | PAT-based cross-repo write for GH Actions |
| P2-1 | Important | Fixed | `gh-next-id.sh` `--repo` flag + repo-aware collision avoidance |
| P2-2 | Important | Fixed | `enforce-github-issue-ref.sh` glob updated in Phase D |
| P2-3 | Important | Fixed | `gh-sync-state.json` for per-repo timestamps |
| P2-4 | Important | Fixed | `gh api --paginate` replaces `--limit 2000` |
| P2-5 | Important | Scoped | Label AC = initial creation only; drift is follow-on |
| P2-6 | Important | Fixed | `deploy-gh-templates.sh` via GH API |

## Verification

1. After Phase A: `bash scripts/work-queue/rebuild-wrk-index.sh && bash scripts/work-queue/whats-next.sh --all` — no stale items
2. After Phase B: `bash scripts/work-queue/whats-next.sh` (filtered) vs `--all-machines` (unfiltered)
3. After Phase C: `bash scripts/work-queue/gh-sync-down.sh && bash scripts/work-queue/whats-next.sh --gh --all` — verify multi-repo sync
4. After Phase D: `bash scripts/work-queue/cross-review-gh-local.sh` — verify repo-prefixed files match GH
5. After Phase E: Two independent agent reviews confirm zero discrepancies across all repos
