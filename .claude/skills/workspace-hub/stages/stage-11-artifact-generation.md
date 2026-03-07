Stage 11 · Artifact Generation | task_agent | medium | single-thread
Entry: evidence/execute.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run generate-html-review.py WRK-NNN --stage 10 --update
2. Verify Stage 10 section exists in lifecycle HTML with execution summary
3. Check required sections present (files changed, test results, code excerpts)
4. Update lifecycle HTML Stage 11 section (generation confirmed)
Exit: WRK-NNN-lifecycle.html (Stage 10+11 sections present and complete)
