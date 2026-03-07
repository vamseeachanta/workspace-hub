Stage 11 · Artifact Generation | task_agent | medium | single-thread
Entry: evidence/execute.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run: uv run --no-project python scripts/work-queue/generate-html-review.py WRK-NNN --lifecycle
2. Verify 20 stage sections present in WRK-NNN-lifecycle.html
3. Check required evidence files present (files changed, test results, gate summary)
4. Open lifecycle HTML in browser and confirm Stage 10/11 content visible
Exit: WRK-NNN-lifecycle.html regenerated from evidence files
