Stage 19 · Close | task_agent | light | single-thread
Entry: evidence/user-review-close.yaml, evidence/gate-evidence-summary.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run: uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-NNN
2. Confirm exit 0; if non-zero fix gates first
3. Run: bash scripts/work-queue/close-item.sh WRK-NNN
4. Verify done/WRK-NNN.md exists; percent_complete: 100
5. Update lifecycle HTML Stage 19 section (close timestamp)
Exit: done/WRK-NNN.md + lifecycle HTML Stage 19 done chip
