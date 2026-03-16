---
name: skill-learner-files-changed-12
description: 'Sub-skill of skill-learner: Files Changed (12) (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Files Changed (12) (+3)

## Files Changed (12)


- src/modules/npv/calculator.py (new)
- src/modules/npv/visualizer.py (new)
- src/modules/npv/__init__.py (new)
- tests/unit/test_npv_calculator.py (new)
- config/input/npv_analysis.yaml (new)
- scripts/run_npv_analysis.sh (new)
- docs/npv_calculator.md (new)
- ... 5 more files

## Code Additions


- Lines added: 847
- Lines removed: 23
- Net change: +824

## Technologies Used


- Plotly for interactive visualization
- Pandas for data handling
- NumPy for NPV calculations
- pytest for testing
```

## 2. Pattern Extraction


**Identifies Reusable Patterns:**

**Pattern Types:**
```markdown
1. **Workflow Patterns**
   - YAML config → Script execution → HTML report
   - Data load → Process → Validate → Visualize → Save

2. **Code Patterns**
   - Interactive plotting with Plotly

*See sub-skills for full details.*
