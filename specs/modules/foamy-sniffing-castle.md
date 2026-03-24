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

**New files:**
- `.github/ISSUE_TEMPLATE/wrk-item.yml` — required fields: title, priority, category, complexity, route, machine
- `scripts/work-queue/setup-gh-project.sh` — idempotent label creation (~60 lines)
- `scripts/work-queue/gh-sync-down.sh` — GH → local sync (~120 lines, core new script)

**Files modified:**
- `scripts/work-queue/whats-next.sh`: add `--gh` flag to trigger sync before display

**ACs:** GH issue template enforces required fields. `gh-sync-down.sh` syncs metadata to local. `/work add` creates GH issue first.

## Phase D — Migration (WRK-6674)

**New files:**
- `scripts/work-queue/audit-wrk-references.sh` — categorized report of WRK-\d+ references (~40 lines)
- `scripts/work-queue/renumber-to-gh.sh` — batch rename WRK files to GH numbers (~150 lines, **highest-risk operation**)

**Files modified:**
- `scripts/work-queue/gh-next-id.sh`: stop prefixing `WRK-` in issue titles

**ACs:** No new WRK IDs minted. Renumbering completes with consistent cross-references. Dual-format support during transition.

## Phase E — Validation (WRK-6675)

**New files:**
- `scripts/work-queue/cross-review-gh-local.sh` — automated GH vs local consistency check (~60 lines)

**ACs:** Two independent cross-review passes. Zero discrepancies between GH and local.

## Scripts to Create

| Script | Phase | Est. Lines | Purpose |
|--------|-------|-----------|---------|
| `audit-pending-status.sh` | A | 25 | Find misplaced pending/ items |
| `setup-gh-project.sh` | C | 60 | Idempotent GH label creation |
| `gh-sync-down.sh` | C | 120 | GH → local sync (core script) |
| `audit-wrk-references.sh` | D | 40 | WRK-\d+ reference report |
| `renumber-to-gh.sh` | D | 150 | Batch rename to GH numbers |
| `cross-review-gh-local.sh` | E | 60 | GH vs local consistency |
| `.github/ISSUE_TEMPLATE/wrk-item.yml` | C | 80 | Issue template |

## Test Plan

| Test | Type | Phase | Expected |
|------|------|-------|----------|
| Rebuild includes done/ items | Happy | A | Index has done/ entries with status "done" |
| Closed items filtered from display | Happy | A | `whats-next` excludes `status: closed` |
| Empty done/ directory | Edge | A | No error on rebuild |
| Default shows local machine only | Happy | B | Only `computer: $(hostname)` items |
| `--all-machines` shows all | Happy | B | All machines visible |
| Machine column always visible | Happy | B | MACHINE header in all sections |
| `gh-sync-down.sh` creates local file | Happy | C | New GH issue → local WRK file |
| `gh-sync-down.sh` offline | Error | C | Graceful fallback to cached data |
| `renumber-to-gh.sh --dry-run` | Happy | D | Reports renames, zero changes |
| Cross-references updated after rename | Happy | D | `blocked_by` uses new IDs |
| Items without GH ref | Edge | D | Flagged and skipped |
| Full cross-review zero discrepancies | Happy | E | GH ↔ local match |

## Risk Mitigation

- **Renumbering (Task 19):** Mandatory `--dry-run`, git commit checkpoint before, `cross-review-gh-local.sh` after. Uses `git mv` for atomicity.
- **Parallel A/B conflicts:** Different code regions — A touches line 12/111, B touches lines 16-26 and 400+.
- **Breaking hooks/skills:** Task 18 audit catches all references. Dual-format regex `(WRK-\d+|#\d+)` during transition.

## Verification

1. After Phase A: `bash scripts/work-queue/rebuild-wrk-index.sh && bash scripts/work-queue/whats-next.sh --all` — no stale items
2. After Phase B: `bash scripts/work-queue/whats-next.sh` (filtered) vs `--all-machines` (unfiltered)
3. After Phase C: `bash scripts/work-queue/gh-sync-down.sh && bash scripts/work-queue/whats-next.sh --gh --all`
4. After Phase D: `bash scripts/work-queue/cross-review-gh-local.sh`
5. After Phase E: Two independent agent reviews confirm zero discrepancies
