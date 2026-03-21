Stage 14 · Verify Gate Evidence | task_agent | medium | single-thread
Entry: review.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run: uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-NNN
2. Fix any FAIL gates before proceeding (do not skip)
3. Re-run until all gates PASS
4. Write evidence/gate-evidence-summary.yaml (all gates: PASS)
Exit: verify-gate-evidence.py exits 0 + evidence/gate-evidence-summary.yaml
