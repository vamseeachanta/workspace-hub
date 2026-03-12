# WRK-1144 Plan — Micro-Skill → Script Extraction Audit

## Objective

Audit all 20 stage micro-skills to identify checklist items promotable from
Level 1 (prose micro-skill) to Level 2 (deterministic script) per the
enforcement gradient in `.claude/rules/patterns.md`.

## Script: audit-micro-skill-scripts.py

**Location:** `scripts/work-queue/audit-micro-skill-scripts.py`

### Classification Logic

```python
BINARY_PATTERNS   = ["exists", "matches", "passes", "generated", "present",
                      "verify", "check", "count", "confirm", "run", "validate"]
JUDGMENT_PATTERNS = ["assess", "evaluate", "decide", "draft", "summarize",
                     "investigate", "review", "explain", "document"]
KNOWN_SCRIPTS     = [f.stem for f in Path("scripts/work-queue").glob("*.py") |
                                     Path("scripts/work-queue").glob("*.sh")]

def classify(line):
    if any(s in line for s in KNOWN_SCRIPTS):     return "already-scripted"
    if any(j in line for j in JUDGMENT_PATTERNS): return "judgment"
    if any(b in line for b in BINARY_PATTERNS):   return "scriptable"
    return "judgment"  # default-safe
```

### Priority Scoring (scriptable items only)

```python
def priority_score(item):
    if item.cls != "scriptable": return 0
    score = 0
    if item.stage in [1, 5, 7, 17]: score += 3  # hard-gate stages
    if item.appears_in_n_stages >= 3: score += 2
    return score
```

### Output

YAML report at `assets/WRK-1144/micro-skill-script-candidates.yaml`:
- `summary`: total, counts by class
- `high_priority`: top-scored scriptable items
- `proposed_wrks`: top-5 child WRK proposals (YAML only — human must approve before .md creation)
- `all_items`: full classified list

## Test Plan (TDD-first)

| # | Test | Type | Expected |
|---|------|------|---------|
| 1 | classify line calling `verify-gate-evidence.py` | happy | already-scripted |
| 2 | classify "verify gate evidence exists" | happy | scriptable |
| 3 | classify "assess if plan is complete" | happy | judgment |
| 4 | classify "evaluate whether scope is appropriate" | happy | judgment (denylist) |
| 5 | priority_score for judgment item in stage 1 | edge | 0 |
| 6 | priority_score for scriptable item in stage 5 | edge | ≥ 3 |
| 7 | All 20 real stage files → YAML produced, ≥3 high-priority | integration | pass |
| 8 | Empty stage file → empty list, no crash | edge | pass |
