Stage 20 · Archive | task_agent | light | single-thread
Entry: done/WRK-NNN.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run: bash scripts/work-queue/archive-item.sh WRK-NNN
2. Verify archive/WRK-NNN.md exists
3. Regenerate INDEX.md
4. Clear active-wrk: bash scripts/work-queue/clear-active-wrk.sh
5. Update lifecycle HTML Stage 20 section (archive path)
6. Git commit lifecycle HTML final state
Exit: archive/WRK-NNN.md + updated INDEX.md + active-wrk cleared
