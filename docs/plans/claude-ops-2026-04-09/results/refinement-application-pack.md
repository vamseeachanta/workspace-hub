# Refinement Application Pack: #2055 and #2062

Generated: 2026-04-09
Source: `docs/plans/claude-followup-2026-04-09/results/issue-2055-2062-refinement-drafts.md`

---

## 1. Backup Procedure (EXECUTE FIRST)

Preserve the current issue bodies before any edits. These backups allow full rollback.

```bash
# Create backup directory
mkdir -p docs/plans/claude-ops-2026-04-09/results/backups

# Backup #2055 current body
gh issue view 2055 --json body --jq '.body' \
  > docs/plans/claude-ops-2026-04-09/results/backups/issue-2055-body-backup-2026-04-09.md

# Backup #2062 current body
gh issue view 2062 --json body --jq '.body' \
  > docs/plans/claude-ops-2026-04-09/results/backups/issue-2062-body-backup-2026-04-09.md

# Verify backups are non-empty
wc -l docs/plans/claude-ops-2026-04-09/results/backups/issue-205*.md
# Both files should be >5 lines. If either is 0 lines, STOP — do not proceed.
```

**Rollback command (if needed later):**

```bash
# Restore #2055 from backup
gh issue edit 2055 --body-file docs/plans/claude-ops-2026-04-09/results/backups/issue-2055-body-backup-2026-04-09.md

# Restore #2062 from backup
gh issue edit 2062 --body-file docs/plans/claude-ops-2026-04-09/results/backups/issue-2062-body-backup-2026-04-09.md
```

---

## 2. Apply Refined Body for #2055 (Subsea Cost Benchmarking)

### Step 2a — Write the refined body to a temp file

```bash
cat > /tmp/issue-2055-refined-body.md << 'ISSUE_EOF'
## Summary

Build cost-per-equipment-unit benchmark curves (cost/tree, cost/km-flowline, cost/manifold) by water-depth band, correlating SubseaIQ equipment counts against sanctioned project costs.

## Problem

The scaffold (#1861) provides `SubseaProject` with equipment-count fields and `load_projects()`, but zero cost functions exist. No module currently correlates equipment counts with project costs.

## Data Prerequisites (must be met before implementation)

- [ ] Equipment counts (num_trees, num_manifolds, tieback_distance_km) backfilled for >= 10 GoM fields in `data/field-development/subseaiq-scan-latest.json`
- [ ] Confirmed name-match mapping between SubseaIQ project names and CostDataPoint project names for overlapping records

## v1 Scope (band-level aggregation)

Use depth-band-level aggregation to compute cost-per-equipment ratios. This avoids per-project name-match fragility and works with sparse data.

### New functions in `digitalmodel/src/digitalmodel/field_development/benchmarks.py`:
- `cost_per_tree(projects) -> dict[str, float]` by depth band
- `cost_per_km_flowline(projects) -> dict[str, float]` by depth band
- `cost_per_manifold(projects) -> dict[str, float]` by depth band
- `unit_cost_curves(projects) -> dict` combining all three metrics
- `cost_benchmark_bands(projects) -> dict` with low/base/high by depth band and concept type

### New helper in `worldenergydata/subseaiq/analytics/cost_correlation.py`:
- `correlate_equipment_costs(subseaiq_records, cost_records)` — depth-band-level join
- `aggregate_costs_by_depth_band(merged)` — band-level cost aggregation

## Deferred to v2

- Per-project cost-per-tree correlation (requires CostDataPoint schema extension with equipment fields)
- Cross-validation of equipment-derived costs against individual sanctioned project costs
- Full 71-record equipment-count backfill

## Acceptance Criteria

- [ ] Equipment counts populated for >= 10 GoM fields
- [ ] `cost_per_tree` returns values in $10M-$200M range per depth band
- [ ] `cost_per_km_flowline` returns values in $5M-$50M range per depth band
- [ ] `cost_per_manifold` returns physically reasonable values per depth band
- [ ] `cost_benchmark_bands` returns nested dict with low/base/high structure
- [ ] All 27 existing `test_benchmarks.py` tests pass unchanged
- [ ] New cost-related tests added and passing
- [ ] `benchmarks` exported from `digitalmodel.field_development.__init__`

## Dependencies

- #1861 (scaffold) — DONE
- Equipment-count data backfill — REQUIRED before implementation

## Labels

`enhancement`, `priority:high`, `cat:engineering`, `dark-intelligence`, `agent:claude`
ISSUE_EOF
```

