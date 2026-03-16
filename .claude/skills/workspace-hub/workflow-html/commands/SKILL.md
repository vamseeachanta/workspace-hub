---
name: workflow-html-commands
description: 'Sub-skill of workflow-html: Commands.'
version: 2.3.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Commands

## Commands


```bash
# Regenerate both files
uv run --no-project python scripts/work-queue/generate-html-review.py WRK-NNN --lifecycle
uv run --no-project python scripts/work-queue/generate-html-review.py WRK-NNN --plan

# Serve locally (cross-platform)
cd .claude/work-queue/assets/WRK-NNN && python -m http.server 7782
# Then open: http://localhost:7782/WRK-NNN-lifecycle.html

# Both files auto-regenerate on every stage exit (exit_stage.py --lifecycle + --plan)
```

---
