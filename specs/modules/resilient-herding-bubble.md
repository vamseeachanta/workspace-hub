# WRK-1170: Reclassify 101k "other" Domain Documents

## Context

The document index (1,033,933 records) has 101,471 records (9.8%) classified as `domain: "other"`. Resource intelligence reveals:
- **0 null domains** — AC1 is already met
- **40,636 records** are in SKIP_PATH_FRAGMENTS (legacy backups, personal) — intentionally excluded
- **60,835 actionable records** need reclassification into proper engineering domains

### Actionable Record Breakdown

| Bucket | Count | Content | Target Domain |
|--------|-------|---------|---------------|
| `disciplines/knowledge_skills/projects` | 26,728 | Halliburton presentations, drilling data, completions | `installation` / `energy-economics` |
| `dde/0000 O&G/2H Projects` | 17,226 | Riser design, SCR, subsea, structural analysis reports | `marine` / `pipeline` / `structural` |
| `disciplines/misc/projects` | 12,289 | GIS maps, SPM analysis, project admin | `marine` / `energy-economics` |
| `Codes & Standards/Spare` | 247 | DNV/MIL standards, SCR guidelines, OTC papers | `pipeline` / `marine` / `structural` |
| Remaining (dde, ace/docs) | 2,545 | Mixed project files, scripts | Various |

## Plan

### Step 1: Add Path Rules to phase-e2-remap.py (~56k records)

Add new PATH_RULES entries before the existing `disciplines/knowledge` catch-all:

```python
# knowledge_skills/projects — engineering project archives
("knowledge_skills/projects/halliburton",    None, "installation",    ["digitalmodel", "OGManufacturing"], "ks_halliburton"),
("knowledge_skills/projects",                None, "project-management", [],                               "ks_projects_fallback"),

# 2H Projects — offshore riser/subsea engineering
("2H Projects",                              None, "marine",          ["digitalmodel"],                    "dde_2h_projects"),

# disciplines/misc/projects — mixed project archives
("disciplines/misc/projects/gis",            None, "energy-economics",["worldenergydata"],                 "misc_gis"),
("disciplines/misc/projects",                None, "project-management", [],                               "misc_projects_fallback"),

# Spare directory refinement
("Spare/Papers/Guidelines",                  None, "pipeline",        ["digitalmodel"],                    "spare_guidelines"),
("Spare/Papers/Offshore Technology",         None, "marine",          ["digitalmodel"],                    "spare_otc"),
("Spare/Papers/Reference",                   None, "materials",       ["digitalmodel"],                    "spare_reference"),
("Spare/Papers",                             None, "pipeline",        ["digitalmodel"],                    "spare_papers"),
("Spare/MIL",                                None, "structural",      ["digitalmodel"],                    "spare_mil"),
("Spare/",                                   None, "pipeline",        ["digitalmodel"],                    "spare_fallback"),
```

### Step 2: Add Filename Rules for OTC papers and company reports

```python
(("OTC ", "OTC-"),        "marine",       ["digitalmodel"]),
(("TNE", "TNE-"),         "pipeline",     ["digitalmodel"]),
```

### Step 3: Run phase-e2-remap.py --dry-run to validate

Verify changes before live run. Target: reduce "other" from 101,471 to <52k (below 5%).

### Step 4: Run live remap + update registry

```bash
uv run --no-project python scripts/data/document-index/phase-e2-remap.py
```

This atomically rewrites index.jsonl and updates registry.yaml.

### Step 5: Accuracy Validation (AC2)

Write `scripts/data/document-index/validate-classification.py`:
- Sample 60 records (10 per major bucket) from reclassified records
- Print path + old domain + new domain for manual review
- Accept `--approve` flag to write validation evidence

### Step 6: Verify registry update (AC3) and taxonomy (AC4)

- Confirm registry.yaml domain counts updated
- No new domains needed — `project-management` already exists but underused; all others map to existing domains

### Step 7: Incremental script (AC5)

phase-e2-remap.py already serves as the incremental reclassification script — run it after any new document scan. Document this in config.yaml comments.

## Critical Files

- `scripts/data/document-index/phase-e2-remap.py` — **primary edit** (add rules)
- `scripts/data/document-index/config.yaml` — taxonomy reference (read-only)
- `data/document-index/index.jsonl` — 486MB index (modified by script)
- `data/document-index/registry.yaml` — domain counts (updated by script)
- `scripts/data/document-index/validate-classification.py` — **new file** (AC2)

## Verification

1. `--dry-run` shows expected change counts per rule
2. Live run + registry.yaml diff shows domain redistribution
3. Validation script samples 60 records for manual spot-check
4. `grep '"domain": "other"' data/document-index/index.jsonl | wc -l` confirms <5% threshold

## TDD Approach

Write tests for the new path/filename rules in `tests/data/test_phase_e2_rules.py`:
- Test each new PATH_RULE matches expected paths
- Test each new FILENAME_RULE matches expected filenames
- Test rules don't false-positive on unrelated paths