### Step 2b — Apply the refined body

```bash
gh issue edit 2055 --body-file /tmp/issue-2055-refined-body.md
```

### Step 2c — Post a refinement comment

```bash
gh issue comment 2055 --body "$(cat << 'EOF'
## Refinement Applied (2026-04-09)

**What changed:**
- Added explicit data prerequisites gate (equipment counts must exist before implementation)
- Scoped v1 to band-level aggregation (avoids per-project name-match fragility)
- Documented data gaps: 0/10 records have equipment counts, no cost-equipment join key
- Added deferred-to-v2 section for per-project correlation and full backfill
- Clarified acceptance criteria with specific value ranges
- Added dependency on equipment-count data backfill as a blocking prerequisite

**Source:** overnight research dossier (terminal-8) + agent team follow-up review

**Previous body:** backed up to `docs/plans/claude-ops-2026-04-09/results/backups/issue-2055-body-backup-2026-04-09.md`
EOF
)"
```

---

## 3. Apply Refined Body for #2062 (Drilling Rig Fleet Adapter)

### Step 3a — Write the refined body to a temp file

```bash
cat > /tmp/issue-2062-refined-body.md << 'ISSUE_EOF'
## Summary

Adapter to register drilling rigs from the vessel fleet CSV into the hull form validation pipeline. v1 targets drillships and semi-submersibles with LOA+BEAM data (~138 of 2,210 rigs).

## Problem

The vessel fleet adapter pattern (#1859) and hull form module (#1319) are complete, but no pipeline connects drilling rig CSV data to hull form coefficient estimation. The CSV lacks draft and displacement columns, so the adapter must estimate draft from hull-type heuristics.

## Data Limitations

- **NO DRAFT_M column** in `drilling_rigs.csv` (column does not exist)
- **DISPLACEMENT_TONNES is 100% empty** across all 2,210 rows
- **Jack-ups (1,009 rigs) have zero LOA/BEAM data** — will be skipped in v1
- **Only ~143 records have any principal dimensions** (51 drillships, 87 semi-subs)
- All computed drafts are heuristic estimates and must be flagged `draft_estimated=True`

## v1 Scope

### New constants in `ship_data.py`:
- `_RIG_TYPE_HULL_FORM_MAP`: drillship -> monohull, semi_submersible -> twin-hull, jack_up -> barge

### New functions in `hull_form.py`:
- `estimate_rig_hull_coefficients(rig_type: str) -> dict` — returns Cb, Cm, Cp, hull_form

### New functions in `ship_data.py`:
- `_estimate_draft(record, rig_type) -> Optional[float]` — L/D heuristics (drillship: LOA/15, semi-sub: BEAM*0.25, jack-up: LOA/8)
- `register_drilling_rigs(records, *, overwrite=False) -> tuple[int, int]` — normalize, estimate draft, map hull form, register

### Draft estimation strategy (Option A from dossier):
- Drillship: draft_ft = loa_ft / 15 (typical L/D ~14-16)
- Semi-submersible: draft_ft = beam_ft * 0.25 (pontoon draft relative to beam)
- Jack-up: draft_ft = loa_ft / 8 (barge hull, shallow draft)

## Deferred (v2 / follow-up issues)

- [ ] Jack-up registration (0 LOA/BEAM data; needs CSV enrichment)
- [ ] Platform rig and other types (sparse dimensions)
- [ ] Displacement-based Cb validation (no displacement data)
- [ ] DRAFT_M column addition to worldenergydata CSV
- [ ] Downstream consumer awareness for estimated drafts in stability/mooring

## Acceptance Criteria

- [ ] `estimate_rig_hull_coefficients` returns Cb/Cm/Cp with Cp = Cb/Cm identity
- [ ] Drillship Cb in [0.55, 0.70]
- [ ] Semi-sub Cb in [0.40, 0.60]
- [ ] Jack-up Cb in [0.75, 0.90]
- [ ] `register_drilling_rigs` skips records without LOA+BEAM, returns (added, skipped)
- [ ] Smoke test: ~138 rigs registered from full CSV, ~2,072 skipped
- [ ] All existing fleet adapter tests pass unchanged
- [ ] 10 new tests (5 hull form coefficients + 5 rig registration)
- [ ] New functions exported from `__init__.py`

## Dependencies

- #1859 (vessel fleet adapter pattern) — DONE
- #1319 (hull form parametric design) — DONE

## Labels

`enhancement`, `cat:engineering`, `domain:code-promotion`, `agent:claude`
ISSUE_EOF
```

### Step 3b — Apply the refined body

```bash
gh issue edit 2062 --body-file /tmp/issue-2062-refined-body.md
```

### Step 3c — Update the title to reflect realistic scope

```bash
gh issue edit 2062 --title "drilling rig fleet adapter — drillship and semi-sub hull form validation (~138 rigs with geometry)"
```

### Step 3d — Post a refinement comment

```bash
gh issue comment 2062 --body "$(cat << 'EOF'
## Refinement Applied (2026-04-09)

**What changed:**
- Title updated from "2,210 rigs" to "~138 rigs with geometry" (realistic v1 throughput)
- Added data limitations section: no DRAFT_M column, 100% empty displacement, 93.5% lack geometry
- Scoped v1 to drillships + semi-subs only (~138 registerable rigs)
- Documented draft estimation strategy (L/D heuristics) with `draft_estimated=True` flag requirement
- Deferred jack-ups (1,009 rigs), platform rigs (182), and displacement validation to v2
- Added specific Cb range acceptance criteria per hull type
- Corrected acceptance criteria to 10 new tests (5+5)

**Source:** overnight research dossier (terminal-2) + agent team follow-up review

**Previous body:** backed up to `docs/plans/claude-ops-2026-04-09/results/backups/issue-2062-body-backup-2026-04-09.md`
EOF
)"
```

---

## 4. Post-Refinement Label Recommendations

### Issue #2055 — Subsea Cost Benchmarking

| Action | Command |
|---|---|
| Add `status:needs-data` (blocks on equipment backfill) | `gh issue edit 2055 --add-label "status:needs-data"` |
| Add `scope:v1` (scoped to band-level aggregation) | `gh issue edit 2055 --add-label "scope:v1"` |
| Remove `status:plan-review` if present (refinement done) | `gh issue edit 2055 --remove-label "status:plan-review"` |
| Add `status:plan-review` (ready for owner approval) | `gh issue edit 2055 --add-label "status:plan-review"` |

### Issue #2062 — Drilling Rig Fleet Adapter

| Action | Command |
|---|---|
| Add `scope:v1` (scoped to ~138 rigs) | `gh issue edit 2062 --add-label "scope:v1"` |
| Remove `status:plan-review` if present | `gh issue edit 2062 --remove-label "status:plan-review"` |
| Add `status:plan-review` (ready for owner approval) | `gh issue edit 2062 --add-label "status:plan-review"` |

**Combined label commands:**

```bash
gh issue edit 2055 --add-label "status:needs-data,scope:v1,status:plan-review"
gh issue edit 2062 --add-label "scope:v1,status:plan-review"
```

---

## 5. Operator Checklist

```
[ ] 1. Run backup commands (Section 1) — verify both backup files are non-empty
[ ] 2. Apply #2055 refined body (Section 2, Steps 2a-2b)
[ ] 3. Post #2055 refinement comment (Step 2c)
[ ] 4. Apply #2062 refined body (Section 3, Steps 3a-3b)
[ ] 5. Update #2062 title (Step 3c)
[ ] 6. Post #2062 refinement comment (Step 3d)
[ ] 7. Apply label updates (Section 4)
[ ] 8. Verify both issues render correctly in browser
[ ] 9. Confirm backup files are committed to repo (optional but recommended)
[ ] 10. Clean up temp files: rm /tmp/issue-2055-refined-body.md /tmp/issue-2062-refined-body.md
```

---

## Safe Application Sequence

**Order matters.** Follow this exact sequence to avoid data loss:

1. **Backup first** — always capture current bodies before any `gh issue edit`
2. **Verify backups** — check file sizes; abort if any backup is 0 bytes
3. **Write temp files** — stage refined bodies to `/tmp/` before applying
4. **Edit bodies** — use `--body-file` (not `--body`) to avoid shell quoting issues with markdown
5. **Post comments** — document what changed and where the backup lives
6. **Update titles** — title edits are independent of body edits; safe to run after
7. **Apply labels** — labels are additive; safe to run last
8. **Verify in browser** — visual confirmation that markdown rendered correctly
9. **Clean up** — remove `/tmp/` staging files after confirmation

**If something goes wrong:** Run the rollback commands from Section 1 to restore original bodies. Title changes must be reverted manually via `gh issue edit NNNN --title "original title"`.

---

RECOMMENDATION: REFINE #2055 AND #2062 BEFORE APPROVAL
